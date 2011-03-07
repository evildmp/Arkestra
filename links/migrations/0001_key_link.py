
from south.db import db
from django.db import models
from links.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'GenericLinkListPlugin'
        db.create_table('cmsplugin_genericlinklistplugin', (
            ('cmsplugin_ptr', orm['links.GenericLinkListPlugin:cmsplugin_ptr']),
            ('insert_as', orm['links.GenericLinkListPlugin:insert_as']),
        ))
        db.send_create_signal('links', ['GenericLinkListPlugin'])
        
        # Adding model 'GenericLinkListPluginItem'
        db.create_table('links_genericlinklistpluginitem', (
            ('id', orm['links.GenericLinkListPluginItem:id']),
            ('destination_content_type', orm['links.GenericLinkListPluginItem:destination_content_type']),
            ('destination_object_id', orm['links.GenericLinkListPluginItem:destination_object_id']),
            ('text_override', orm['links.GenericLinkListPluginItem:text_override']),
            ('description_override', orm['links.GenericLinkListPluginItem:description_override']),
            ('optional_title', orm['links.GenericLinkListPluginItem:optional_title']),
            ('include_description', orm['links.GenericLinkListPluginItem:include_description']),
            ('plugin', orm['links.GenericLinkListPluginItem:plugin']),
        ))
        db.send_create_signal('links', ['GenericLinkListPluginItem'])
        
        # Adding model 'ExternalLink'
        db.create_table('links_externallink', (
            ('id', orm['links.ExternalLink:id']),
            ('title', orm['links.ExternalLink:title']),
            ('url', orm['links.ExternalLink:url']),
            ('external_site', orm['links.ExternalLink:external_site']),
            ('description', orm['links.ExternalLink:description']),
        ))
        db.send_create_signal('links', ['ExternalLink'])
        
        # Adding model 'ObjectLink'
        db.create_table('links_objectlink', (
            ('id', orm['links.ObjectLink:id']),
            ('destination_content_type', orm['links.ObjectLink:destination_content_type']),
            ('destination_object_id', orm['links.ObjectLink:destination_object_id']),
            ('text_override', orm['links.ObjectLink:text_override']),
            ('description_override', orm['links.ObjectLink:description_override']),
            ('optional_title', orm['links.ObjectLink:optional_title']),
            ('include_description', orm['links.ObjectLink:include_description']),
            ('content_type', orm['links.ObjectLink:content_type']),
            ('object_id', orm['links.ObjectLink:object_id']),
        ))
        db.send_create_signal('links', ['ObjectLink'])
        
        # Adding model 'ExternalSite'
        db.create_table('links_externalsite', (
            ('id', orm['links.ExternalSite:id']),
            ('site', orm['links.ExternalSite:site']),
        ))
        db.send_create_signal('links', ['ExternalSite'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'GenericLinkListPlugin'
        db.delete_table('cmsplugin_genericlinklistplugin')
        
        # Deleting model 'GenericLinkListPluginItem'
        db.delete_table('links_genericlinklistpluginitem')
        
        # Deleting model 'ExternalLink'
        db.delete_table('links_externallink')
        
        # Deleting model 'ObjectLink'
        db.delete_table('links_objectlink')
        
        # Deleting model 'ExternalSite'
        db.delete_table('links_externalsite')
        
    
    
    models = {
        'cms.cmsplugin': {
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Page']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'publisher_is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'publisher_public': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'publisher_draft'", 'unique': 'True', 'null': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'publisher_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.page': {
            'changed_by': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'menu_login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'moderator_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'blank': 'True'}),
            'navigation_extenders': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'page_flags': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['cms.Page']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'publication_end_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'publisher_is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'publisher_public': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'publisher_draft'", 'unique': 'True', 'null': 'True', 'to': "orm['cms.Page']"}),
            'publisher_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'reverse_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'soft_root': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'links.externallink': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'external_site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['links.ExternalSite']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'links.externalsite': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'links.genericlinklistplugin': {
            'Meta': {'db_table': "'cmsplugin_genericlinklistplugin'"},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'insert_as': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        },
        'links.genericlinklistpluginitem': {
            'description_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'destination_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links_to_genericlinklistpluginitem'", 'to': "orm['contenttypes.ContentType']"}),
            'destination_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_description': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'optional_title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['links.GenericLinkListPlugin']"}),
            'text_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'links.objectlink': {
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'destination_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links_to_objectlink'", 'to': "orm['contenttypes.ContentType']"}),
            'destination_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_description': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'optional_title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'text_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['links']
