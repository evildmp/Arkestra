# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Insert'
        db.create_table('arkestra_utilities_insert', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('insertion_point', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=60)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Placeholder'], null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=256, null=True)),
        ))
        db.send_create_signal('arkestra_utilities', ['Insert'])


    def backwards(self, orm):
        # Deleting model 'Insert'
        db.delete_table('arkestra_utilities_insert')


    models = {
        'arkestra_utilities.insert': {
            'Meta': {'object_name': 'Insert'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '256', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insertion_point': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '60'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['arkestra_utilities']