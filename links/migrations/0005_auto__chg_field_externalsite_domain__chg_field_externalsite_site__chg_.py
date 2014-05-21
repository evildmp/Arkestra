# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ExternalSite.domain'
        db.alter_column('links_externalsite', 'domain', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'ExternalSite.site'
        db.alter_column('links_externalsite', 'site', self.gf('django.db.models.fields.CharField')(default='', max_length=50))

        # Changing field 'ExternalLink.description'
        db.alter_column('links_externallink', 'description', self.gf('django.db.models.fields.TextField')(default='', max_length=256))

        # Changing field 'GenericLinkListPlugin.final_separator'
        db.alter_column('cmsplugin_genericlinklistplugin', 'final_separator', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'GenericLinkListPlugin.separator'
        db.alter_column('cmsplugin_genericlinklistplugin', 'separator', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Adding field 'GenericLinkListPluginItem.format'
        db.add_column('links_genericlinklistpluginitem', 'format',
                      self.gf('django.db.models.fields.CharField')(default='title', max_length=25),
                      keep_default=False)





        # Rename field 'GenericLinkListPluginItem.description_override'
        db.rename_column(
            'links_genericlinklistpluginitem',
            'description_override',
            'summary_override'
            )



        # Rename field 'ObjectLink.description_override'
        db.rename_column(
            'links_objectlink',
            'description_override',
            'summary_override'
            )






        # Changing field 'GenericLinkListPluginItem.text_override'
        db.alter_column('links_genericlinklistpluginitem', 'text_override', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'GenericLinkListPluginItem.metadata_override'
        db.alter_column('links_genericlinklistpluginitem', 'metadata_override', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'GenericLinkListPluginItem.html_title_attribute'
        db.alter_column('links_genericlinklistpluginitem', 'html_title_attribute', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'GenericLinkListPluginItem.heading_override'
        db.alter_column('links_genericlinklistpluginitem', 'heading_override', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Adding field 'ObjectLink.format'
        db.add_column('links_objectlink', 'format',
                      self.gf('django.db.models.fields.CharField')(default='title', max_length=25),
                      keep_default=False)



        # Changing field 'ObjectLink.text_override'
        db.alter_column('links_objectlink', 'text_override', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'ObjectLink.metadata_override'
        db.alter_column('links_objectlink', 'metadata_override', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'ObjectLink.html_title_attribute'
        db.alter_column('links_objectlink', 'html_title_attribute', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'ObjectLink.heading_override'
        db.alter_column('links_objectlink', 'heading_override', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'FocusOnPluginItemEditor.short_text_override'
        db.alter_column('links_focusonpluginitemeditor', 'short_text_override', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'FocusOnPluginItemEditor.text_override'
        db.alter_column('links_focusonpluginitemeditor', 'text_override', self.gf('django.db.models.fields.CharField')(default='', max_length=256))

        # Changing field 'FocusOnPluginItemEditor.description_override'
        db.alter_column('links_focusonpluginitemeditor', 'description_override', self.gf('django.db.models.fields.TextField')(default='', max_length=256))

    def backwards(self, orm):

        # Changing field 'ExternalSite.domain'
        db.alter_column('links_externalsite', 'domain', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'ExternalSite.site'
        db.alter_column('links_externalsite', 'site', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'ExternalLink.description'
        db.alter_column('links_externallink', 'description', self.gf('django.db.models.fields.TextField')(max_length=256, null=True))

        # Changing field 'GenericLinkListPlugin.final_separator'
        db.alter_column('cmsplugin_genericlinklistplugin', 'final_separator', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'GenericLinkListPlugin.separator'
        db.alter_column('cmsplugin_genericlinklistplugin', 'separator', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))


        # Deleting field 'GenericLinkListPluginItem.format'
        db.delete_column('links_genericlinklistpluginitem', 'format')

        # Rename summary back to description
        db.rename_column('links_genericlinklistpluginitem', 'summary_override',  'description_override')


        # Changing field 'GenericLinkListPluginItem.text_override'
        db.alter_column('links_genericlinklistpluginitem', 'text_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'GenericLinkListPluginItem.metadata_override'
        db.alter_column('links_genericlinklistpluginitem', 'metadata_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'GenericLinkListPluginItem.html_title_attribute'
        db.alter_column('links_genericlinklistpluginitem', 'html_title_attribute', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'GenericLinkListPluginItem.heading_override'
        db.alter_column('links_genericlinklistpluginitem', 'heading_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))


        # Rename field 'ObjectLink.description_override'
        db.rename_column('links_objectlink', 'summary_override', 'description_override')


        # Deleting field 'ObjectLink.format'
        db.delete_column('links_objectlink', 'format')



        # Changing field 'ObjectLink.text_override'
        db.alter_column('links_objectlink', 'text_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'ObjectLink.metadata_override'
        db.alter_column('links_objectlink', 'metadata_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'ObjectLink.html_title_attribute'
        db.alter_column('links_objectlink', 'html_title_attribute', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'ObjectLink.heading_override'
        db.alter_column('links_objectlink', 'heading_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'FocusOnPluginItemEditor.short_text_override'
        db.alter_column('links_focusonpluginitemeditor', 'short_text_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'FocusOnPluginItemEditor.text_override'
        db.alter_column('links_focusonpluginitemeditor', 'text_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'FocusOnPluginItemEditor.description_override'
        db.alter_column('links_focusonpluginitemeditor', 'description_override', self.gf('django.db.models.fields.TextField')(max_length=256, null=True))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 4, 10, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_files'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_files'", 'null': 'True', 'to': "orm['auth.User']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_filer.file_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.folder': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('parent', 'name'),)", 'object_name': 'Folder'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filer_owned_folders'", 'null': 'True', 'to': "orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.image': {
            'Meta': {'object_name': 'Image', '_ormbases': ['filer.File']},
            '_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['filer.File']", 'unique': 'True', 'primary_key': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'links.carouselplugin': {
            'Meta': {'object_name': 'CarouselPlugin', 'db_table': "'cmsplugin_carouselplugin'", '_ormbases': ['cms.CMSPlugin']},
            'aspect_ratio': ('django.db.models.fields.FloatField', [], {'default': '1.5', 'null': 'True', 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '100.0'})
        },
        'links.carouselpluginitem': {
            'Meta': {'ordering': "['inline_item_ordering', 'id']", 'object_name': 'CarouselPluginItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'destination_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links_to_carouselpluginitem'", 'to': "orm['contenttypes.ContentType']"}),
            'destination_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']"}),
            'inline_item_ordering': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'link_title': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'carousel_item'", 'to': "orm['links.CarouselPlugin']"})
        },
        'links.externallink': {
            'Meta': {'ordering': "['title']", 'object_name': 'ExternalLink'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'}),
            'external_site': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['links.ExternalSite']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['links.LinkType']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'links.externalsite': {
            'Meta': {'ordering': "['domain']", 'object_name': 'ExternalSite'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['links.ExternalSite']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'site': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'links.focusonplugineditor': {
            'Meta': {'object_name': 'FocusOnPluginEditor', 'db_table': "'cmsplugin_focusonplugineditor'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'heading_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'})
        },
        'links.focusonpluginitemeditor': {
            'Meta': {'ordering': "['id']", 'object_name': 'FocusOnPluginItemEditor'},
            'description_override': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'}),
            'destination_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links_to_focusonpluginitemeditor'", 'to': "orm['contenttypes.ContentType']"}),
            'destination_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_override': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'focuson_item'", 'to': "orm['links.FocusOnPluginEditor']"}),
            'short_text_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'text_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'links.genericlinklistplugin': {
            'Meta': {'object_name': 'GenericLinkListPlugin', 'db_table': "'cmsplugin_genericlinklistplugin'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'final_separator': ('django.db.models.fields.CharField', [], {'default': "' and '", 'max_length': '20', 'blank': 'True'}),
            'insert_as': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'separator': ('django.db.models.fields.CharField', [], {'default': "', '", 'max_length': '20', 'blank': 'True'}),
            'use_link_icons': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'links.genericlinklistpluginitem': {
            'Meta': {'ordering': "['inline_item_ordering', 'id']", 'object_name': 'GenericLinkListPluginItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'destination_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links_to_genericlinklistpluginitem'", 'to': "orm['contenttypes.ContentType']"}),
            'destination_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'title'", 'max_length': '25'}),
            'heading_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'html_title_attribute': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_item_ordering': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'key_link': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'metadata_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links_item'", 'to': "orm['links.GenericLinkListPlugin']"}),
            'summary_override': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'}),
            'text_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'links.linktype': {
            'Meta': {'object_name': 'LinkType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'scheme': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'links.objectlink': {
            'Meta': {'object_name': 'ObjectLink'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'destination_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links_to_objectlink'", 'to': "orm['contenttypes.ContentType']"}),
            'destination_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'title'", 'max_length': '25'}),
            'heading_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'html_title_attribute': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_link': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'metadata_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'summary_override': ('django.db.models.fields.TextField', [], {'max_length': '256', 'blank': 'True'}),
            'text_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        }
    }

    complete_apps = ['links']