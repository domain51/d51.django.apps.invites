from ..utils import INVITE_SESSION_KEY, SENT_INVITATIONS, InviteBackendException
from django.conf.urls.defaults import patterns, url
from django.utils.importlib import import_module
from django.conf.urls.defaults import patterns, url
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from d51.django.auth.decorators import auth_required

class InviteBackend(object):
    def __init__(self, backend_name, site):
        self._site = site
        self.backend_name = backend_name

    def get_form_class(self):
        return None
    
    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^%s/confirm/$' % self.backend_name,
                auth_required()(self.confirmation_view),
                name='invite-%s-confirm' % self.backend_name),
            url(r'^%s/$'%self.backend_name,
                auth_required()(self.invite_view),
                name='invite-%s' % self.backend_name),
        )
        return urlpatterns

    def get_url_namespace(self):
        return self._site.app_name
 
    def get_absolute_url(self):
        return reverse(self.get_url_namespace() + ':invite-%s'%self.backend_name)

    def create_invitations_from_form(self, user, form):
        return self.model_class.objects.create_for(self.backend_name, user, with_form=form)

    def send_invites(self, invitations, form):
        return invitations 

    def message_user(self, user, message):
        pass

    def get_registration_url(self):
        return reverse('registration_register')

    def model_class(self):
        return self._site.model_class
    model_class = property(model_class)

    def home_view_name(self):
        return self._site.home_view_name
    home_view_name = property(home_view_name)

    def revoke_invitations(self, invitations):
        [invitation.delete() for invitation in invitations]

    def confirmation_view(self, request):
        invitations = request.session[SENT_INVITATIONS]
        return render_to_response([
            'invites/%s/confirmation.html'%self.backend_name,
            'invites/confirmation.html',
            ], {
                'invitations':invitations,
            }, context_instance=RequestContext(request))

    def accept_invite_view(self, request, invitation):
        response = HttpResponseRedirect(reverse(self.home_view_name))
        if not request.user.is_authenticated():
            request.session[INVITE_SESSION_KEY] = invitation.pk
            response = HttpResponseRedirect(self.get_registration_url())
        return response

    def confirm_invite_view(self, request, invitation):
        response = HttpResponseRedirect(request.GET.get('next', reverse(self.home_view_name)))
        if request.user.is_authenticated():
            self.model_class.objects.confirm(invitation, request.user)
            request.session[INVITE_SESSION_KEY] = None
        return response            

    def invite_view(self, request):
        form_class = self.get_form_class()
        if form_class:
            form = form_class(request.POST) if request.method == 'POST' else form_class()
        else:
            form = False
        context = { 'form': form }
        if form and form.is_valid() and request.method == 'POST':
            invitations = self.create_invitations_from_form(request.user, form)
            try:
                invitations = self.send_invites(invitations, form, request)
                request.session[SENT_INVITATIONS] = invitations
                return HttpResponseRedirect(reverse('invites:invite-%s-confirm' % self.backend_name))
            except InviteBackendException as e:
                context['error'] = e
        return render_to_response([
            'invites/%s/invite_form.html' % self.backend_name,
            'invites/invite_form.html',
            ], context, context_instance=RequestContext(request))
