# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Event.body'
        db.add_column('news_and_events_event', 'body', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Placeholder'], null=True), keep_default=False)

        # Adding field 'Event.external_url'
        db.add_column('news_and_events_event', 'external_url', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event_item', blank=True, null=True, to=orm['links.ExternalLink']), keep_default=False)

        # Removing M2M table for field publishing_destinations on 'Event'
        # db.delete_table('news_and_events_event_publishing_destinations')
        # db.rename_table('news_and_events_event_publishing_destinations', 'news_and_events_event_publish_to')

        # Adding M2M table for field publish_to on 'Event'
        # db.create_table('news_and_events_event_publish_to', (
        #     ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
        #     ('event', models.ForeignKey(orm['news_and_events.event'], null=False)),
        #     ('entity', models.ForeignKey(orm['contacts_and_people.entity'], null=False))
        # ))
        # db.create_unique('news_and_events_event_publish_to', ['event_id', 'entity_id'])

        # Changing field 'Event.subtitle'
        db.alter_column('news_and_events_event', 'subtitle', self.gf('django.db.models.fields.TextField')(max_length=256, null=True))

        # Adding field 'NewsArticle.body'
        db.add_column('news_and_events_newsarticle', 'body', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Placeholder'], null=True), keep_default=False)

        # Adding field 'NewsArticle.external_url'
        db.add_column('news_and_events_newsarticle', 'external_url', self.gf('django.db.models.fields.related.ForeignKey')(related_name='newsarticle_item', blank=True, null=True, to=orm['links.ExternalLink']), keep_default=False)

        # Removing M2M table for field publishing_destinations on 'NewsArticle'
        # db.delete_table('news_and_events_newsarticle_publishing_destinations')
        # db.rename_table('news_and_events_newsarticle_publishing_destinations', 'news_and_events_newsarticle_publish_to')

        # Adding M2M table for field publish_to on 'NewsArticle'
        # db.create_table('news_and_events_newsarticle_publish_to', (
        #     ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
        #     ('newsarticle', models.ForeignKey(orm['news_and_events.newsarticle'], null=False)),
        #     ('entity', models.ForeignKey(orm['contacts_and_people.entity'], null=False))
        # ))
        # db.create_unique('news_and_events_newsarticle_publish_to', ['newsarticle_id', 'entity_id'])

        # Changing field 'NewsArticle.subtitle'
        db.alter_column('news_and_events_newsarticle', 'subtitle', self.gf('django.db.models.fields.TextField')(max_length=256, null=True))


    def backwards(self, orm):
        
        # Deleting field 'Event.body'
        db.delete_column('news_and_events_event', 'body_id')

        # Deleting field 'Event.external_url'
        db.delete_column('news_and_events_event', 'external_url_id')

        # Adding M2M table for field publishing_destinations on 'Event'
        # db.create_table('news_and_events_event_publishing_destinations', (
        #     ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
        #     ('event', models.ForeignKey(orm['news_and_events.event'], null=False)),
        #     ('entity', models.ForeignKey(orm['contacts_and_people.entity'], null=False))
        # ))
        # db.create_unique('news_and_events_event_publishing_destinations', ['event_id', 'entity_id'])

        # Removing M2M table for field publish_to on 'Event'
        # db.delete_table('news_and_events_event_publish_to')
        # db.rename_table('news_and_events_event_publish_to', 'news_and_events_event_publishing_destinations')

        # Changing field 'Event.subtitle'
        db.alter_column('news_and_events_event', 'subtitle', self.gf('django.db.models.fields.TextField')(max_length=350, null=True))

        # Deleting field 'NewsArticle.body'
        db.delete_column('news_and_events_newsarticle', 'body_id')

        # Deleting field 'NewsArticle.external_url'
        db.delete_column('news_and_events_newsarticle', 'external_url_id')

        # Adding M2M table for field publishing_destinations on 'NewsArticle'
        # db.create_table('news_and_events_newsarticle_publishing_destinations', (
        #     ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
        #     ('newsarticle', models.ForeignKey(orm['news_and_events.newsarticle'], null=False)),
        #     ('entity', models.ForeignKey(orm['contacts_and_people.entity'], null=False))
        # ))
        # db.create_unique('news_and_events_newsarticle_publishing_destinations', ['newsarticle_id', 'entity_id'])

        # Removing M2M table for field publish_to on 'NewsArticle'
        # db.rename_table('news_and_events_newsarticle_publish_to', 'news_and_events_newsarticle_publishing_destinations')
 
        # Changing field 'NewsArticle.subtitle'
        db.alter_column('news_and_events_newsarticle', 'subtitle', self.gf('django.db.models.fields.TextField')(max_length=350, null=True))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
        'cms.page': {
            'Meta': {'object_name': 'Page'},
            'changed_by': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'limit_visibility_in_menu': ('django.db.models.fields.SmallIntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'moderator_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'blank': 'True'}),
            'navigation_extenders': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'blank': 'True', 'null': 'True', 'to': "orm['cms.Page']"}),
            'placeholders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cms.Placeholder']", 'symmetrical': 'False'}),
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
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'contacts_and_people.building': {
            'Meta': {'object_name': 'Building'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'access_and_parking': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'additional_street_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'getting_here': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'map': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts_and_people.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zoom': ('django.db.models.fields.IntegerField', [], {'default': '17', 'null': 'True', 'blank': 'True'})
        },
        'contacts_and_people.entity': {
            'Meta': {'object_name': 'Entity', '_ormbases': ['contacts_and_people.EntityLite']},
            'abstract_entity': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'access_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'auto_contacts_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'auto_news_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts_and_people.Building']", 'null': 'True', 'blank': 'True'}),
            'contacts_page_menu_title': ('django.db.models.fields.CharField', [], {'default': "'Contacts & people'", 'max_length': '50'}),
            'display_parent': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'entitylite_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['contacts_and_people.EntityLite']", 'unique': 'True', 'primary_key': 'True'}),
            'external_url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_item'", 'blank': 'True', 'null': 'True', 'to': "orm['links.ExternalLink']"}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'news_page_menu_title': ('django.db.models.fields.CharField', [], {'default': "'News & events'", 'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'precise_location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity'", 'unique': 'True', 'null': 'True', 'to': "orm['cms.Page']"})
        },
        'contacts_and_people.entitylite': {
            'Meta': {'object_name': 'EntityLite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contacts_and_people.membership': {
            'Meta': {'object_name': 'Membership'},
            'display_role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'display_roles'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Membership']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['contacts_and_people.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance_to_entity': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'importance_to_person': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'key_contact': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'member_of'", 'to': "orm['contacts_and_people.Person']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'contacts_and_people.person': {
            'Meta': {'object_name': 'Person', '_ormbases': ['contacts_and_people.PersonLite']},
            'access_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts_and_people.Building']", 'null': 'True', 'blank': 'True'}),
            'data_feed_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'entities': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'people'", 'to': "orm['contacts_and_people.Entity']", 'through': "orm['contacts_and_people.Membership']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'external_url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'person_item'", 'blank': 'True', 'null': 'True', 'to': "orm['links.ExternalLink']"}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'institutional_username': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'override_entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'people_override'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'personlite_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['contacts_and_people.PersonLite']", 'unique': 'True', 'primary_key': 'True'}),
            'please_contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact_for'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Person']"}),
            'precise_location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'db_index': 'True'}),
            'staff_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'person_user'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"})
        },
        'contacts_and_people.personlite': {
            'Meta': {'object_name': 'PersonLite'},
            'given_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'middle_names': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts_and_people.Title']", 'to_field': "'abbreviation'", 'null': 'True', 'blank': 'True'})
        },
        'contacts_and_people.phonecontact': {
            'Meta': {'object_name': 'PhoneContact'},
            'area_code': ('django.db.models.fields.CharField', [], {'default': "'029'", 'max_length': '5'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'country_code': ('django.db.models.fields.CharField', [], {'default': "'44'", 'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_extension': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'contacts_and_people.site': {
            'Meta': {'object_name': 'Site'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_town': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True'})
        },
        'contacts_and_people.title': {
            'Meta': {'object_name': 'Title'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_file_type_plugin_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'all_files'", 'blank': 'True', 'null': 'True', 'to': "orm['filer.Folder']"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_files'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.folder': {
            'Meta': {'unique_together': "(('parent', 'name'),)", 'object_name': 'Folder'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'filer_owned_folders'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'blank': 'True', 'null': 'True', 'to': "orm['filer.Folder']"}),
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
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'links.externallink': {
            'Meta': {'object_name': 'ExternalLink'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'external_site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'blank': 'True', 'null': 'True', 'to': "orm['links.ExternalSite']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'blank': 'True', 'null': 'True', 'to': "orm['links.LinkType']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'links.externalsite': {
            'Meta': {'object_name': 'ExternalSite'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'blank': 'True', 'null': 'True', 'to': "orm['links.ExternalSite']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'site': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'links.linktype': {
            'Meta': {'object_name': 'LinkType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'scheme': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True'})
        },
        'news_and_events.event': {
            'Meta': {'object_name': 'Event'},
            'access_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'always_display_series': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'body': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts_and_people.Building']", 'null': 'True', 'blank': 'True'}),
            'child_list_heading': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'do_not_advertise_children': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'enquiries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'event_person'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Person']"}),
            'external_url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_item'", 'blank': 'True', 'null': 'True', 'to': "orm['links.ExternalLink']"}),
            'hosted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_hosted_events'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'importance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True'}),
            'inherit_name': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'jumps_queue_everywhere': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'jumps_queue_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'no_direct_access_to_children': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'organisers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'event_organiser'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Person']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'blank': 'True', 'null': 'True', 'to': "orm['news_and_events.Event']"}),
            'precise_location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'publish_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['contacts_and_people.Entity']", 'symmetrical': 'False', 'null': 'True', 'blank': 'True'}),
            'registration_enquiries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'event_registration'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Person']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'series': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'single_day_event': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '60', 'unique': 'True', 'blank': 'True'}),
            'speakers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'event_speaker'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Person']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.TextField', [], {'max_length': '256', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news_and_events.EventType']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'news_and_events.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'news_and_events.newsandeventsplugin': {
            'Meta': {'object_name': 'NewsAndEventsPlugin', 'db_table': "'cmsplugin_newsandeventsplugin'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'display': ('django.db.models.fields.CharField', [], {'default': "'news_and_events'", 'max_length': '25'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'news_events_plugin'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'events_heading_text': ('django.db.models.fields.CharField', [], {'default': "'Events'", 'max_length': '25'}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'title'", 'max_length': '25'}),
            'heading_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'}),
            'layout': ('django.db.models.fields.CharField', [], {'default': "'sidebyside'", 'max_length': '25'}),
            'limit_to': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'}),
            'news_heading_text': ('django.db.models.fields.CharField', [], {'default': "'News'", 'max_length': '25'}),
            'order_by': ('django.db.models.fields.CharField', [], {'default': "'date'", 'max_length': '25'}),
            'show_previous_events': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'news_and_events.newsarticle': {
            'Meta': {'object_name': 'NewsArticle'},
            'body': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'display_indefinitely': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enquiries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'newsarticle_person'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Person']"}),
            'external_news_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news_and_events.NewsSource']", 'null': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'newsarticle_item'", 'blank': 'True', 'null': 'True', 'to': "orm['links.ExternalLink']"}),
            'hosted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'newsarticle_hosted_events'", 'blank': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'importance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True'}),
            'is_sticky_everywhere': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'publish_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['contacts_and_people.Entity']", 'symmetrical': 'False', 'null': 'True', 'blank': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '60', 'unique': 'True', 'blank': 'True'}),
            'sticky_until': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.TextField', [], {'max_length': '256', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'news_and_events.newssource': {
            'Meta': {'object_name': 'NewsSource'},
            'external_news_source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'sites.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['news_and_events']
