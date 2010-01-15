from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse 
from django.template.defaultfilters import slugify

class InvitationManager(models.Manager):
    def accept_invite(self, invitation, user):
        invitation.resulting_user = user
        invitation.status = 1
        invitation.save()

    def create_for(self, backend_string, user, with_form):
        return [self.create(**{
                'target':id,
                'status':0,
                'backend':backend_string,
                'sent_by':user,
            }) for id in with_form.invite_ids]

class Invitation(models.Model):
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Accepted'),
    )
    sent_by = models.ForeignKey(User, related_name='invitations')
    backend = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES)
    published = models.DateTimeField(auto_now_add=True)
    resulting_user = models.ForeignKey(User, null=True, blank=True)

    objects = InvitationManager()

    def get_backend(self):
        from .backends import invite_site 
        return invite_site.load_backend_for(self)

    def get_absolute_url(self):
        return reverse('invites:invite-accept', kwargs={'username':'user-'+slugify(self.sent_by.get_full_name()), 'invite_pk':self.pk})
