
from south.db import db
from django.db import models
from chaining.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('chaining_category', (
            ('id', orm['chaining.Category:id']),
            ('name', orm['chaining.Category:name']),
        ))
        db.send_create_signal('chaining', ['Category'])
        
        # Adding model 'SubCategory'
        db.create_table('chaining_subcategory', (
            ('id', orm['chaining.SubCategory:id']),
            ('category', orm['chaining.SubCategory:category']),
            ('name', orm['chaining.SubCategory:name']),
        ))
        db.send_create_signal('chaining', ['SubCategory'])
        
        # Adding model 'Product'
        db.create_table('chaining_product', (
            ('id', orm['chaining.Product:id']),
            ('name', orm['chaining.Product:name']),
            ('subcategory', orm['chaining.Product:subcategory']),
        ))
        db.send_create_signal('chaining', ['Product'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('chaining_category')
        
        # Deleting model 'SubCategory'
        db.delete_table('chaining_subcategory')
        
        # Deleting model 'Product'
        db.delete_table('chaining_product')
        
    
    
    models = {
        'chaining.category': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'chaining.product': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chaining.SubCategory']"})
        },
        'chaining.subcategory': {
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chaining.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['chaining']
