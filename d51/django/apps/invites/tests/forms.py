from django.test import TestCase
from d51.django.apps.invites.forms import InvitationForm

class InvitationFormTests(TestCase):
    def test_allows_multiple_emails_in_to_field(self):
        form = InvitationForm({
            "from_email": "travis@example.com",
            "to_email": "bob@example.com, alice@example.com",
        })

        self.assert_(form.is_valid())

