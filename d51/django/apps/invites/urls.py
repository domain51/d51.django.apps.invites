from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('d51.django.apps.invites.views',
    url(r'^$', 'index', name='invites_index'),
    url(r'^thanks/$', 'thanks', name='invites_thanks'),
)

