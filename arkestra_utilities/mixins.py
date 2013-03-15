from django.db import models
from django.core.urlresolvers import reverse
from links.models import ExternalLink     
        

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
        elif self.url_path in ["news","event","vacancy","studentship"]:
            return reverse(self.url_path,kwargs={"slug":self.slug})
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
        

