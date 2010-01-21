from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse 
from django.template.defaultfilters import slugify

class InvitationManager(models.Manager):
    def confirm(self, invitation, user):
        """ deprecated: see Invitation.fulfill """
        return self.invitation.fulfill(user)

    def create_for(self, backend_string, user, with_form):
        return [self.create(**{
                'target':id,
                'backend':backend_string,
                'sent_by':user,
            }) for id in with_form.invite_ids]


class Group(models.Model):
    sent_by = models.ForeignKey(User, related_name="group_invitation")
    backend = models.CharField(max_length=255)

    def fulfill(self, target, user):
        try:
            invitation = self.invitations.get(target=target)
            invitation.fulfill(user)
            return True
        except Invitation.DoesNotExist, e:
            return False

class Invitation(models.Model):
    sent_by = models.ForeignKey(User, related_name='invitations')
    backend = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    published = models.DateTimeField(auto_now_add=True)
    objects = InvitationManager()
    group = models.ForeignKey(Group, related_name="invitations", blank=True, null=True)

    def get_number_fulfilled(self):
        return self.fulfillments.all().count()
    number_fulfilled = property(get_number_fulfilled)

    def get_backend(self):
        from .sites import invite_site 
        return invite_site.load_backend_for(self)

    def get_absolute_url(self):
        return reverse('invites:invite-accept', kwargs={'username':'user-'+slugify(self.sent_by.get_full_name()), 'invite_pk':self.pk})

    def fulfill(self, user):
        InvitationFulfillment.objects.get_or_create(
            invitation=self,
            user=user
        )

class InvitationFulfillment(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='fulfillments')
    user = models.OneToOneField(User, related_name='accepted_invitation')
    published = models.DateTimeField(auto_now_add=True)

