from django.core.mail import send_mail
from .forms import EmailInvitationForm

class EmailInviteBackend(InviteBackend):
    def get_form(self, request):
        form = None
        if request.method == 'POST':
            form = EmailInvitationForm(request.POST)
        else:
            form = EmailInvitationForm()
        return form

    def process_form(self, request, form):
        to_emails = form.cleaned_data['to_email']
        send_mail(
            self.get_subject(user),
            self.get_message(user),
            form.cleaned_data['from_email'],
            to_emails
        )
        for email in to_emails:
            Invitation.objects.create(
                        sent_by=request.user,
                        backend='d51.django.apps.invites.email.backends.EmailInviteBackend',
                        target=email,
                        status=Invitation.STATUS_CHOICES[0]
            )
