from django import forms, template
from django.contrib.sites.models import Site
from django.forms.fields import EmailField
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from .base import InviteBackend

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

    # TODO: This should be a view...
    # TODO: This is too abstracted, has form been validated?  This all needs to
    #       happen in the same code
    # TODO: These need to be queued up in RabbitMQ
    def send_invites(self, invitations, form, request):
        for invitation in invitations:
            context = template.Context({
                'invitation': invitation,
                'url': invitation.get_absolute_url(),
                'note': form.cleaned_data['personal_note'],
            })
            subject_template = template.loader.get_template('invites/emails/subject.txt')
            message_template = template.loader.get_template('invites/emails/message.txt')
            send_mail(
                subject_template.render(context).strip(),
                message_template.render(context),
                request.user.email,
                (invitation.target, )
            )
        return invitations
