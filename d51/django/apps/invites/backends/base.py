from d51.django.auth.decorators import auth_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.shortcuts import render_to_response, get_object_or_404
from ..models import Invitation
from ..sites import invite_site
from ..utils import INVITE_SESSION_KEY, SENT_INVITATIONS, InviteBackendException

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

    def model_class(self):
        return self._site.model_class
    model_class = property(model_class)

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
        if request.user.is_authenticated():
            self.model_class.objects.accept_invite(invitation, request.user)
            return HttpResponseRedirect(request.GET.get('next', '/'))
        else:
            raise Exception('not yet implemented')

    def invite_view(self, request):
        form_class = self.get_form_class()
        form = form_class(request.POST) if request.method == 'POST' else form_class()
        context = { 'form': form }
        if form.is_valid() and request.method == 'POST':
            invitations = self.create_invitations_from_form(request.user, form)
            try:
                invitations = self.send_invites(invitations, form)
                request.session[SENT_INVITATIONS] = invitations
                return HttpResponseRedirect(reverse('invites:invite-%s-confirm'%self.backend_name))
            except InviteBackendException as e:
                context['error'] = e
        return render_to_response([
            'invites/%s/invite_form.html' % self.backend_name,
            'invites/invite_form.html',
            ], context, context_instance=RequestContext(request))
