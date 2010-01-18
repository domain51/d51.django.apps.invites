from django import forms

class InvitationConfirmationForm(forms.Form):
    confirm_invite = forms.BooleanField()

class InvitationForm(forms.Form):
    pass
