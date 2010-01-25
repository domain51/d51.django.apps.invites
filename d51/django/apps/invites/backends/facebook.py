from d51.django.apps.invites.backends.base import InviteBackend
from d51.django.apps.invites.models import Group, Invitation
from d51.django.apps.invites.utils import SENT_INVITATIONS
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

CURRENT_GROUP_INVITATION = 'd51.django.apps.invites.backends.facebook.CURRENT_GROUP_INVITATION'

class Backend(InviteBackend):
    def __init__(self, *args, **kwargs):
        super(Backend, self).__init__(*args, **kwargs)

    @property
    def model_class(self):
        return Group

    def create_view(self, request, extra_context={}):
        if request.method != 'POST':
            group = Group.objects.create(sent_by=request.user, backend=self.backend_name)
            request.session[CURRENT_GROUP_INVITATION] = group
            extra_context['group'] = group
        return super(Backend, self).create_view(request, extra_context)

    def can_handle_create_for(self, request, with_form):
        return request.method == 'POST'

    def handle_create_for(self, request, with_form, and_context):
        form, context = with_form, and_context
        targets = request.POST.getlist('ids[]')

        group = request.session[CURRENT_GROUP_INVITATION]
        request.session[CURRENT_GROUP_INVITATION] = None

        invitations = []
        for target in targets:
            invitations.append(Invitation.objects.create(
                sent_by=group.sent_by,
                target=target,
                group=group
            ))
        request.session[SENT_INVITATIONS] = invitations
        return self.successful_create_redirect


    def fulfill_current_invitation(self, request):
        # TODO: should only work if user is FB user
        group = self.fetch_current_invitation_object(request)
        if hasattr(request.user, 'facebook'):
            group.fulfill(request.user.facebook.uid, request.user)
        else:
            invitation = group.invitations.create(
                                            sent_by=group.sent_by,
                                            backend=group.backend,
                                            target='nogroup-%d'%user.pk,
            )
            invitation.fulfill(request.user)

    def get_registration_url(self):
        # TODO: refactor into common super-class
        import urllib
        return '%s?%s' % (reverse(self.home_view_name), urllib.urlencode({'next':reverse('registration_activation_thanks')})) 


