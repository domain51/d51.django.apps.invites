from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from d51.django.apps.invites.views import index, thanks

class IndexViewTests(TestCase):
    def test_renders_invites_index_html_on_GET(self):
        c = Client()
        response = c.get(reverse("invites_index"))
        self.assertEqual(200, response.status_code)

    def test_redirects_to_thanks_on_successful_POST(self):
        c = Client()
        response = c.post(reverse("invites_index"), {
            "from_email": "travis@example.com",
            "to_email": "bob@example.com"
        })
        self.assertEqual(302, response.status_code)
        redirect = response._headers['location']
        self.assertEqual(
            reverse("invites_thanks")+"?num=1",
            redirect[1][-len(reverse("invites_thanks")+"?num=1"):]
        )

