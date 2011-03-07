from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from links.models import GenericLinkListPlugin, GenericLinkListPluginItem, CarouselPlugin, CarouselPluginItem, FocusOnPluginEditor, FocusOnPluginItemEditor
from django.conf import settings
from links.admin import ObjectLinkInlineForm
from django.contrib import admin
from arkestra_utilities.output_libraries.plugin_widths import *

class FocusOnInlineForm(ObjectLinkInlineForm):
    class Meta:
        model=FocusOnPluginItemEditor

class FocusOnInlineItemAdmin(admin.StackedInline):
    model = FocusOnPluginItemEditor
    form = FocusOnInlineForm
    fieldsets = (
        (None, {
            'fields': (
                'destination_content_type', 'destination_object_id',
            ),
        }),
        ('Overrides', {
            'fields': ('short_text_override', 'text_override','description_override', 'image_override',
            ),
            'classes': ('collapse',),
        })
    )

class FocusOnPluginPublisher(CMSPluginBase):
    model = FocusOnPluginEditor
    name = "FocusOn"
    render_template = "links/cms_plugins/focuson.html"
    text_enabled = True
    inlines = (FocusOnInlineItemAdmin,)
    def icon_src(self, instance):
        print "getting icon image for links plugin"
        return "/media/arkestra/focus_on.png"
    def render(self, context, instance, placeholder):
        print "--------------------------"
        print "in render of FocusOnPlugin"
        focuson = instance.focuson_items.order_by('?')[0]
        focuson.heading_level = instance.heading_level
        context.update({
            'focuson':focuson,
            'placeholder':placeholder,
            })
        print "returning context of FocusOnPlugin"
        return context

plugin_pool.register_plugin(FocusOnPluginPublisher)

# -----------------------------------------
class PluginLinkInlineForm(ObjectLinkInlineForm):
    class Meta:
        model=GenericLinkListPluginItem

class PluginInlineLink(admin.StackedInline):
    model = GenericLinkListPluginItem
    form = PluginLinkInlineForm
    fieldsets = (
        (None, {
            'fields': (
                'destination_content_type', 'destination_object_id',
                ('include_description', 'key_link',),
            ),
        }),
        ('Overrides', {
            'fields': ('metadata_override', 'heading_override', 'text_override','description_override', 'html_title_attribute',
            ),
            'classes': ('collapse',),
        })
    )

class LinksPlugin(CMSPluginBase):
    model = GenericLinkListPlugin
    name = "Link(s)"
    render_template = "links/cms_plugins/links.html"
    text_enabled = True
    
    raw_id_fields = ('image',)
    fieldsets = (
        (None, {
            'fields': (
                ('insert_as',), ('use_link_icons',), ('separator',)
            ),
        }),
    )
    inlines = (PluginInlineLink,)
    def icon_src(self, instance):
        return "/media/arkestra/links.png"
    def render(self, context, instance, placeholder):
        print "in render of LinksPlugin"
        all_links = instance.links.all()
        links = []
        links = [link for link in all_links if link.destination_content_object]
        # are there at least two items? if so, the second-last has a final_separator
        if len(links) > 1:
            links[-2].separator = instance.final_separator
        # are there at least three items? if so, all up to third-last have a separator
        if len(links) > 2:
            for link in links[0:-2]:
                link.separator = instance.separator        
        context.update({
            'object':instance,
            'use_link_icons': instance.use_link_icons,
            'links':links, 
            'placeholder':placeholder,
            'separator': instance.separator
        })
        return context
plugin_pool.register_plugin(LinksPlugin)

class PluginCarouselItemForm(ObjectLinkInlineForm):
    """
    """
    class Meta:
        model=CarouselPluginItem

class PluginInlineCarousel(admin.StackedInline):
    model = CarouselPluginItem
    form = PluginCarouselItemForm
    extra=3
    max_num=5
    fieldsets = (
        (None, {
            'fields': (
                ('destination_content_type', 'destination_object_id',),
                ('link_title', 'image', ),
            ),
        }),
    )
   
class CarouselPluginPublisher(CMSPluginBase):
    model = CarouselPlugin
    name = "Carousel"
    render_template = "links/cms_plugins/carousel.html"
    text_enabled = True
    raw_id_fields = ('image',)
    inlines = (PluginInlineCarousel,)
    def icon_src(self, instance):
        print "returning carousel icon"
        return "/media/arkestra/carousel.png"
        
    def render(self, context, instance, placeholder):
        print "----------------- Carousel plugin ------------------------"
        segments = list(instance.carousel_item.all())
        if len(segments) < 2:
            return # because it would be silly to have a carousel with only one segment
        # TODO: this scaling code needs to be in a common place
        # use the placeholder width as a hint for sizing
        placeholder_width = context.get('width', None)
        
        placeholder_width = get_placeholder_width(context, instance)
        if instance.width <= 10:     
            width = placeholder_width/instance.width

        else:
            plugins = get_plugin_ancestry(instance)
            width = placeholder_width/100.0 * instance.width
            print width, placeholder_width, instance.width              
            width = calculate_container_width(plugins, width)
        
        width = int(width) -2 # make room for left/right borders
        print "width (with room for borders):", width
        label_width = width/len(segments)
        
        print "label width:", label_width, width%len(segments)
        heights = []
        for segment in segments:
            print "------"
            print "segment size", segment.image.width, segment.image.height
            divider = 1.0/float(segment.image.width)
            height_multiplier = float(segment.image.height)*divider
            heights.append(height_multiplier)
            print "Segment details", segment, segment.url()
            print "label length", len(segment.link_title), ((width * label_width)/100.0) /float(len(segment.link_title))
            if ((width * label_width)/100.0) /float(len(segment.link_title)) > 6.0: # if the label width divided by no. of characters in label is > 10 (i.e. we allow about 10px width per character, then we'll assume the label can fit on a single line)
                segment.line_class = "single-line"
            else:
                segment.line_class = "double-line"
            segment.label_width = int(label_width - 1)
        heights.sort()
        height_multiplier = heights[0]
        segments[-1].label_class = "right"
        segments[-1].label_width = int(label_width + width%len(segments))

        print "--"
        print "heights", heights, height_multiplier
        if instance.aspect_ratio:
            height = width / instance.aspect_ratio
        else:
            height = width * height_multiplier
        print "height:", height 
        print "widths:", width/len(segments)
        size= (int(width),int(height))
        print "size", size
        context.update({
            'carousel':instance,
            'segments':segments, 
            'size': size,

        })
        return context
plugin_pool.register_plugin(CarouselPluginPublisher)

