from django.utils.translation import ugettext_lazy as _
from django.db import models
from cms.models import CMSPlugin, Page
from django.utils.translation import ugettext_lazy as _
from posixpath import join, basename, splitext, exists
from filer.fields.image import FilerImageField
from filer.fields.video import FilerVideoField
from cms import settings as cms_settings
from django.conf import settings

class FilerVideoEditor(CMSPlugin):
    LEFT = "left"
    RIGHT = "right"
    FLOAT_CHOICES = ((LEFT, _("left")),
                     (RIGHT, _("right")),
                     )
    video = FilerVideoField()
    #   added for cardiff template calculations
    VIDEO_WIDTHS = (
        (1000.0, u"Automatic"),
        (u'Widths relative to the containing column', (
            (100.0, u"100%"),
            (75.0, u"75%"),
            (66.7, u"66%"),
            (50.0, u"50%"),
            (33.3, u"33%"),
            (25.0, u"25%"),
            )
        ),
        ('', u"Video's native width - on your head be it"),
    )
    width = models.FloatField(null=True, blank=True, choices = VIDEO_WIDTHS, default = 1000.0)
    wait = models.BooleanField(default=False) # not implemented yet - will make the plugin wait until all the video files are OK and present before rendering anything

#   end of cardiff amendments
    use_description_as_caption = models.BooleanField(verbose_name = "Use description", default=False, help_text = "Use image's description field as caption")
    caption = models.TextField(_("Caption"), blank=True, null=True)
    float = models.CharField(_("float"), max_length=10, blank=True, null=True, choices=FLOAT_CHOICES)
    
    def __unicode__(self):
        if self.video:
            return self.video.label
        else:
            return u"Video %s" % self.caption
        return ''
        
class VideoVersion(models.Model):
    source = FilerVideoField()
    status = models.CharField(max_length=10, blank=True, null=True,)
