from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from d51.django.apps.invites.forms import InvitationForm


def index(request):
    if request.method == "POST":
        form = InvitationForm(request.POST)
        if form.is_valid():
            to_emails = form.cleaned_data['to_email']
            # TODO: handle error cases
            send_mail(
                'Subject',
                'Our message',
                form.cleaned_data['from_email'],
                to_emails
            )
            return redirect(reverse('invites_thanks') + '?num=%d' % len(to_emails))
    else:
        form = InvitationForm()

    return render_to_response(
        'invites/index.html',
        {
            'invitation_form': form,
        },
        context_instance=RequestContext(request)
    )
def thanks(request):
    return render_to_response(
        'invites/thanks.html',
        {
            'number_of_invites': int(request.GET['num']),
        },
        context_instance=RequestContext(request))

