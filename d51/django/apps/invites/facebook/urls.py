from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('d51.django.apps.invites.facebook.views',
    url(r'^$', 'index', name='facebook:invite'),
)
