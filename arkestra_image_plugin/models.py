from posixpath import join, basename, splitext, exists

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin

from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField

from arkestra_utilities.import_free_model_mixins import ArkestraGenericPluginItemOrdering
from arkestra_utilities.settings import VIDEO_HOSTING_SERVICES
from arkestra_utilities.output_libraries.plugin_widths import get_placeholder_width, calculate_container_width

from links.models import LinkMethodsMixin

from arkestra_utilities.settings import IMAGESET_ITEM_PADDING, LIGHTBOX_COLUMNS


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
        ('0', u"Image's native width"),
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

class ImageSetTypePluginMixin(object):

    def width_of_image_container(self, context):
        # Based on the plugin settings and placeholder width, calculate image container width
    
        # work out native image aspect ratio
        self.has_borders = False
    
        # width values
        # None:     use native width
        # <0:       an absolute value
        # <=100:    a percentage of placeholder's width
        # 1000:     automatic, based on placeholder's width
    
        placeholder_width = get_placeholder_width(context, self)

        if self.width > 0 and self.width <= 100:
            width = placeholder_width/100.0 * self.width
            auto = False
        else:
            width = placeholder_width
            auto = True
        
        # calculate the width of the block the image will be in
        width = calculate_container_width(context, self, width, auto)
    
        # return the width of the container
        # print "width_of_image_container", width
        return width

    def shave_if_floated(plugin, width):
        # shave off 5 point if the image is floated, to make room for a margin
        # see arkestra.css, span.image.left and span.image.right
        if plugin.float and plugin.width > 0:
            # print "-5 for float"
                return width - 5

    def calculate_height(self, width, aspect_ratio):
        # given_width, given_height, given_aspect_ratio are values set by the plugin
        # width and aspect_ratio are calculated values
        # using given values gives us a chance to use given values to override calculated ones 
       
        # rules:
        # if the instance has an aspect ratio, use that to calculate the height
        # if the instance has no aspect ratio, but does have a height, use the height
        # if the instance has no aspect ratio, we use the native aspect ratio

        # has aspect ratio
        # print  given_aspect_ratio
    
        if self.aspect_ratio == -1:
            height=width/aspect_ratio 
        elif self.aspect_ratio: 
            height = width / self.aspect_ratio
            # if the instance has no width, but does have a height, use the aspect ratio to calculate it
            if self.height and not self.width: 
                width = height * self.aspect_ratio
        # has height
        elif self.height: 
            height = self.height
            # if it had no width either, we can use the native aspect ratio to calculate that
            if not self.width: 
                width = aspect_ratio * height
        # use the native aspect ratio
        else:
            height = width / aspect_ratio
        
        return width, height

class ImageSetPlugin(CMSPlugin, ImageSetTypePluginMixin):
    IMAGESET_KINDS = (
        ("basic", "Basic"),
        ("multiple", "Multiple images"),
        ("lightbox", "Lightbox with gallery"),
        ("lightbox-single", "Lightbox"),
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
            (-50.0, u'50 x 50'),
            (-175.0, u'175 pixels'),
            (-350.0, u'350 pixels'),
            )
        ),    
        (0.0, u"Native"),
    )
    width = models.FloatField(choices = IMAGE_WIDTHS, default = 1000.0)
    height = models.PositiveIntegerField(null=True, blank=True,
        help_text = "Only applies when <strong>Aspect ratio</strong> is <em>Automatic</em>")

    ASPECT_RATIOS = (
        (0, u'Automatic'),
        (3.0, u'3x1'),
        (1.778, u'16x9'),
        (1.618, u'Golden ratio (horizontal)'),
        (1.5, u'3x2'),
        (1.333, u'4x3'),
        (1.0, u'Square'),
        (.75, u'3x4'),
        (.667, u'2x3'),
        (0.618, u'Golden ratio (vertical)'),
        (0.563, u'16x9'),
        (0.3, u'1x3'),
        (-1.0, u'Force native'),
        )
    aspect_ratio = models.FloatField(null=True, choices = ASPECT_RATIOS, default = 0,          
        help_text = "<em>Automatic</em>: native aspect ratio if possible, calculated otherwise")

    LEFT = "left"
    RIGHT = "right"
    FLOAT_CHOICES = ((LEFT, _("left")),
                     (RIGHT, _("right")),
                     )
    float = models.CharField(_("float"), max_length=10, blank=True, null=True, choices=FLOAT_CHOICES)
    items_per_row = models.PositiveSmallIntegerField(blank = True, null = True,
        help_text = "Only applies to Multiple and Lightbox plugins")

    @property
    def items_have_links(self):
        return all(item.destination_content_object is not None for item in self.imageset_item.all())

    @property
    def active_items(self):
        return self.imageset_item.active_items()      
        
    def calculate_aspect_ratio(self, item_list):
        return sum(
            [float(
                item.image.width)/item.image.height for item in item_list]
            )/len(item_list)

    def width_of_image(self, image=None):
        # no plugin width? 
        if not self.width:
            if image:
                # print "image", image
                # use native image width
                width = image.width
            else:
                # use container width
                width = self.container_width
        # negative numbers are absolutes
        elif self.width < 0:
            width = -self.width   
        else:
            width = self.container_width 
        return width

    def single_image(self):                 
        self.items = self.active_items
        self.template = "arkestra_image_plugin/single_image.html"
        # choose an image at random from the set
        self.item = self.items.order_by('?')[0]
        # calculate its native aspect ratio
        aspect_ratio = self.calculate_aspect_ratio([self.item.image])
        # get width 
        width = self.width_of_image(self.item.image)
        # shave if floated
        width = self.shave_if_floated(width) or width
        # calculate height 
        self.item.width, self.item.height = self.calculate_height(width, aspect_ratio)
        self.item.width, self.item.height = int(self.item.width), int(self.item.height)    
        self.item.caption_width = self.item.width
        
    def multiple_images(self):
        self.items = self.active_items

        # for lightboxes and multiple image sets
        self.template = "arkestra_image_plugin/%s.html" %self.kind
 
        self.padding = IMAGESET_ITEM_PADDING
        padding_adjuster = IMAGESET_ITEM_PADDING * 2
    
        # each item will be the same width - the user gets no say in this
        # also, let's not have any nonsense about using the native widths
        # - and only percentage and automatic widths are allowed
        # we call width_of_image() without an image argument 
        each_item_width = self.width_of_image()           

        # if self.aspect_ratio is 0 (auto) get an average and use that
        if self.aspect_ratio == 0 and not self.height:
            aspect_ratio = self.calculate_aspect_ratio(self.active_items)
        # otherwise use supplied aspect ratio
        else:
            aspect_ratio = self.aspect_ratio                             

        # don't allow more items_per_row than there are items
        if self.items_per_row > self.items.count():
            self.items_per_row = self.items.count()
    
        items_per_row = self.items_per_row or LIGHTBOX_COLUMNS.get(self.items.count(), 8) 

        # if we are using automatic/percentage widths, base them on the placeholder
        if self.width > 0: 
            each_item_width = each_item_width / items_per_row

        # fancybox icons and multiple images with links have padding, so:
        if self.kind == "lightbox" or self.items_have_links:
            each_item_width = each_item_width - padding_adjuster                   
        else: 
            # otherwise give them a margin
            if self.width > 0:
                each_item_width = each_item_width - (items_per_row-1) * padding_adjuster/items_per_row  

        # if self.aspect_ratio  is not -1 (forced native) calculate height/width for all
        if not self.aspect_ratio == -1:
            each_item_width, each_item_height = self.calculate_height(each_item_width, aspect_ratio)

        # set up each item
        # for counter, item in enumerate(self.items, start = 1): # enable this when we no longer need to support Python 2.5
        for counter, item in enumerate(self.items):
            counter=counter+1
            # mark end-of-row items in case the CSS needs it    
            # only when we are using percentage widths
            if self.width > 0 and not counter%items_per_row:
                item.lastinrow = True

            if self.aspect_ratio == -1:
                aspect_ratio = calculate_aspect_ratio(item.image) 
                item.width,item.height = self(each_item_width, aspect_ratio)
                item.width,item.height = int(item.width), int(item.height)
                # print item.width,item.height
            else:            
                item.width,item.height = int(each_item_width), int(each_item_height)
                # print item.width,item.height
            # item.image_size = u'%sx%s' %(item.width, item.height) 
            item.caption_width=item.width  
             
        # # if forced_native, set each individually
        # else:
        #     for counter, item in enumerate(self.items):
        #         counter=counter+1
        #         # mark end-of-row items in case the CSS needs it    
        #         # only when we are using percentage widths
        #         if self.width > 0 and not counter%items_per_row:
        #             item.lastinrow = True
        # 
        #         aspect_ratio = calculate_aspect_ratio(item.image)
        #         item.width,item.height = calculate_height(self.width, self.height, self.aspect_ratio, each_item_width, aspect_ratio)
        #         item.width,item.height = int(item.width), int(item.height)
        #         item.image_size = u'%sx%s' %(item.width, item.height) 
        #         item.caption_width=item.width   

    def lightbox_single(self):
        self.items = list(self.active_items)
        self.template = "arkestra_image_plugin/%s.html" %"lightbox"            
        self.padding = IMAGESET_ITEM_PADDING
        padding_adjuster = IMAGESET_ITEM_PADDING * 2
    
        # choose the first image from the set
        item = self.items[0]

        # calculate its native aspect ratio
        aspect_ratio = self.calculate_aspect_ratio([item])
        # get width
        width = self.width_of_image(item.image)        
        # shave if floated
        width = self.shave_if_floated(width) or width

        # fancybox icons  have padding, so:
        width = width - padding_adjuster
    
        # calculate height 
        item.width, item.height = self.calculate_height(width, aspect_ratio)

        # item.caption = set_image_caption(self.item)
        item.width,item.height = int(item.width), int(item.height)
        item.caption_width = item.width

    def slider(self):
        self.items = list(self.active_items)
        # loops over the items in the set, and calculates their sizes
        # for use in a slider
        imageset.template = "arkestra_image_plugin/slider.html"
        width = self.width_of_image()
        if self.aspect_ratio:
            height = self.container_width / self.aspect_ratio
        elif self.height:
            height = self.height    
        else:
            # use the aspect ratio of the widest image
            heights = []
            for item in self.items:
                divider = 1.0/float(item.image.width)
                height_multiplier = float(item.image.height)*divider
                heights.append(height_multiplier)
            
            heights.sort()
            height_multiplier = heights[0]
            height = width * height_multiplier
        self.size = (int(width),int(height))
        for item in self.items:
            item.image_size = self.size


    def __unicode__(self):
        return u"image-set-%s" % self.kind
    
    def copy_relations(self, oldinstance):
        for plugin_item in oldinstance.imageset_item.all():
            plugin_item.pk = None
            plugin_item.plugin = self
            plugin_item.save()



class ImageSetItem(ArkestraGenericPluginItemOrdering, LinkMethodsMixin, models.Model):
    class Meta:
        ordering=('inline_item_ordering', 'id',)
    plugin = models.ForeignKey(ImageSetPlugin, related_name="imageset_item")
    image = FilerImageField(on_delete=models.PROTECT)
    alt_text = models.CharField(null=True, blank=True, max_length=255,
        help_text = "The image's meaning, message or function (if any). Leave empty for items with links."
        )
    auto_image_title = models.BooleanField(_("Auto image title"), 
        default=False, 
        help_text = "Use the image's name field as a title")
    manual_image_title = models.TextField(_("Manual image title"), 
        blank=True, null=True)
    auto_image_caption = models.BooleanField(_("Auto image caption"), 
        default=False, 
        help_text = "Use the image's description field as caption")
    manual_image_caption = models.TextField(_("Manual image caption"), 
        blank=True, null=True)

    auto_link_title = models.BooleanField(_("Auto link title"), 
        default=False, 
        help_text = "Use the link destination's title")
    manual_link_title = models.TextField(_("Manual link title"), 
        blank=True, null=True)
    auto_link_description = models.BooleanField(_("Auto link description"), 
        default=False, 
        help_text = "Use the link destination's description metadata")
    manual_link_description = models.TextField(_("Manual link description"), 
        blank=True, null=True)

    destination_content_type = models.ForeignKey(ContentType, verbose_name="Type", related_name = "links_to_%(class)s", null = True, blank = True) 
    destination_object_id = models.PositiveIntegerField(verbose_name="Item", null = True, blank = True)
    destination_content_object = generic.GenericForeignKey('destination_content_type', 'destination_object_id')

    def __unicode__(self):
        if self.destination_object_id:
            return u"%s (links to: %s %s)" % (self.image.label, self.destination_content_type, self.destination_content_object)
        elif self.image:
            return self.image.label
        else:
            return u"Image Publication %s" % self.caption
        return ''

    @property
    def image_title(self):
        return self.manual_image_title or (self.auto_image_title and self.image.name)
        
    @property
    def image_caption(self):
        return self.manual_image_caption or (self.auto_image_caption and self.image.description)

    @property
    def link_title(self): 
        if self.plugin.items_have_links:
            return self.manual_link_title or (self.auto_link_title and self.text)

    @property
    def link_description(self): 
        if self.plugin.items_have_links:
            return self.manual_link_description or (self.auto_link_description and self.description)

    @property
    def alt(self): 
        if self.plugin.items_have_links:
            return self.alt_text or self.destination_content_object
        else: 
            return ""

    @property
    def image_size(self):
        return u'%sx%s' % (self.width, self.height)

                    
class EmbeddedVideoSetPlugin(CMSPlugin, ImageSetTypePluginMixin):
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
    )
    width = models.FloatField(choices = IMAGE_WIDTHS, default = 1000.0)

    @property
    def active_items(self):
        return self.embeddedvideoset_item.filter(active=True)

    def __unicode__(self):
        return u"embedded-video-set-%s" % self.id
    
    def copy_relations(self, oldinstance):
        for plugin_item in oldinstance.embeddedvideoset_item.all():
            plugin_item.pk = None
            plugin_item.plugin = self
            plugin_item.save()

class EmbeddedVideoSetItem(LinkMethodsMixin, ArkestraGenericPluginItemOrdering):
    class Meta:
        ordering=('inline_item_ordering', 'id',)
    plugin = models.ForeignKey(
        EmbeddedVideoSetPlugin, 
        related_name="embeddedvideoset_item"
        )
    SERVICES = [(service, values["name"]) for service,values in VIDEO_HOSTING_SERVICES.items()]
    service = models.CharField(choices = SERVICES, max_length = 50)
    video_code = models.CharField(max_length=255,
        help_text = "Not the full URL."
        )
    video_title = models.CharField(_("Title"), max_length=250)
    # video_caption = models.TextField(
    #     _("Video caption"), 
    #     blank=True, null=True
    #     )
    video_autoplay = models.BooleanField(_("Autoplay"), default=False)

    ASPECT_RATIOS = (
        (3.0, u'3x1'),
        (1.778, u'16x9'),
        (1.618, u'Golden ratio (horizontal)'),
        (1.5, u'3x2'),
        (1.333, u'4x3'),
        (1.0, u'Square'),
        (.75, u'3x4'),
        (.667, u'2x3'),
        (0.618, u'Golden ratio (vertical)'),
        (0.563, u'9x16'),
        (0.3, u'1x3'),
        )
    aspect_ratio = models.FloatField(choices = ASPECT_RATIOS, default = 1.333,          
        help_text = "Adjust to match video file"
        )

    def __unicode__(self):
        return self.video_title