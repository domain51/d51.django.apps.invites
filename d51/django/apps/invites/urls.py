from django.conf.urls.defaults import patterns, url, include
from .backends import invite_site 
urlpatterns = patterns('d51.django.apps.invites',
    ('^', include(invite_site.urls)),
)

