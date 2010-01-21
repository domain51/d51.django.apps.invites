from .models import Invitation
from .utils import INVITE_SESSION_KEY

def invite_registration(request):
    invite_pk = request.session.get(INVITE_SESSION_KEY, None)
    if invite_pk is not None:
        try:
            return {
                'accepting_invite':Invitation.objects.get(pk=int(invite_pk))
            }
        except Invitation.DoesNotExist:
            pass
    return {
        'accepting_invite':None
    } 

