from django.db import models
from django.db.models import ForeignKey
from django.conf import settings
from django import forms

from cms.utils import cms_static_url

from widgetry import fk_lookup

from links.models import ExternalLink
from links.link_functions import object_links


class AutocompleteMixin(object):
    class Media:
        js = [
            # '/static/jquery/jquery.js',
            settings.ADMIN_MEDIA_PREFIX + 'js/jquery.min.js',
            cms_static_url('js/libs/jquery.ui.core.js'),
        ]
        css = {
            'all': ('/static/jquery/themes/base/ui.all.css',)
        }    

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if (isinstance(db_field, ForeignKey) and 
                db_field.name in self.related_search_fields):
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)          
        return super(AutocompleteMixin, self).formfield_for_dbfield(db_field, **kwargs)


class SupplyRequestMixin(object):
    def get_form(self, request, obj=None, **kwargs):
        form_class = super(SupplyRequestMixin, self).get_form(request, obj, **kwargs)
        form_class.request = request
        return form_class

class InputURLMixin(forms.ModelForm):
    input_url = forms.CharField(max_length=255, required = False,
        help_text=u"Enter the URL of an external item that you want <strong>automatically</strong> added to the database, but first check carefully using <strong>External URL</strong> (above) to make sure it's really not there.", 
        )
        

class URLModelMixin(models.Model):
    class Meta:
        abstract = True

    # url fields
    url = models.URLField(null=True, blank=True, verify_exists=True, 
        help_text=u"To be used <strong>only</strong> for external items. Use with caution!")
    external_url = models.ForeignKey(ExternalLink, related_name="%(class)s_item", blank=True, null=True,
        help_text=u"Select an item from the External Links database."
        )                              
    slug = models.SlugField(unique=True, max_length=60, blank=True, help_text=u"Do not meddle with this unless you know exactly what you're doing!", error_messages={"unique": "unique"})

    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/%s/%s/" % (self.url_path, self.slug)


class LocationModelMixin(models.Model):
    class Meta:
        abstract = True
    # location fields
    precise_location = models.CharField(help_text=u"Precise location <em>within</em> the building, for visitors",
        max_length=255, null=True, blank=True)
    access_note = models.CharField(help_text = u"Notes on access/visiting hours/etc",
        max_length=255, null=True, blank=True)
        
fieldsets = {
    'basic': ('', {'fields': ('title',  'short_title', 'summary')}),
    'host': ('', {'fields': ('hosted_by',)}),
    'image': ('', {'fields': ('image',)}),
    'body':  ('', {
        'fields': ('body',),
        'classes': ('plugin-holder', 'plugin-holder-nopage',)
        }),
    'where_to_publish': ('', {'fields': ('publish_to',)}),
    'people': ('People to contact about this item', {'fields': ('please_contact',)}),
    'publishing_control': ('Publishing control', {'fields': ('published', 'in_lists')}),
    'date': ('', {'fields': ('date',)}),
    'closing_date': ('', {'fields': ('closing_date',)}),
    'importance': ('', {'fields': ('importance',)}),
    'url': ('If this is an external item', {'fields': ('external_url', 'input_url',)}),         
    'slug': ('If this is an internal item', {'fields': ('slug',)}),
    'location': ('', {'fields': ('precise_location', 'access_note',)}),
    'email': ('', {'fields': ('email',)}),
    }