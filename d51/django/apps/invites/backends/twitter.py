from django import forms, template
from django.conf import settings as django_settings
from django.contrib.sites.models import Site
from django.forms.fields import EmailField
from .base import InviteBackend
from ..sites import invite_site
from dolt.apis.bitly import Bitly
from dolt.apis.twitter import Twitter
from d51.django.auth.twitter.utils import *
import oauth2

class TwitterDMInvitationForm(forms.Form):
    to_ids = forms.CharField(required=True, widget=forms.Textarea())
    message = forms.CharField(required=True, max_length=120, widget=forms.Textarea())

    def invite_ids(self):
        return [id.strip() for id in self.cleaned_data['to_ids'].split(',') if id.strip()]
    invite_ids = property(invite_ids)

class TwitterTweetInvitationForm(forms.Form):
    message = forms.CharField(required=True, max_length=120, widget=forms.Textarea())
    invite_ids = ('global',)

def shorten_invite_url(invite, settings=django_settings):
    bitly_api = Bitly(login=settings.BITLY_LOGIN, apiKey=settings.BITLY_API_KEY)
    url = 'http://%s%s' % (Site.objects.get_current().domain, invite.get_absolute_url())
    results = bitly_api.shorten(longUrl=url)
    shortened_url = url 
    if results['statusCode'] != 'ERROR':
        shortened_url = results.get('results', {}).get(url, {}).get('shortUrl', None)
    return shortened_url

class TwitterInviteBackend(InviteBackend):
    def send_invites(self, invitations, form, *args, **kwargs):
        user = invitations[0].sent_by
        consumer = oauth2.Consumer(*get_key_and_secret())
        oauth_token = oauth2.Token(user.twitter.key, user.twitter.secret)
        http = oauth2.Client(consumer, oauth_token)
        twitter_api = Twitter(http=http)
        for invite in invitations:
            bitly_link = shorten_invite_url(invite)
            self.dispatch_invite(twitter_api, invite, ' '.join([form.cleaned_data['message'], bitly_link]))

class TwitterTweetInviteBackend(TwitterInviteBackend):
    def get_form_class(self):
        return TwitterTweetInvitationForm

    def dispatch_invite(self, twitter_api, invite, message):
        twitter_api.statuses.update.POST(**{
            'status':message,
        })

    def accept_invite(self, request, invitation):
        pass

class TwitterDMInviteBackend(TwitterInviteBackend):
    def get_form_class(self):
        return TwitterDMInvitationForm
    
    def dispatch_invite(self, twitter_api, invite, message):
        twitter_api.direct_messages.new.POST(**{
            'text':message,
            'screen_name': invite.target,
        })

    def accept_invite(self, request, invitation):
        pass

invite_site.register_backend('twitter-dm', TwitterDMInviteBackend)
invite_site.register_backend('twitter-tweet', TwitterTweetInviteBackend)
