from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse 
from django.template.defaultfilters import slugify

class InviteBackendException(Exception):
    pass

INVITE_SESSION_KEY = 'd51.django.apps.invites.INVITE_SESSION_KEY'
SENT_INVITATIONS = 'sent_invitations'

def get_absolute_url_for(obj):
    from .sites import invite_site
    backend = invite_site.load_backend_for(obj)
    return 'http://%(domain)s%(path)s' % {
        'domain': Site.objects.get_current().domain,
        'path': reverse(
            'invites:invite-%s-accept' % backend.backend_name,
            kwargs={
                'username': 'user-%s' % slugify(obj.sent_by.get_full_name()),
                'invite_pk': obj.pk,
            }),
    }


