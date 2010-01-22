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
        # invitee's
        urlpatterns = patterns('',
            url('^%s/from/(?P<username>[\w\d\-_]+)/(?P<invite_pk>\d+)/$' % self.backend_name, 
                self.accept_view,
                name='invite-%s-accept'%self.backend_name),
            url('^%s/fulfill/$' % self.backend_name,
                self.fulfill_view,
                name='invite-%s-fulfill'%self.backend_name),
        )

        # inviter's
        urlpatterns += patterns('',
            url(r'^%s/processed/$' % self.backend_name,
                auth_required()(self.processed_view),
                name='invite-%s-processed' % self.backend_name),
            url(r'^%s/$'%self.backend_name,
                auth_required()(self.create_view),
                name='invite-%s-create' % self.backend_name),
        )
        return urlpatterns

    def get_url_namespace(self):
        return self._site.app_name
 
    def get_absolute_url(self):
        return reverse(self.get_url_namespace() + ':invite-%s-create'%self.backend_name)

    def create_invitations_from_form(self, user, form):
        return self.model_class.objects.create_for(self.backend_name, user, with_form=form)

    def send_invites(self, invitations, form):
        return invitations 

    def get_registration_url(self):
        return reverse('registration_register')

    def model_class(self):
        return self._site.model_class
    model_class = property(model_class)

    def home_view_name(self):
        return self._site.home_view_name
    home_view_name = property(home_view_name)

    def create_view(self, request):
        form_class = self.get_form_class()
        if form_class:
            form = form_class(request.POST) if request.method == 'POST' else form_class()
        else:
            form = False
        context = { 'form': form }
        if self.can_handle_create_for(request, with_form=form):
            response = self.handle_create_for(request, with_form=form, and_context=context)
            if response:
                return response

        return render_to_response([
            'invites/%s/create.html' % self.backend_name,
            'invites/create.html',
            ], context, context_instance=RequestContext(request))

    def can_handle_create_for(request, with_form=None):
        form = with_form
        return form and form.is_valid() and request.method == 'POST'

    def handle_create_for(request, with_form, and_context):
        form, context = with_form, and_context
        invitations = self.create_invitations_from_form(request.user, form)
        try:
            invitations = self.send_invites(invitations, form, request)
            request.session[SENT_INVITATIONS] = invitations
            return HttpResponseRedirect(reverse('invites:invite-%s-processed' % self.backend_name))
        except InviteBackendException as e:
            context['error'] = e

    def processed_view(self, request):
        invitations = request.session[SENT_INVITATIONS]
        return render_to_response([
            'invites/%s/processed.html'%self.backend_name,
            'invites/processed.html',
            ], {
                'invitations':invitations,
            }, context_instance=RequestContext(request))

    def accept_view(self, request, username, invite_pk):
        """
            user hits this page from an invitation link, should be redirected
            to the appropriate registration method
        """
        invitation = get_object_or_404(self.model_class, pk=int(invite_pk))
        response = HttpResponseRedirect(reverse(self.home_view_name))
        if not request.user.is_authenticated():
            request.session[INVITE_SESSION_KEY] = invitation.pk
            response = HttpResponseRedirect(self.get_registration_url())
        return response

    def fulfill_view(self, request):
        """
            after registering, a user should pass through this
            view to actually generate a confirmed InvitationFulfillment
        """
        if request.user.is_authenticated():
            self.fulfill_current_invitation(request)
        response = HttpResponseRedirect(request.GET.get('next', reverse(self.home_view_name)))
        return response 

    def fulfill_current_invitation(self, request):
        invite_pk = request.session.get(INVITE_SESSION_KEY, None)
        get_object_or_404(self.model_class, pk=int(invite_pk)).fulfill(request.user)
        request.session[INVITE_SESSION_KEY] = None

