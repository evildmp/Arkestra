from django.db import models
from django.db.models import ForeignKey
from django.conf import settings

from cms.models.fields import PlaceholderField
from cms.utils import cms_static_url

from filer.fields.image import FilerImageField

from widgetry import fk_lookup

from contacts_and_people.models import Entity, Person, default_entity_id

from links.models import ExternalLink
from links.link_functions import object_links


class AutocompleteMixin(object):
    class Media:
        js = [
            '/static/jquery/jquery.js',
            # settings.ADMIN_MEDIA_PREFIX + 'js/jquery.min.js',
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

        
class UniversalPluginModelMixin(models.Model):
    class Meta:
        abstract = True

    # core fields
    title = models.CharField(max_length=255,
        help_text="e.g. Outrage as man bites dog in unprovoked attack")
    short_title = models.CharField(max_length=255,  null=True, blank=True,
        help_text= u"e.g. Man bites dog (if left blank, will be copied from Title)")
    summary = models.TextField(verbose_name="Summary",
        null=False, blank=False, 
        help_text="e.g. Cardiff man arrested in latest wave of man-on-dog violence (maximum two lines)",)
    body = PlaceholderField('body', help_text="Not used or required for external items")    
    image = FilerImageField(null=True, blank=True)

    # universal plugin fields 
    hosted_by = models.ForeignKey(Entity, default=default_entity_id,
        related_name='%(class)s_hosted_events', null=True, blank=True,
        help_text=u"The entity responsible for publishing this item")
    publish_to = models.ManyToManyField(Entity, null=True, blank=True, related_name="%(class)s_publish_to",
        help_text=u"Use these sensibly - don't send minor items to the home page, for example")
    # though in fact the .save() and the admin between them won't allow null = True
    please_contact = models.ManyToManyField(Person, related_name='%(class)s_person', 
        help_text=u'The person to whom enquiries about this should be directed ', 
        null=True, blank=True)
    IMPORTANCES = (
        (0, u"Normal"),
        (1, u"More important"),
        (10, u"Most important"),
    )
    importance = models.PositiveIntegerField(null=True, blank=False,
        default=0, choices=IMPORTANCES,
        help_text=u"Important items will be featured in lists")

    def get_importance(self):
        if self.importance: # if they are not being gathered together, mark them as important
            return "important"
        else:
            return ""

    @property
    def links(self):
        return object_links(self)

    @property
    def external_url(self):
        # if the inheriting model doesn't have an external_url attribute, we'll give it a None one just in case this is needed
        return None
    
    @property
    def is_uninformative(self):
        if self.external_url or self.body.cmsplugin_set.all() or self.please_contact.all() or self.links:
            return False
        else:
            return True


class URLModelMixin(models.Model):
    class Meta:
        abstract = True

    # url fields
    url = models.URLField(null=True, blank=True, verify_exists=True, 
        help_text=u"To be used <strong>only</strong> for external items. Use with caution!")
    external_url = models.ForeignKey(ExternalLink, related_name="%(class)s_item", blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=60, blank=True, help_text=u"Do not meddle with this unless you know exactly what you're doing!")

    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/%s/%s/" % (self.url_path, self.slug)


class LocationModelMixin(object):
    # location fields
    precise_location = models.CharField(help_text=u"Precise location <em>within</em> the building, for visitors",
        max_length=255, null=True, blank=True)
    access_note = models.CharField(help_text = u"Notes on access/visiting hours/etc",
        max_length=255, null=True, blank=True)