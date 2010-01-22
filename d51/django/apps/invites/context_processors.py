from django.core.exceptions import ObjectDoesNotExist
from .models import Invitation
from d51.django.apps.invites import models
from .utils import INVITE_SESSION_KEY

def invite_registration(request):
    invite = request.session.get(INVITE_SESSION_KEY, None)
    return {"accepting_invite": invite}

