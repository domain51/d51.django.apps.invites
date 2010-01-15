from django.db.models.loading import cache as app_cache
from django.db import models
from .models import Invitation

def index(request, backend_type=None):
    



    try:
        facebook = getattr(request.user, 'facebook', None)
        return HttpResponseRedirect(reverse('facebook:invite'))
    except models.Model.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse('email:invite'))

def thanks(request):

