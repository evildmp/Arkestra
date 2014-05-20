from __future__ import division

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from cms.models import CMSPlugin

from filer.fields.image import FilerImageField

from arkestra_utilities.import_free_model_mixins import ArkestraGenericPluginItemOrdering
from arkestra_utilities.settings import VIDEO_HOSTING_SERVICES
from arkestra_utilities.output_libraries.plugin_widths import get_placeholder_width, calculate_container_width

from links.models import LinkMethodsMixin

from arkestra_utilities.settings import IMAGESET_ITEM_PADDING, LIGHTBOX_COLUMNS


class ImageSetTypePluginMixin(object):

    def get_container_width(self, context):
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
        self.container_width = int(calculate_container_width(context, self, width, auto))
        return self.container_width # return it for further processing

    def get_plugin_width(self, image=None):
        # given plugin.width and plugin.container_width and optionally an image,
        # return the width we'll use for the plugin. Mostly it will be the same as
        # plugin.container_width, but for native and absolute sizes we ignore that

        # no plugin width? use native image width or container width
        if not self.width:
            if image:
                # use native image width
                width = image.width
            else:
                # use container width
                width = 0
        # negative plugin widths are absolutes
        elif self.width < 0:
            width = -self.width
        else:
            width = 0
        return width

    def shave_if_floated(plugin, width):
        # shave off 5 point if the image is floated, to make room for a margin
        # see arkestra.css, span.image.left and span.image.right
        if plugin.float and plugin.width > 0:
            # print "-5 for float"
                return width - 5

    def calculate_aspect_ratio(self, item_list):
        return sum(
            [float(
                item.image.width)/item.image.height for item in item_list]
            )/len(item_list)

    def calculate_plugin_dimensions(self, calculated_width, calculated_aspect_ratio):

        # calculated_width and self.aspect_ratio determine height
        if self.aspect_ratio > 0:
            return int(calculated_width), int(calculated_width / self.aspect_ratio)

        # no self.aspect_ratio, so self.height applies
        elif self.aspect_ratio == 0 and self.height:
            # self.width exists, so use calculated_width and self.height
            if self.width:
                return int(calculated_width), int(self.height)
            # no width has been set; calculate it from self.height
            else:
                return int(self.height * calculated_aspect_ratio), int(self.height)

        # native width, aspect ratio and height
        elif self.aspect_ratio == -1 or self.aspect_ratio == 0:
            return int(calculated_width), int(calculated_width/calculated_aspect_ratio)
        else:
            return int(calculated_width), int(calculated_width/calculated_aspect_ratio)


class ImageSetPlugin(CMSPlugin, ImageSetTypePluginMixin):
    IMAGESET_KINDS = (
        ("basic", "Basic"),
        ("multiple", "Multiple image gallery"),
        ("lightbox", "Lightbox with gallery"),
        ("lightbox-single", "Lightbox without gallery"),
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
    width = models.FloatField(u"Width of set", choices = IMAGE_WIDTHS, default = 1000.0)
    height = models.PositiveIntegerField(null=True, blank=True,
        help_text = "Only applies when <strong>Aspect ratio</strong> is <em>Automatic</em>")

    ASPECT_RATIOS = (
        (0, u'Automatic'),
        (9.0, u'9x1'),
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
        help_text = "Only applies to gallery-type plugins")

    @property
    def items_have_links(self):
        return all(item.destination_content_object is not None for item in self.imageset_item.all())

    @property
    def active_items(self):
        return self.imageset_item.active_items()

    def select_imageset_kind(self):
        if not self.active_items:
            self.template = "null.html"
            return None
        self.items = self.active_items
        # at least two items are required for a slider
        if self.kind == "slider" and self.active_items.count() > 1:
            self.template = "arkestra_image_plugin/slider.html"
            return "slider"
        # multiple_images() prepares a gallery of images
        elif self.kind == "lightbox" or \
            (self.kind == "multiple" and self.active_items.count() > 1):
            self.template = "arkestra_image_plugin/%s.html" %self.kind
            return "multiple_images"
        # lightbox_single can work with one iamge
        elif self.kind == "lightbox-single":
            self.template = "arkestra_image_plugin/lightbox.html"
            return "lightbox_single"
        else:
            self.template = "arkestra_image_plugin/single_image.html"
            return "single_image"

    def single_image(self, context={"placeholder_width": 500}):
        # choose an image at random from the set
        self.item = self.items.order_by('?')[0]
        # get width
        width = self.get_plugin_width(self.item.image) or self.get_container_width(context)
        # shave if floated
        width = self.shave_if_floated(width) or width
        # calculate height
        self.item.width, self.item.height = self.calculate_plugin_dimensions(
            width,
            self.calculate_aspect_ratio([self.item.image])
            )

        self.item.caption_width = self.item.width
        self.items = [self.item]

    def multiple_images(self, context={"placeholder_width": 500}):
        # for lightboxes and multiple image sets

        self.padding = IMAGESET_ITEM_PADDING
        padding_adjuster = IMAGESET_ITEM_PADDING * 2

        # don't allow more items_per_row than there are items
        if self.items_per_row > self.items.count():
            self.items_per_row = self.items.count()

        items_per_row = self.items_per_row or LIGHTBOX_COLUMNS.get(self.items.count(), 8)

        # each item will be the same width - the user gets no say in this

        each_item_width = self.get_container_width(context) / items_per_row
        aspect_ratio = self.calculate_aspect_ratio(self.items)
        each_item_width, each_item_height = self.calculate_plugin_dimensions(
            each_item_width,
            aspect_ratio
            )

        # fancybox icons and multiple images with links have padding, so:
        if self.kind == "lightbox" or self.items_have_links:
            each_item_width = each_item_width - padding_adjuster
        else:
            # otherwise give them a margin
            each_item_width = int(each_item_width - (items_per_row-1) * padding_adjuster/items_per_row)

        # set up each item
        # for counter, item in enumerate(self.items, start = 1):
        # enable this when we no longer need to support Python 2.5
        for counter, item in enumerate(self.items):
            counter=counter+1
            # mark end-of-row items in case the CSS needs it
            if not counter%items_per_row:
                item.lastinrow = True

            item.width = item.caption_width = each_item_width
            item.height = each_item_height

    def lightbox_single(self, context={"placeholder_width": 500}):
        self.padding = IMAGESET_ITEM_PADDING
        padding_adjuster = IMAGESET_ITEM_PADDING * 2
        # convert to a list
        self.items = list(self.items)
        # choose the first image from the set
        self.item = self.items[0]

        # get width
        width = self.get_plugin_width(self.item.image) or self.get_container_width(context)
        # shave if floated
        width = self.shave_if_floated(width) or width

        # fancybox icons  have padding, so:
        width = width - padding_adjuster

        # calculate height
        self.item.width, self.item.height = self.calculate_plugin_dimensions(
            width, self.calculate_aspect_ratio([self.item])
            )
        # item.caption = set_image_caption(self.item)
        # item.width,item.height = int(item.width), int(item.height)
        self.item.caption_width = self.item.width

    def slider(self, context={"placeholder_width": 500}):
        # loops over the items in the set, and calculates their sizes
        # for use in a slider
        width = self.get_plugin_width() or self.get_container_width(context)

        self.size = (self.calculate_plugin_dimensions(
            width, self.calculate_aspect_ratio(self.items)
            ))

        for item in self.items:
            (item.width, item.height) = self.size

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
    alt_text = models.CharField(
        blank=True,
        max_length=255,
        help_text = """
        The image's meaning, message or function (if any). Leave empty for
        items with links.
        """
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
            return self.manual_link_title or (self.auto_link_title and self.destination_content_object)

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
        return u'%sx%s' % (int(self.width), int(self.height))


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

class EmbeddedVideoSetItem(ArkestraGenericPluginItemOrdering):
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
