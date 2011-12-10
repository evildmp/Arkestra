from django.utils.translation import ugettext_lazy as _
from django.db import models
from cms.models import CMSPlugin, Page
from cms.models.fields import PageField
from django.utils.translation import ugettext_lazy as _
from posixpath import join, basename, splitext, exists
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField
from cms import settings as cms_settings
from django.conf import settings

class FilerImage(CMSPlugin):
    LEFT = "left"
    RIGHT = "right"
    image = FilerImageField()
    IMAGE_WIDTHS = (
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
        (u'Absolute widths', (
            (-50.0, u'50 pixels square, cropped'),
            (-175.0, u'175 pixels'),
            (-350.0, u'350 pixels'),
            )
        ),    
        ('', u"Image's native width"),
    )
    width = models.FloatField(null=True, blank=True, choices = IMAGE_WIDTHS, default = 1000.0)
    height = models.PositiveIntegerField(null=True, blank=True)
    ASPECT_RATIOS = (
        (0, u'Native'),
        (1.5, u'3x2'),
        (1.333, u'4x3'),
        (1.0, u'Square'),
        (.75, u'3x4'),
        (.667, u'2x3'),
        (.3, u'1x3'),
        (3.0, u'3x1'),
        )
    aspect_ratio = models.FloatField(null=True, choices = ASPECT_RATIOS, default = 0)
    alt_text = models.CharField(null=True, blank=True, max_length=255)
    use_description_as_caption = models.BooleanField(verbose_name = "Show caption", default=False, help_text = "Use image's description field as caption; override using <em>Caption</em> field below")
    caption = models.TextField(_("Caption"), blank=True, null=True)
    use_autoscale = models.BooleanField(_("use automatic scaling"), default=False, 
                                        help_text=_('tries to auto scale the image based on the placeholder context'))
    FLOAT_CHOICES = ((LEFT, _("left")),
                     (RIGHT, _("right")),
                     )
    float = models.CharField(_("float"), max_length=10, blank=True, null=True, choices=FLOAT_CHOICES)
    
    '''
    @property
    def scaled_image_url(self):
        h = self.height or self.image.width
        w = self.width or self.image.height
        tn = unicode(DjangoThumbnail(self.image.file, (w,h), opts=['crop','upscale'] ))
        return tn
    '''
    def __unicode__(self):
        if self.image:
            return self.image.label
        else:
            return u"Image Publication %s" % self.caption
        return ''
    @property
    def alt(self): 
        return self.alt_text
    @property
    def link(self):
        if self.free_link:
            return self.free_link
        elif self.page_link and self.page_link:
            return self.page_link.get_absolute_url()
        else:
            return ''

class ImageSetPlugin(CMSPlugin):
    IMAGESET_KINDS = (
        ("basic", "Basic"),
        ("lightbox", "LightBox"),
        ("slider", "Slider"),
        )
    kind = models.CharField(choices = IMAGESET_KINDS, max_length = 50, default = "basic")
    IMAGE_WIDTHS = (
        (1000.0, u"Automatic"),
        (u'Relative to column', (
            (100.0, u"100%"),
            (75.0, u"75%"),
            (66.7, u"66%"),
            (50.0, u"50%"),
            (33.3, u"33%"),
            (25.0, u"25%"),
            )
        ),
        (u'Absolute widths', (
            (-50.0, u'50 pixels square'),
            (-175.0, u'175 pixels'),
            (-350.0, u'350 pixels'),
            )
        ),    
        ('', u"Image's native width"),
    )
    width = models.FloatField(null=True, blank=True, choices = IMAGE_WIDTHS, default = 1000.0)
    height = models.PositiveIntegerField(null=True, blank=True)
    ASPECT_RATIOS = (
        (0, u'Native'),
        (3.0, u'3x1'),
        (1.778, u'16x9'),
        (1.618, u'Golden ratio (horizonal)'),
        (1.5, u'3x2'),
        (1.333, u'4x3'),
        (1.0, u'Square'),
        (.75, u'3x4'),
        (.667, u'2x3'),
        (0.618, u'Golden ratio (vertical)'),
        (0.563, u'16x9'),
        (0.3, u'1x3'),
        )
    aspect_ratio = models.FloatField(null=True, choices = ASPECT_RATIOS, default = 0)
    LEFT = "left"
    RIGHT = "right"
    FLOAT_CHOICES = ((LEFT, _("left")),
                     (RIGHT, _("right")),
                     )
    float = models.CharField(_("float"), max_length=10, blank=True, null=True, choices=FLOAT_CHOICES)
    def __unicode__(self):
        return u"image-set-%s" % self.kind
    

class ImageSetItem(models.Model):
    plugin = models.ForeignKey(ImageSetPlugin, related_name="imageset_item")
    image = FilerImageField()
    alt_text = models.CharField(null=True, blank=True, max_length=255)
    use_description_as_caption = models.BooleanField(verbose_name = "Use description", default=False, help_text = "Use image's description field as caption")
    caption = models.TextField(_("Caption"), blank=True, null=True)

    def __unicode__(self):
        if self.image:
            return self.image.label
        else:
            return u"Image Publication %s" % self.caption
        return ''

    @property
    def alt(self): 
        return self.alt_text
