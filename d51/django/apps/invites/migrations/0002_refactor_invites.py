
from south.db import db
from django.db import models
from d51.django.apps.invites.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'InvitationFulfillment'
        db.create_table('invites_invitationfulfillment', (
            ('id', models.AutoField(primary_key=True)),
            ('invitation', models.ForeignKey(orm.Invitation, related_name='fulfillments')),
            ('user', models.OneToOneField(orm['auth.User'], related_name='accepted_invitation')),
            ('published', models.DateTimeField(auto_now_add=True)),
        ))
        db.send_create_signal('invites', ['InvitationFulfillment'])
        
        # Deleting field 'Invitation.status'
        db.delete_column('invites_invitation', 'status')
        
        # Deleting field 'Invitation.resulting_user'
        db.delete_column('invites_invitation', 'resulting_user_id')
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'InvitationFulfillment'
        db.delete_table('invites_invitationfulfillment')
        
        # Adding field 'Invitation.status'
        db.add_column('invites_invitation', 'status', models.PositiveIntegerField())
        
        # Adding field 'Invitation.resulting_user'
        db.add_column('invites_invitation', 'resulting_user', models.ForeignKey(orm['auth.User'], null=True, blank=True))
        
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'invites.invitationfulfillment': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'invitation': ('models.ForeignKey', ["orm['invites.Invitation']"], {'related_name': "'fulfillments'"}),
            'published': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'user': ('models.OneToOneField', ["orm['auth.User']"], {'related_name': "'accepted_invitation'"})
        },
        'invites.invitation': {
            'backend': ('models.CharField', [], {'max_length': '255'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'published': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'sent_by': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': "'invitations'"}),
            'target': ('models.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['invites']
