from django import forms
from .fields import MultiEmailField

email_attrs = {
    'class': 'required',
    'max_length': 100,
}

class InvitationForm(forms.Form):
    """
    Form for sending invitations
    """
    from_email = forms.EmailField(widget=forms.TextInput(attrs=email_attrs))
    to_email = MultiEmailField(widget=forms.TextInput(attrs=email_attrs))

    personal_note = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )

