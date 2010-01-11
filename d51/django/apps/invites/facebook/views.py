from django.http import Http404
from django.shortcuts import render_to_response
from d51.django.auth.facebook.models import FacebookID
from d51.django.auth.decorators import auth_required

index = auth_required()(invite_view('d51.django.apps.invites.facebook.backends.FacebookBackend', reverse('invite-thanks')))
