from django.db import models
from django.core.urlresolvers import reverse

from links.models import ExternalLink


class URLModelMixin(models.Model):
    # for models that can have external (hosted elsewhere) items
    class Meta:
        abstract = True

    # sublasses *must* be provided with a view_name attribute

    # url fields
    external_url = models.ForeignKey(
        ExternalLink,
        related_name="%(class)s_item",
        on_delete=models.PROTECT,
        blank=True, null=True,
        help_text=u"Select an item from the External Links database."
        )
    slug = models.SlugField(
        unique=True, max_length=60, blank=True,
        help_text=u"""
        Do not meddle with this unless you know exactly what you're doing!
        """,
        error_messages={"unique": "unique"}
        )

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return reverse(self.view_name, kwargs={"slug": self.slug})


class LocationModelMixin(models.Model):
    # provides location fields, for people, contacts, events, etc
    class Meta:
        abstract = True
    precise_location = models.CharField(
        help_text=u"Location <em>within</em> the building, for visitors",
        max_length=255, null=True, blank=True
        )
    access_note = models.CharField(
        help_text=u"Notes on access/visiting hours/etc",
        max_length=255, null=True, blank=True
        )
