# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Site'
        db.create_table('contacts_and_people_site', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('post_town', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal('contacts_and_people', ['Site'])

        # Adding model 'Building'
        db.create_table('contacts_and_people_building', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('additional_street_address', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts_and_people.Site'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=255, unique=True, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'], null=True, blank=True)),
            ('summary', self.gf('django.db.models.fields.TextField')(default='', max_length=256)),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(related_name='building_description', null=True, to=orm['cms.Placeholder'])),
            ('getting_here', self.gf('django.db.models.fields.related.ForeignKey')(related_name='getting_here', null=True, to=orm['cms.Placeholder'])),
            ('access_and_parking', self.gf('django.db.models.fields.related.ForeignKey')(related_name='building_access_and_parking', null=True, to=orm['cms.Placeholder'])),
            ('map', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('zoom', self.gf('django.db.models.fields.IntegerField')(default=17, null=True, blank=True)),
        ))
        db.send_create_signal('contacts_and_people', ['Building'])

        # Adding model 'PhoneContact'
        db.create_table('contacts_and_people_phonecontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(default='44', max_length=5)),
            ('area_code', self.gf('django.db.models.fields.CharField')(default='029', max_length=5)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('internal_extension', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal('contacts_and_people', ['PhoneContact'])

        # Adding model 'EntityLite'
        db.create_table('contacts_and_people_entitylite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('contacts_and_people', ['EntityLite'])

        # Adding model 'Entity'
        db.create_table('contacts_and_people_entity', (
            ('entitylite_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['contacts_and_people.EntityLite'], unique=True, primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('external_url', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entity_item', null=True, to=orm['links.ExternalLink'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=60, blank=True)),
            ('precise_location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('access_note', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'], null=True, blank=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('abstract_entity', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['contacts_and_people.Entity'])),
            ('display_parent', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('building_recapitulates_entity_name', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts_and_people.Building'], null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entity', unique=True, null=True, to=orm['cms.Page'])),
            ('auto_news_page', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('news_page_menu_title', self.gf('django.db.models.fields.CharField')(default='News & events', max_length=50)),
            ('news_page_intro', self.gf('django.db.models.fields.related.ForeignKey')(related_name='news_page_intro', null=True, to=orm['cms.Placeholder'])),
            ('auto_contacts_page', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contacts_page_menu_title', self.gf('django.db.models.fields.CharField')(default='Contacts & people', max_length=50)),
            ('contacts_page_intro', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contacts_page_intro', null=True, to=orm['cms.Placeholder'])),
            ('auto_vacancies_page', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('vacancies_page_menu_title', self.gf('django.db.models.fields.CharField')(default='Vacancies & studentships', max_length=50)),
            ('vacancies_page_intro', self.gf('django.db.models.fields.related.ForeignKey')(related_name='vacancies_page_intro', null=True, to=orm['cms.Placeholder'])),
            ('auto_publications_page', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publications_page_menu_title', self.gf('django.db.models.fields.CharField')(default='Publications', max_length=50)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('contacts_and_people', ['Entity'])

        # Adding model 'Title'
        db.create_table('contacts_and_people_title', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal('contacts_and_people', ['Title'])

        # Adding model 'PersonLite'
        db.create_table('contacts_and_people_personlite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts_and_people.Title'], to_field='abbreviation', null=True, blank=True)),
            ('given_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('middle_names', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('contacts_and_people', ['PersonLite'])

        # Adding model 'Person'
        db.create_table('contacts_and_people_person', (
            ('personlite_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['contacts_and_people.PersonLite'], unique=True, primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('external_url', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='person_item', null=True, to=orm['links.ExternalLink'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=60, blank=True)),
            ('precise_location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('access_note', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='person_user', unique=True, null=True, to=orm['auth.User'])),
            ('institutional_username', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Placeholder'], null=True)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts_and_people.Building'], null=True, blank=True)),
            ('override_entity', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='people_override', null=True, to=orm['contacts_and_people.Entity'])),
            ('please_contact', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='contact_for', null=True, to=orm['contacts_and_people.Person'])),
            ('staff_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('data_feed_locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('contacts_and_people', ['Person'])

        # Adding model 'Teacher'
        db.create_table('contacts_and_people_teacher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='teacher', unique=True, null=True, to=orm['contacts_and_people.Person'])),
            ('dummy_field_one', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('dummy_field_two', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('contacts_and_people', ['Teacher'])

        # Adding model 'Membership'
        db.create_table('contacts_and_people_membership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='member_of', to=orm['contacts_and_people.Person'])),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['contacts_and_people.Entity'])),
            ('display_role', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='display_roles', null=True, to=orm['contacts_and_people.Membership'])),
            ('key_contact', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('importance_to_person', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('importance_to_entity', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
        ))
        db.send_create_signal('contacts_and_people', ['Membership'])

        # Adding model 'EntityAutoPageLinkPluginEditor'
        db.create_table('cmsplugin_entityautopagelinkplugineditor', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('link_to', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='auto_page_plugin', null=True, to=orm['contacts_and_people.Entity'])),
            ('text_override', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('contacts_and_people', ['EntityAutoPageLinkPluginEditor'])

        # Adding model 'EntityDirectoryPluginEditor'
        db.create_table('cmsplugin_entitydirectoryplugineditor', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='directory_plugin', null=True, to=orm['contacts_and_people.Entity'])),
            ('levels', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('display_descriptions_to_level', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, null=True, blank=True)),
            ('link_icons', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('use_short_names', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('contacts_and_people', ['EntityDirectoryPluginEditor'])

        # Adding model 'EntityMembersPluginEditor'
        db.create_table('cmsplugin_entitymembersplugineditor', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entity_members_plugin', null=True, to=orm['contacts_and_people.Entity'])),
        ))
        db.send_create_signal('contacts_and_people', ['EntityMembersPluginEditor'])


    def backwards(self, orm):
        
        # Deleting model 'Site'
        db.delete_table('contacts_and_people_site')

        # Deleting model 'Building'
        db.delete_table('contacts_and_people_building')

        # Deleting model 'PhoneContact'
        db.delete_table('contacts_and_people_phonecontact')

        # Deleting model 'EntityLite'
        db.delete_table('contacts_and_people_entitylite')

        # Deleting model 'Entity'
        db.delete_table('contacts_and_people_entity')

        # Deleting model 'Title'
        db.delete_table('contacts_and_people_title')

        # Deleting model 'PersonLite'
        db.delete_table('contacts_and_people_personlite')

        # Deleting model 'Person'
        db.delete_table('contacts_and_people_person')

        # Deleting model 'Teacher'
        db.delete_table('contacts_and_people_teacher')

        # Deleting model 'Membership'
        db.delete_table('contacts_and_people_membership')

        # Deleting model 'EntityAutoPageLinkPluginEditor'
        db.delete_table('cmsplugin_entityautopagelinkplugineditor')

        # Deleting model 'EntityDirectoryPluginEditor'
        db.delete_table('cmsplugin_entitydirectoryplugineditor')

        # Deleting model 'EntityMembersPluginEditor'
        db.delete_table('cmsplugin_entitymembersplugineditor')


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
            'Meta': {'ordering': "('site', 'tree_id', 'lft')", 'object_name': 'Page'},
            'changed_by': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'limit_visibility_in_menu': ('django.db.models.fields.SmallIntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'moderator_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'blank': 'True'}),
            'navigation_extenders': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'page_flags': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['cms.Page']"}),
            'placeholders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cms.Placeholder']", 'symmetrical': 'False'}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'publication_end_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publisher_is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'publisher_public': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'publisher_draft'", 'unique': 'True', 'null': 'True', 'to': "orm['cms.Page']"}),
            'publisher_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'reverse_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'soft_root': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
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
            'Meta': {'ordering': "('site', 'street', 'number', 'name')", 'object_name': 'Building'},
            'access_and_parking': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'building_access_and_parking'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'additional_street_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'building_description'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'getting_here': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'getting_here'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'map': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts_and_people.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '256'}),
            'zoom': ('django.db.models.fields.IntegerField', [], {'default': '17', 'null': 'True', 'blank': 'True'})
        },
        'contacts_and_people.entity': {
            'Meta': {'ordering': "['tree_id', 'lft']", 'object_name': 'Entity', '_ormbases': ['contacts_and_people.EntityLite']},
            'abstract_entity': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'access_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'auto_contacts_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_news_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_publications_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_vacancies_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts_and_people.Building']", 'null': 'True', 'blank': 'True'}),
            'building_recapitulates_entity_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contacts_page_intro': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts_page_intro'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'contacts_page_menu_title': ('django.db.models.fields.CharField', [], {'default': "'Contacts & people'", 'max_length': '50'}),
            'display_parent': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'entitylite_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['contacts_and_people.EntityLite']", 'unique': 'True', 'primary_key': 'True'}),
            'external_url': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity_item'", 'null': 'True', 'to': "orm['links.ExternalLink']"}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'news_page_intro': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'news_page_intro'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'news_page_menu_title': ('django.db.models.fields.CharField', [], {'default': "'News & events'", 'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'precise_location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'publications_page_menu_title': ('django.db.models.fields.CharField', [], {'default': "'Publications'", 'max_length': '50'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '60', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'vacancies_page_intro': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vacancies_page_intro'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'vacancies_page_menu_title': ('django.db.models.fields.CharField', [], {'default': "'Vacancies & studentships'", 'max_length': '50'}),
            'website': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity'", 'unique': 'True', 'null': 'True', 'to': "orm['cms.Page']"})
        },
        'contacts_and_people.entityautopagelinkplugineditor': {
            'Meta': {'object_name': 'EntityAutoPageLinkPluginEditor', 'db_table': "'cmsplugin_entityautopagelinkplugineditor'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'auto_page_plugin'", 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'link_to': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'text_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'contacts_and_people.entitydirectoryplugineditor': {
            'Meta': {'object_name': 'EntityDirectoryPluginEditor', 'db_table': "'cmsplugin_entitydirectoryplugineditor'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'display_descriptions_to_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'directory_plugin'", 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'levels': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'link_icons': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'use_short_names': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'contacts_and_people.entitylite': {
            'Meta': {'object_name': 'EntityLite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contacts_and_people.entitymembersplugineditor': {
            'Meta': {'object_name': 'EntityMembersPluginEditor', 'db_table': "'cmsplugin_entitymembersplugineditor'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity_members_plugin'", 'null': 'True', 'to': "orm['contacts_and_people.Entity']"})
        },
        'contacts_and_people.membership': {
            'Meta': {'ordering': "('-importance_to_entity', 'person__surname')", 'object_name': 'Membership'},
            'display_role': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'display_roles'", 'null': 'True', 'to': "orm['contacts_and_people.Membership']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['contacts_and_people.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance_to_entity': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'importance_to_person': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'key_contact': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'member_of'", 'to': "orm['contacts_and_people.Person']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'contacts_and_people.person': {
            'Meta': {'ordering': "['surname', 'given_name', 'user']", 'object_name': 'Person', '_ormbases': ['contacts_and_people.PersonLite']},
            'access_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts_and_people.Building']", 'null': 'True', 'blank': 'True'}),
            'data_feed_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'entities': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'people'", 'to': "orm['contacts_and_people.Entity']", 'through': "orm['contacts_and_people.Membership']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'external_url': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'person_item'", 'null': 'True', 'to': "orm['links.ExternalLink']"}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'institutional_username': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'override_entity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'people_override'", 'null': 'True', 'to': "orm['contacts_and_people.Entity']"}),
            'personlite_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['contacts_and_people.PersonLite']", 'unique': 'True', 'primary_key': 'True'}),
            'please_contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contact_for'", 'null': 'True', 'to': "orm['contacts_and_people.Person']"}),
            'precise_location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '60', 'blank': 'True'}),
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
            'Meta': {'ordering': "('label',)", 'object_name': 'PhoneContact'},
            'area_code': ('django.db.models.fields.CharField', [], {'default': "'029'", 'max_length': '5'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'country_code': ('django.db.models.fields.CharField', [], {'default': "'44'", 'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_extension': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'contacts_and_people.site': {
            'Meta': {'ordering': "('country', 'site_name', 'post_town')", 'object_name': 'Site'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_town': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'contacts_and_people.teacher': {
            'Meta': {'object_name': 'Teacher'},
            'dummy_field_one': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'dummy_field_two': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'teacher'", 'unique': 'True', 'null': 'True', 'to': "orm['contacts_and_people.Person']"})
        },
        'contacts_and_people.title': {
            'Meta': {'ordering': "['title']", 'object_name': 'Title'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
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
        },
        'links.externallink': {
            'Meta': {'ordering': "['title']", 'object_name': 'ExternalLink'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'external_site': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'to': "orm['links.ExternalSite']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'to': "orm['links.LinkType']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'links.externalsite': {
            'Meta': {'ordering': "['site']", 'object_name': 'ExternalSite'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['links.ExternalSite']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'site': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'links.linktype': {
            'Meta': {'object_name': 'LinkType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'scheme': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['contacts_and_people']
