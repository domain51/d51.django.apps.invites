from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse 
from django.template.defaultfilters import slugify

class Invitation(models.Model):
    STATUS_CHOICES = (
        (0, 'Unsent'),
        (1, 'Pending'),
        (2, 'Accepted'),
        (3, 'Expired'),
    )
    sent_by = models.ForeignKey(User, related_name='invitations')
    backend = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES)
    published = models.DateTimeField(auto_now_add=True)
    resulting_user = models.ForeignKey(User, null=True, blank=True)

    def get_backend(self):
        from .backends import invite_site 
        return invite_site.load_backend_for(self)

    def get_absolute_url(self):
        return reverse('invites:invite-accept', kwargs={'username':'user-'+slugify(self.sent_by.get_full_name()), 'invite_pk':self.pk})
