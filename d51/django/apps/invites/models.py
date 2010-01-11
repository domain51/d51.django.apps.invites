from django.db import models
from django.contrib.auth.models import User

class Invitation(models.Model):
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Accepted'),
        (2, 'Expired'),
    )
    sent_by = models.ForeignKey(User, related_name='invitations')
    backend = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES)
    published = models.DateTimeField(auto_now_add=True)
    resulting_user = models.ForeignKey(User, null=True, blank=True)
