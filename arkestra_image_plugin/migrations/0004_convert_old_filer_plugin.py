# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        # loop over FilerImage instances
        for item in orm.FilerImage.objects.all():
                        
            # collect FilerImage attributes to copy
            cmsplugin_ptr = item.cmsplugin_ptr
            width = item.width or 1000
            height = item.height
            floatvalue = item.float
            aspect_ratio = item.aspect_ratio or 0

            # collect CMSPlugin attributes to copy
            language = item.language
            position = item.position
            id = item.id

            # collect CMSPlugin attributes to copy
            parent = item.parent
            tree_id = item.tree_id
            lft = item.lft
            rght = item.rght
            level = item.level
            placeholder = item.placeholder
            
            # collect ImageSetItem attributes to copy
            image = item.image
            alt_text = item.alt_text
            auto_image_caption = item.use_description_as_caption
            manual_image_caption = item.caption
            
            
            # create and save an ImageSet instance
            imageset = orm.ImageSetPlugin(
                plugin_type="ImageSetPublisher", 
                cmsplugin_ptr=cmsplugin_ptr,
                width=width,
                height=height,
                float=floatvalue,
                aspect_ratio=aspect_ratio,
                language=language,
                position=position,
                id=id,
                parent=parent,
                tree_id=tree_id,
                lft=lft,
                rght=rght,
                level=level,
                placeholder=placeholder,
                )
            imageset.save()
                
            # create and save an ImageSetItem
            imagesetitem = orm.ImageSetItem(
                plugin=imageset, 
                image=image,
                alt_text=alt_text,
                auto_image_caption=auto_image_caption,
                manual_image_caption=manual_image_caption
                ) 
            imagesetitem.save() 

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'arkestra_image_plugin.embeddedvideosetitem': {
            'Meta': {'ordering': "('inline_item_ordering', 'id')", 'object_name': 'EmbeddedVideoSetItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'aspect_ratio': ('django.db.models.fields.FloatField', [], {'default': '1.333'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_item_ordering': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'embeddedvideoset_item'", 'to': "orm['arkestra_image_plugin.EmbeddedVideoSetPlugin']"}),
            'service': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'video_autoplay': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'video_code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video_title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'arkestra_image_plugin.embeddedvideosetplugin': {
            'Meta': {'object_name': 'EmbeddedVideoSetPlugin', 'db_table': "'cmsplugin_embeddedvideosetplugin'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '1000.0'})
        },
        'arkestra_image_plugin.filerimage': {
            'Meta': {'object_name': 'FilerImage', 'db_table': "'cmsplugin_filerimage'", '_ormbases': ['cms.CMSPlugin']},
            'alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'aspect_ratio': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'float': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']"}),
            'use_autoscale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'use_description_as_caption': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '1000.0', 'null': 'True', 'blank': 'True'})
        },
        'arkestra_image_plugin.imagesetitem': {
            'Meta': {'ordering': "('inline_item_ordering', 'id')", 'object_name': 'ImageSetItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'auto_image_caption': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_image_title': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_link_description': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_link_title': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'destination_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links_to_imagesetitem'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'destination_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'on_delete': 'models.PROTECT'}),
            'inline_item_ordering': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'manual_image_caption': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'manual_image_title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'manual_link_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'manual_link_title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imageset_item'", 'to': "orm['arkestra_image_plugin.ImageSetPlugin']"})
        },
        'arkestra_image_plugin.imagesetplugin': {
            'Meta': {'object_name': 'ImageSetPlugin', 'db_table': "'cmsplugin_imagesetplugin'", '_ormbases': ['cms.CMSPlugin']},
            'aspect_ratio': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'float': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'items_per_row': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'basic'", 'max_length': '50'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '1000.0'})
        },
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
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 10, 0, 0)'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['arkestra_image_plugin']
    symmetrical = True
