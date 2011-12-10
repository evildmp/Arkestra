from __future__ import division
import os

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms
from django.db import models

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from easy_thumbnails.files import get_thumbnailer

from widgetry.tabs.admin import ModelAdminWithTabs

from arkestra_utilities.output_libraries.plugin_widths import *

from models import FilerImage, ImageSetItem, ImageSetPlugin

def width_of_image(context, plugin, image):
    print "** image", image
    aspect_ratio = float(image.width)/image.height
    plugin.has_borders = False

    # use native width
    if not plugin.width: 
        width = float(image.width) # is float needed?

    # absolute widths
    elif plugin.width < 0: 
        width = -plugin.width
        # a special case: 50px images are square
        if width == 50:
            plugin.aspect_ratio = 1

    # relative widths
    else:
        # calculate the width of the placeholder
        placeholder_width = get_placeholder_width(context, plugin)

        # widths a fraction of nominal container width (deprecated)
        if plugin.width <= 10:
            width = placeholder_width/plugin.width
 
        # widths relative to placeholder width
        else:
            # widths a percentage of placeholder width
            if plugin.width <= 100:
                width = placeholder_width/100.0 * plugin.width
                auto = False
    
            # automatic width      
            elif plugin.width == 1000:
                width = placeholder_width
                auto = True
        
            # calculate the width of the block the image will be in
            width = calculate_container_width(context, plugin, width, auto)

    return width, aspect_ratio

def shave_if_floated(plugin, width):
    # shave off 5 point if the image is floated, to make room for a margin
    # see arkestra.css, span.image.left and span.image.right
    if plugin.float and plugin.width > 0:
        # print "-5 for float"
            return width - 5
               
def calculate_height(plugin, width, aspect_ratio):
    # if the instance has an aspect ratio, use that to calculate the height
    if plugin.aspect_ratio: 
        height = width / plugin.aspect_ratio
        # if the instance has no width, but does have a height, use the aspect ratio to calculate it
        if plugin.height and not plugin.width: 
            width = height * plugin.aspect_ratio

    # if the instance has no aspect ratio, but does have a height, use the height
    elif plugin.height: 
        height = plugin.height
        # if it had no width either, we can use the native aspect ratio to calculate that
        if not plugin.width: 
            width = aspect_ratio * height
    # if the instance has no aspect ratio, we use the native aspect ratio
    else:
        height = width / aspect_ratio
        
    return width, height

def set_image_caption(image):
    # set caption
    if image.use_description_as_caption:
        return image.caption or image.image.description


class FilerImagePlugin(CMSPluginBase):
    model = FilerImage
    name = _("Image")
    render_template = "cmsplugin_filer_image/image.html"
    text_enabled = True
    raw_id_fields = ('image',)
    admin_preview = False   
         
    def render(self, context, instance, placeholder):
        """
        if width => 0: image width will be relative to placeholder's width
            if width > 0 but <= 10: now no longer available - image width = placeholder's width/width
            if width > 10 but <= 100: image width = width% of placeholder's width
            if width = 1000: width will be calculated automatically
        if width < 0: absolute widths (preset in choices)
            image width = - width
            if image width = 50: special case: small square images
                aspect ratio = 1
         if width = "":
             image width = image's native width
             
        """
        # TODO: this scaling code needs to be in a common place
        # use the placeholder width as a hint for sizing
        # print
        # print "----------------- Image plugin ------------------------" 
        # print "image:", instance.image, "image width:", instance.image.width
        # get the image's aspect ratio, in case we need it later
        aspect_ratio = float(instance.image.width)/instance.image.height
        instance.has_borders = False
        
        # calculate its width
        print "**", width_of_image(context, instance, instance.image)
        width, aspect_ratio = width_of_image(context, instance, instance.image)
                       
        # shave if floated
        width = shave_if_floated(instance, width) or width
                            
        # calculate height 
        width, height = calculate_height(instance, width, aspect_ratio)
                
        # set caption
        instance.caption = set_image_caption(instance)
        
        # print
        # print "final output size", width, "x", height
                
        context.update({
            'object':instance,
            #'link':instance.link, 
            #'image_url':instance.scaled_image_url,
            'image_size': u'%sx%s' % (int(width), int(height)),
            'caption_width': int(width),
            'placeholder':placeholder,
        })
        return context

    def get_thumbnail(self, context, instance):
        if instance.image:
            return instance.image.image.file.get_thumbnail(self._get_thumbnail_options(context, instance))

    def icon_src(self, instance):
        return instance.image.thumbnails['admin_tiny_icon']


class ImageSetItemEditor(admin.TabularInline):
    model = ImageSetItem
    extra=1
    fieldset_basic = ('', {'fields': (('image', 'alt_text',),)})
    fieldset_advanced = ('Caption', {'fields': (( 'use_description_as_caption', 'caption'),), 'classes': ('collapse',)})
    fieldsets = (fieldset_basic, fieldset_advanced)
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'cols':30, 'rows':3,},),},
    }

class ImageSetPublisher(CMSPluginBase):
    model = ImageSetPlugin
    name = "Image Set"
    text_enabled = True
    raw_id_fields = ('image',)
    inlines = (ImageSetItemEditor,)
    admin_preview = False        
    fieldset_basic = ('Size & proportions', {'fields': (('kind', 'width', 'aspect_ratio',),)})
    fieldset_advanced = ('Advanced', {'fields': (( 'float', 'height'),), 'classes': ('collapse',)})
    fieldsets = (fieldset_basic, fieldset_advanced)
    
    def __init__(self, model = None, admin_site = None):
        self.admin_preview = False
        self.text_enabled = True
        super(ImageSetPublisher, self).__init__(model, admin_site)

    def render(self, context, imageset, placeholder):
        if imageset.imageset_item.count():
            if imageset.kind == "slider" and imageset.imageset_item.count() > 2:
                self.render_template = "arkestra_image_plugin/slider.html"
            
                # calculate the width of the placeholder
                placeholder_width = get_placeholder_width(context, imageset) 

                # widths a percentage of placeholder width
                if imageset.width <= 100:
                    width = placeholder_width/100.0 * imageset.width
                    auto = False
    
                # automatic width      
                elif imageset.width == 1000:
                    width = placeholder_width
                    auto = True

                # calculate the width of the block the image will be in
                width = calculate_container_width(context, imageset, width, auto)

                items = list(imageset.imageset_item.all())
                heights = []
                for item in items:
                    divider = 1.0/float(item.image.width)
                    height_multiplier = float(item.image.height)*divider
                    heights.append(height_multiplier)
                heights.sort()
                height_multiplier = heights[0]
                if imageset.aspect_ratio:
                    height = width / imageset.aspect_ratio
                else:
                    height = width * height_multiplier
                size= (int(width),int(height))
                imageset.items = items
                
                context.update({
                    'imageset':imageset,
                    'icon_size': size,
                    # 'image_size': u'%sx%s' % (int(width), int(height)),
                    # 'caption_width': int(width),
                    'placeholder':placeholder,
                })

            elif imageset.kind == "lightbox":
                self.render_template = "arkestra_image_plugin/lightbox.html"  

                # set captions
                items = imageset.imageset_item.all()
                for imageset_item in items:
                    thumbnail_options = {} 
                    
                    # set a caption for the item
                    imageset_item.caption = set_image_caption(imageset_item)
                    
                    # get width, height and lightbox_max_dimension
                    [width, height] = [imageset_item.image.width, imageset_item.image.height]
                    lightbox_max_dimension = context.get("lightbox_max_dimension")
                    
                    # user has set aspect ratio? apply it, set crop argument for thumbnailer
                    if imageset.aspect_ratio:
                        height = width / imageset.aspect_ratio
                        thumbnail_options.update({'crop': True}) 
                    
                    # get scaler value from width, height
                    scaler = min(lightbox_max_dimension / dimension for dimension in [width, height])
                    
                    # set size of thumbnail using scaler
                    thumbnail_options.update({'size': (width * scaler, height * scaler)})

                    # get thumbnailer object for the image
                    thumbnailer = get_thumbnailer(imageset_item.image)
                    
                    # apply options and get url
                    imageset_item.url = thumbnailer.get_thumbnail(thumbnail_options).url  

                imageset.items = items
                num_of_items = len(items)
                
                # calculate the width of the placeholder
                placeholder_width = get_placeholder_width(context, imageset) 
                
                # calculate the width of the block the image will be in
                container_width = calculate_container_width(context, imageset, placeholder_width, auto=True)
                
                # widths a percentage of placeholder width
                if imageset.width <= 100:
                    icon_width = (container_width/100 * imageset.width) / num_of_items
                    icon_height = imageset.height or icon_width 
    
                # automatic width      
                else:
                    LIGHTBOX_COLUMNS = {2:2, 3:3, 4:4, 5:5, 6:3, 7:4, 8:4, 9:3, 10:5, 11:4, 12:4, 13:5, 14:5, 15:5, 16:4, 17:6, 18:6, 19:5, 20:5, 21:6, 22:6, 23:6, 24:6, 25:5 }
                    divider = LIGHTBOX_COLUMNS.get(num_of_items, 6) 
                    icon_width = container_width / divider 
                    icon_height = imageset.height or icon_width
                     
                    # make the icons small enough to fit neatly on a line; if too small, make them bigger
                    while icon_width < 30:
                        icon_width = icon_width * 2 
                        icon_height = icon_height / 2 
                
                icon_width = icon_width - 6                   
                
                context.update({
                    'imageset':imageset,
                    'icon_size': (int(icon_width), int(icon_height)),
                    'placeholder':placeholder,
                })

            # we'll use the basic style
            else:
                self.render_template = "arkestra_image_plugin/single_image.html"
            
                # choose an image at random from the set
                imageset_item = imageset.imageset_item.order_by('?')[0]
        
                # calculate its width
                width, aspect_ratio = width_of_image(context, imageset, imageset_item.image)
        
                # shave if floated
                width = shave_if_floated(imageset, width) or width
                            
                # calculate height 
                width, height = calculate_height(imageset, width, aspect_ratio)

                # set caption
                imageset_item.caption = set_image_caption(imageset_item)
        
                print "final output size", width, "x", height
                
                context.update({
                    'imageset':imageset,
                    'imageset_item': imageset_item, 
                    'image_size': u'%sx%s' % (int(width), int(height)),
                    'caption_width': int(width),
                    'placeholder':placeholder,
                })
                
        # no items, use a null template    
        else:
            print "using a null template" , imageset
            self.render_template = "null.html"  
            context.update({
                'placeholder':placeholder,
            })
        return context

            
    def __unicode__(self):
        return self

    def icon_src(self, instance):
        print instance.kind
        if instance.imageset_item.count() == 1:
            return instance.imageset_item.all()[0].image.thumbnails['admin_tiny_icon']
        elif instance.kind == "basic":
            return "/static/plugin_icons/imageset_basic.png"
        elif instance.kind == "lightbox":
            return "/static/plugin_icons/lightbox.png"
        elif instance.kind == "slider":
            return "/static/plugin_icons/image_slider.png"
        
plugin_pool.register_plugin(ImageSetPublisher)
plugin_pool.register_plugin(FilerImagePlugin)   

                    # gcbirzan's suggestion on how to calculate LIGHTBOX_COLUMNS
                    # d={}
                    # def mid(n):
                    #     middle = int(n**.5)
                    #     for diff in range(3):
                    #         if n % (middle + diff) == 0:
                    #             return middle + diff
                    # 
                    # 
                    # for n in range(2, 100):
                    #     for diff in range(3):
                    #         res = mid(n+diff)
                    #         if not res:
                    #             continue
                    #         d[n] = res
                    #         break
                    #             
                    # 
                    # print "****", d
                    # print d[len(items)] 
