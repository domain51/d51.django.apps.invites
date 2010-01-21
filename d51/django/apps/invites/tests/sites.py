from django.test import TestCase
from ..sites import InviteBackendSite, patterns, url

class TestOfInviteBackendSite(TestCase):
    def test_get_urls(self):
        site = InviteBackendSite('home', app_name='invites', model_name='invites')
        class MockBackend(object):
            def __init__(_self, name, _site):
                _self.name = name
                self.assertEqual(site, _site)
            def get_urls(self):
                return patterns('',
                        url('^'+self.name+'$', self.get_urls, name=self.name)
                )
        mock_backends = {
            'gary':MockBackend,
            'busey':MockBackend,
            'rocks':MockBackend,
        }
        for name, backend in mock_backends.iteritems():
            site.register_backend(name, backend)

        urlpatterns = site.get_urls()
        patterns_has = lambda x: len([p for p in urlpatterns if p.name==x]) > 0
        for name, backend in mock_backends.iteritems():
            self.assertTrue(patterns_has(name))
