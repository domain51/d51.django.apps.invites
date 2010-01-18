from django import forms
from django.forms.fields import EmailField
from .base import InviteBackend
from ..sites import invite_site
from django.core.mail import send_mail
class ConsoleInviteBackend(InviteBackend):
    def get_form_class(self):
        class form_class(forms.Form):
            things = forms.IntegerField(required=True)
            def invite_ids(self):
                return (i for i in range(0, int(self.cleaned_data['things'])))
            invite_ids = property(invite_ids)
        return form_class

    def send_invites(self, invitations, form):
        for invitation in invitations:
            print invitation.get_absolute_url()



def check(email):
    field = EmailField()
    return field.clean(email.strip())

class MultiEmailField(forms.Field):
    def clean(self, value):
        return [check(email) for email in value.split(',')]


email_attrs = {
    'class': 'required',
    'max_length': 100,
}

class EmailInvitationForm(forms.Form):
    """
    Form for sending invitations
    """
    from_email = forms.EmailField(widget=forms.TextInput(attrs=email_attrs))
    to_email = MultiEmailField(widget=forms.TextInput(attrs=email_attrs))

    personal_note = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )

    def invite_ids(self):
        return (email for email in self.cleaned_data['to_email'])
    invite_ids = property(invite_ids)

class EmailInviteBackend(InviteBackend):
    def get_form_class(self):
        return EmailInvitationForm

    def send_invites(self, invitations, form):
        emails = [invitation.target for invitation in invitations]
        send_mail('Subject', 'Our Message', form.cleaned_data['from_email'], emails) 

    def accept_invite(self, request, invitation):
        if request.user.is_authenticated():
            return super(EmailInviteBackend, self).accept_invite(request, invitation)
        else:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(email=invitation.target)
                self.model_class_objects.accept_invite(invitation, user)
                return HttpResponseRedirect('/')
            except User.DoesNotExist:
                pass
 
invite_site.register_backend('email', EmailInviteBackend)
invite_site.register_backend('console', ConsoleInviteBackend)
