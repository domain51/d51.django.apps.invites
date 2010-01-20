from d51.django.apps.invites.backends.base import InviteBackend
from d51.django.apps.invites.sites import invite_site

class Backend(InviteBackend):
    pass

invite_site.register_backend('facebook', Backend)
