from django.forms.util import ValidationError
from django.test import TestCase
from ..fields import MultiEmailField

class MultiEmailFieldTest(TestCase):
    def test_allows_multiple_emails(self):
        field = MultiEmailField()
        expected = ["bob@example.com", "alice@example.com",]
        actual = field.clean(", ".join(expected))
        self.assert_(expected[0] in actual)
        self.assert_(expected[1] in actual)

    def test_throws_validation_error_if_bad_email_provided(self):
        bad_data = "bob@example.com, alice@bad"
        field = MultiEmailField()
        self.assertRaises(ValidationError, field.clean, bad_data)

