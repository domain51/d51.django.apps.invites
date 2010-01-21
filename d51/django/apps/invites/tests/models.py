from d51.django.apps.invites.models import *
from django.contrib.auth.models import User
from django.test import TestCase
import random

def generate_random_target():
    return "some-random-target-%d" % random.randint(1000, 2000)

def generate_random_user():
    return User.objects.create(username="random-user-%d" % random.randint(1000, 2000))

class TestOfGroup(TestCase):
    def test_can_fulfill_target(self):
        random_target = generate_random_target()
        user = generate_random_user()
        group = Group.objects.create(sent_by=user, backend='foobar')
        invitation = Invitation.objects.create(
            sent_by=user,
            backend='foobar',
            target=random_target,
            group=group
        )

        fulfillments = InvitationFulfillment.objects.filter(invitation=invitation)
        self.assertEqual(0, fulfillments.count(), 'sanity check')
        group.fulfill(random_target, generate_random_user())
        self.assertEqual(1, fulfillments.count())

    def test_fulfill_returns_true_if_fulfilled(self):
        random_target = generate_random_target()
        user = generate_random_user()
        group = Group.objects.create(sent_by=user, backend='foobar')
        invitation = Invitation.objects.create(
            sent_by=user,
            backend='foobar',
            target=random_target,
            group=group
        )

        self.assertTrue(group.fulfill(random_target, generate_random_user()))

    def test_fulfill_returns_false_if_cannot_fulfill(self):
        sent_by = generate_random_user()
        group = Group.objects.create(sent_by=sent_by, backend='foobar')
        self.assertFalse(group.fulfill(generate_random_target(), generate_random_user()))

class TestOfInvitation(TestCase):
    def test_can_fulfill_with_user(self):
        sent_by = generate_random_user()
        invitation = Invitation.objects.create(sent_by=sent_by, backend='foobar')
        fulfillments = InvitationFulfillment.objects.filter(invitation=invitation)

        self.assertEqual(0, fulfillments.count(), 'sanity check')

        accepter = generate_random_user()
        invitation.fulfill(accepter)

        self.assertEqual(1, fulfillments.count())


