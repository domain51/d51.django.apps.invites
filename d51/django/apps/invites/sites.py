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
        urlpatterns = patterns('')
        for backend in self._invitation_registration.values():
            urlpatterns += backend.get_urls()
        return urlpatterns 

    def urls(self):
        return self.get_urls(), self.app_name, self.model_name
    urls = property(urls)

    def register_backend(self, name, backend_class):
        self._invitation_registration[name] = backend_class(name, self)
    
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
