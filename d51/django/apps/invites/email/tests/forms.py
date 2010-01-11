from django.test import TestCase
from ..forms import EmailInvitationForm

class EmailInvitationFormTests(TestCase):
    def test_allows_multiple_emails_in_to_field(self):
        form = EmailInvitationForm({
            "from_email": "travis@example.com",
            "to_email": "bob@example.com, alice@example.com",
        })

        self.assert_(form.is_valid())

