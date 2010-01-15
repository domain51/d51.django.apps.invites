
from south.db import db
from django.db import models
from d51.django.apps.invites.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Invitation'
        db.create_table('invites_invitation', (
            ('id', models.AutoField(primary_key=True)),
            ('sent_by', models.ForeignKey(orm['auth.User'], related_name='invitations')),
            ('backend', models.CharField(max_length=255)),
            ('target', models.CharField(max_length=255)),
            ('status', models.PositiveIntegerField()),
            ('published', models.DateTimeField(auto_now_add=True)),
            ('resulting_user', models.ForeignKey(orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('invites', ['Invitation'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Invitation'
        db.delete_table('invites_invitation')
        
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'invites.invitation': {
            'backend': ('models.CharField', [], {'max_length': '255'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'published': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'resulting_user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'}),
            'sent_by': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': "'invitations'"}),
            'status': ('models.PositiveIntegerField', [], {}),
            'target': ('models.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['invites']
