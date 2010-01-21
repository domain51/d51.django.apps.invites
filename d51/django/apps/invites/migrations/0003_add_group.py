
from south.db import db
from django.db import models
from d51.django.apps.invites.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Group'
        db.create_table('invites_group', (
            ('id', models.AutoField(primary_key=True)),
            ('sent_by', models.ForeignKey(orm['auth.User'], related_name="group_invitation")),
            ('backend', models.CharField(max_length=255)),
        ))
        db.send_create_signal('invites', ['Group'])
        
        # Adding field 'Invitation.group'
        db.add_column('invites_invitation', 'group', models.ForeignKey(orm.Group, related_name="invitations", null=True, blank=True))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Group'
        db.delete_table('invites_group')
        
        # Deleting field 'Invitation.group'
        db.delete_column('invites_invitation', 'group_id')
        
    
    
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
        'invites.group': {
            'backend': ('models.CharField', [], {'max_length': '255'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'sent_by': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': '"group_invitation"'})
        },
        'invites.invitation': {
            'backend': ('models.CharField', [], {'max_length': '255'}),
            'group': ('models.ForeignKey', ["orm['invites.Group']"], {'related_name': '"invitations"', 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'published': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'sent_by': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': "'invitations'"}),
            'target': ('models.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['invites']
