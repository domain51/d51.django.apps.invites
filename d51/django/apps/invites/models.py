from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse 
from django.template.defaultfilters import slugify

class InvitationManager(models.Manager):
    def confirm(self, invitation, user):
        existing_fulfillments = invitation.fulfillments.filter(user=user, invitation=invitation)
        if not existing_fulfillments:
            return InvitationFulfillment.objects.create(
                user=user,
                invitation=invitation,
            )
        return None

    def create_for(self, backend_string, user, with_form):
        return [self.create(**{
                'target':id,
                'backend':backend_string,
                'sent_by':user,
            }) for id in with_form.invite_ids]

class Invitation(models.Model):
    sent_by = models.ForeignKey(User, related_name='invitations')
    backend = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    published = models.DateTimeField(auto_now_add=True)
    objects = InvitationManager()

    def get_number_fulfilled(self):
        return len(self.fulfillments.all())
    number_fulfilled = property(get_number_fulfilled)

    def get_backend(self):
        from .sites import invite_site 
        return invite_site.load_backend_for(self)

    def get_absolute_url(self):
        return reverse('invites:invite-accept', kwargs={'username':'user-'+slugify(self.sent_by.get_full_name()), 'invite_pk':self.pk})

class InvitationFulfillment(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='fulfillments')
    user = models.OneToOneField(User, related_name='accepted_invitation')
    published = models.DateTimeField(auto_now_add=True)

