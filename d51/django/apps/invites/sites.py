from django.conf.urls.defaults import patterns, url
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from .models import Invitation
from .utils import INVITE_SESSION_KEY, InviteBackendException
from d51.django.auth.decorators import auth_required

class InviteBackendSite(object):
    def __init__(self, app_name='invites', model_name='invites', model_class=Invitation, login_url_name='home'):
        self._invitation_registration = {}
        self.app_name, self.model_name = app_name, model_name
        self.model_class = model_class
        self.login_url_name = login_url_name

    def get_urls(self):
        urlpatterns = patterns('',
            url('^$', auth_required()(self.root_view), name='invite-root'),
            url('^thanks/$', auth_required()(self.thanks_view), name='invite-thanks'),
            url('^from/(?P<username>[\w\d\-_]+)/(?P<invite_pk>\d+)/$', self.accept_invite_view, name='invite-accept'),
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
        return render_to_response('invites/index.html', { 'registration_backends':self._invitation_registration }, context_instance=RequestContext(request)) 

    def thanks_view(self, request):
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
        invite = get_object_or_404(self.model_class, pk=int(invite_pk))
        backend = invite.get_backend()
        return backend.accept_invite_view(request, invite)
        if request.user.is_authenticated():
            response = backend.accept_invite(request, invite)
        else:
            
            request.session[INVITE_SESSION_KEY] = invite_pk
            response = render_to_response([
                    'invites/%s/accept.html'%backend.backend_name,
                    'invites/accept.html',
            ],{
                                'invitation':invite,
            }, context_instance=RequestContext(request))
        return response

    def load_backend_for(self, invitation):
        try:
            return self._invitation_registration[invitation.backend]
        except KeyError:
            raise InviteBackendException()

invite_site = InviteBackendSite()
