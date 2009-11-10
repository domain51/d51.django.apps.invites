from django import forms
from django.forms.fields import EmailField

def check(email):
    field = EmailField()
    return field.clean(email.strip())

class MultiEmailField(forms.Field):
    def clean(self, value):
        return [check(email) for email in value.split(',')]

