from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url, include
from django.shortcuts import render_to_response, get_object_or_404
from .forms import InvitationConfirmationForm
from .models import Invitation

INVITE_SESSION_KEY = 'd51.django.apps.invites.INVITE_SESSION_KEY'
UNSENT_INVITATIONS = 'unsent_invitations'

class InviteBackendException(Exception):
    pass

class InviteBackendSite(object):
    def __init__(self):
        self._invitation_registration = {}

    def get_urls(self):
        urlpatterns = patterns('',
            url('^$', self.root_view, name='invite-root'),
            url('^thanks/$', self.thanks_view, name='invite-thanks'),
            url('^from/(?P<username>[\w\d\-_]+)/(?P<invite_pk>\d+)/$', self.accept_invite_view, name='invite-accept'),
        )
        for backend in self._invitation_registration.values():
            urlpatterns += backend.get_urls()
        return urlpatterns, 'invites', 'invites'
    urls = property(get_urls)

    def register_backend(self, name, backend_class):
        self._invitation_registration[name] = backend_class()
    
    def root_view(self, request):
        return render_to_response('invites/index.html', { 'registration_backends':self._invitation_registration }, context_instance=RequestContext(request)) 

    def thanks_view(self, request):
        invite_pk = request.session.get(INVITE_SESSION_KEY, None)
        template_list = [ 
                'invites/thanks.html',
        ]
        if invite_pk is not None:
            invitation = Invitation.objects.get(pk=int(pk))
            backend = invitation.get_backend()
            template_list.insert(0, 'invites/%s/thanks.html' % backend.backend_name)

        return render_to_response([
            'invites/thanks.html',
            'thanks.html',
        ], {}, context_instance=RequestContext(request))

    def accept_invite_view(self, request, username, invite_pk):
        invite = get_object_or_404(Invitation, pk=int(invite_pk), status=Invitation.STATUS_CHOICES[1][0]) 
        backend = invite.get_backend()
        response = backend.accept_invite(request, invite)
        return response

    def load_backend_for(self, invitation):
        try:
            return self._invitation_registration[invitation.backend]
        except KeyError:
            raise InviteBackendException()

invite_site = InviteBackendSite()

class InviteBackendMetaclass(type):
    def __init__(cls, name, bases, attrs):
        if not attrs.get('is_abstract', False):
            backend_name = attrs.get('backend_name', name.lower)
            attrs['backend_name'] = backend_name
            invite_site.register_backend(backend_name, cls)

class InviteBackend(object):
    revokation_notification = 'sorry for the trouble'
    confirmation_notification = 'thanks for sending an invite'
    is_abstract = True
    __metaclass__ = InviteBackendMetaclass

    def accept_invite(self, request, invitation):
        invitation.resulting_user = request.user
        invitation.status = Invitation.STATUS_CHOICES[2][0]
        invitation.save()
        return HttpResponseRedirect(request.GET.get('next', '/'))

    def get_urls(self):
        urlpatterns = patterns('',
            url('^%s/confirm/$'%self.backend_name, self.confirmation_view, name='invite-%s-confirm'%self.backend_name),
            url('^%s/$'%self.backend_name, self.invite_view, name='invite-%s'%self.backend_name),
        )
        return urlpatterns

    def process_target_from_form(self, form):
        return None

    def create_invitations_from_form(self, user, form):
        return [Invitation.objects.create(
            sent_by=user,
            backend=self.backend_name,
            target=self.process_target_from_form(form),
            status=Invitation.STATUS_CHOICES[0][0],
        ),]

    def send_invite(self, invitation):
        pass

    def message_user(self, user, message):
        pass

    def get_absolute_url(self):
        return reverse('invites:invite-%s'%self.backend_name)

    def revoke_invitations(self, invitations):
        [invitation.delete() for invitation in invitations]

    def confirmation_view(self, request):
        invitation_pks = request.session.get(UNSENT_INVITATIONS, None)
        invitations = Invitation.objects.filter(pk__in=invitation_pks)
        form = InvitationConfirmationForm(request.POST) if request.method == 'POST' else InvitationConfirmationForm()
        if form.is_valid() and request.method == 'POST':
            form_confirmation = form.cleaned_data['confirm_invite'] is True
            message = None
            if form_confirmation:
                message = self.confirmation_notification
                self.send_invites(invitations)
                for invitation in invitations:
                    invitation.status = Invitation.STATUS_CHOICES[1][0]
                    invitation.save()
            else:
                message = self.revokation_notification
                self.revoke_invitations(invitations)
            self.message_user(request.user, message)
            request.session[UNSENT_INVITATIONS] = None
            return HttpResponseRedirect(reverse('invites:invite-root'))
        return render_to_response([
            'invites/%s/confirmation_form.html'%self.backend_name,
            'invites/confirmation_form.html',
            ], {
                'invitations':invitations,
                'form':form,
            }, context_instance=RequestContext(request))

    def get_form_class(self):
        return None

    def invite_view(self, request):
        form_class = self.get_form_class()
        form = form_class(request.POST) if request.method == 'POST' else form_class()
        if form.is_valid() and request.method == 'POST':
            invitations = self.create_invitations_from_form(request.user, form)
            [invitation.save() for invitation in invitations]
            request.session[UNSENT_INVITATIONS] = [inv.pk for inv in invitations]
            return HttpResponseRedirect(reverse('invites:invite-%s-confirm'%self.backend_name))
        return render_to_response([
            'invites/%s/invite_form.html' % self.backend_name,
            'invites/invite_form.html',
            ], {
                'form':form,
            }, context_instance=RequestContext(request))

class ConsoleInvitationBackend(InviteBackend):
    backend_name = 'console'

    def get_form_class(self):
        from django import forms 
        class form_class(forms.Form):
            things = forms.IntegerField(required=True)
        return form_class

    def send_invites(self, invitations):
        print [invitation.get_absolute_url() for invitation in invitations]

    def create_invitations_from_form(self, user, form):
        return [Invitation.objects.create(
            sent_by=user,
            backend=self.backend_name,
            target="invite %d of %d invites" % (i, form.cleaned_data['things']),
            status=Invitation.STATUS_CHOICES[0][0],
        ) for i in range(0, form.cleaned_data['things'])]
