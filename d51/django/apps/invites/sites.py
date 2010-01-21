from django.utils.importlib import import_module
from django.conf.urls.defaults import patterns, url
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from .models import Invitation
from .utils import INVITE_SESSION_KEY, InviteBackendException
from d51.django.auth.decorators import auth_required

class InviteBackendSite(object):
    def __init__(self, home_view_name, app_name='invites', model_name='invites', model_class=Invitation):
        self._invitation_registration = {}
        self.app_name, self.model_name = app_name, model_name
        self.model_class = model_class
        self.home_view_name = home_view_name

    def get_urls(self):
        urlpatterns = patterns('',
            url('^$', auth_required()(self.root_view), name='invite-root'),
            url('^thanks/$', auth_required()(self.thanks_view), name='invite-thanks'),
            url('^from/(?P<username>[\w\d\-_]+)/(?P<invite_pk>\d+)/$', self.accept_invite_view, name='invite-accept'),
            url('^confirm/$', self.confirm_invite_view, name='invite-confirm'),
        )
        for backend in self._invitation_registration.values():
            urlpatterns += backend.get_urls()
        return urlpatterns 

    def urls(self):
        return self.get_urls(), self.app_name, self.model_name
    urls = property(urls)

    def register_backend(self, name, backend_class):
        self._invitation_registration[name] = backend_class(name, self)
    
    def root_view(self, request):
        """
            a basic list of all available invitation backends
        """
        return render_to_response('invites/index.html', { 'registration_backends':self._invitation_registration }, context_instance=RequestContext(request)) 

    def thanks_view(self, request):
        """
            this view is presented to the inviter after 
            sending his or her invitations
        """
        invite_pk = request.session.get(INVITE_SESSION_KEY, None)
        template_list = [ 
                'invites/thanks.html',
        ]
        if invite_pk is not None:
            invitation = self.model_class.objects.get(pk=int(pk))
            backend = invitation.get_backend()
            template_list.insert(0, 'invites/%s/thanks.html' % backend.backend_name)

        return render_to_response(template_list, {}, context_instance=RequestContext(request))

    def accept_invite_view(self, request, username, invite_pk):
        """
            user hits this page from an invitation link, should be redirected
            to the appropriate registration method
        """
        invite = get_object_or_404(self.model_class, pk=int(invite_pk))
        backend = invite.get_backend()
        return backend.accept_invite_view(request, invite)

    def confirm_invite_view(self, request):
        """
            after registering, a user should pass through this
            view to actually generate a confirmed InvitationFulfillment
        """
        invite_pk = request.session.get(INVITE_SESSION_KEY, None)
        invite = get_object_or_404(self.model_class, pk=int(invite_pk))
        backend = invite.get_backend()
        return backend.confirm_invite_view(request, invite)

    def load_backend_for(self, invitation):
        try:
            return self._invitation_registration[invitation.backend]
        except KeyError:
            raise InviteBackendException()

def generate_invite_site(with_backends=[], *args, **kwargs):
    invite_site = InviteBackendSite(*args, **kwargs) 
    for name, backend_string in with_backends.iteritems():
        get_module_and_target = lambda x: x.rsplit('.', 1)
        module, target = get_module_and_target(backend_string)
        module = import_module(module)
        target = getattr(module, target)
        invite_site.register_backend(name, target)
    return invite_site

invite_site = None

def set_invite_site(site):
    global invite_site
    invite_site = site
