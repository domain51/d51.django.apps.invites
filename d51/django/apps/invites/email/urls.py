from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('d51.django.apps.invites.email.views',
    url(r'^$', 'index', name='email:invite'),
)
