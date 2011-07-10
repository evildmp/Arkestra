import os
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
import models
from django.conf import settings

from filer.settings import FILER_STATICMEDIA_PREFIX
from arkestra_utilities.output_libraries.plugin_widths import *

class FilerImagePlugin(CMSPluginBase):
    model = models.FilerImage
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
        print
        print "----------------- Image plugin ------------------------" 
        print "image:", instance.image, "image width:", instance.image.width
        # get the image's aspect ratio, in case we need it later
        aspect_ratio = float(instance.image.width)/instance.image.height
        instance.has_borders = False
        
        # use native width
        if not instance.width: 
            width = float(instance.image.width) # is float needed?

        # absolute widths
        elif instance.width < 0: 
            width = -instance.width
            # a special case: 50px images are square
            if width == 50:
                instance.aspect_ratio = 1
        
        # relative widths
        else:
            # calculate the width of the placeholder
            placeholder_width = get_placeholder_width(context, instance)

            # widths a fraction of nominal container width (deprecated)
            if instance.width <= 10:
                width = placeholder_width/instance.width
         
            # widths relative to placeholder width
            else:
                # widths a percentage of placeholder width
                if instance.width <= 100:
                    width = placeholder_width/100.0 * instance.width
                    auto = False
            
                # automatic width      
                elif instance.width == 1000:
                    width = placeholder_width
                    auto = True
                
                # calculate the width of the block the image will be in
                width = calculate_container_width(instance, width, auto)
                       
            # shave off 5 point if the image is floated, to make room for a margin    
            if instance.float:
                print "-5 for float"
                width = width - 5   

        # # widths => 0 are relative to the placeholder or container
        # if instance.width > 0:
        #     # calculate the width of the placeholder
        #     placeholder_width = get_placeholder_width(context, instance)
        #     
        #     # widths <= 10 are relative to the placeholder (deprecated)
        #     if instance.width <= 10:     
        #         width = placeholder_width/instance.width
        # 
        #     else:
        # 
        #         # widths > 10 and <= 100 are a percentage of column width
        #         if instance.width <= 100:
        #             width = placeholder_width/100.0 * instance.width
        #             auto = False
        #         elif instance.width == 1000:
        #             width = placeholder_width
        #             auto = True
        # 
        #         # calculate the width of the block the image will be in
        #         width = calculate_container_width(instance, width, auto)
        # 
        #     # shave off 5 point if the image is floated, to make room for a margin    
        #     if instance.float:
        #         print "-5 for float"
        #         width = width - 5   
        #  
        #         
        # # if the instance has a negative width, it means it's an absolute width 
        # elif instance.width and instance.width < 0:
        #     width = -instance.width
        #     # a special case: 50px images are square
        #     if width == 50:
        #         instance.aspect_ratio = 1
        # 
        # # if the instance has no width we use the image's width
        # else: 
        #     width = float(instance.image.width) # is float needed?
                            
        # if the instance has an aspect ratio, use that to calculate the height
        if instance.aspect_ratio: 
            height = width / instance.aspect_ratio
            # if the instance has no width, but does have a height, use the aspect ratio to calculate it
            if instance.height and not instance.width: 
                width = height * instance.aspect_ratio

        # if the instance has no aspect ratio, but does have a height, use the height
        elif instance.height: 
            height = instance.height
            # if it had no width either, we can use the native aspect ratio to calculate that
            if not instance.width: 
                width = aspect_ratio * height
        # if the instance has no aspect ratio, we use the native aspect ratio
        else:
            height = width / aspect_ratio
        #else:
        #    print "doing something funny"
            # height was not externally defined: use image's native ratio to scale it by the width
        #    height = int( float(width)*float(instance.image.height)/float(instance.image.width) )
        
        if instance.use_description_as_caption:
            instance.caption = instance.caption or instance.image.description

        instance.float = instance.float or ""   # used as a CSS class
        
        print
        print "final output size", width, "x", height
                
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

plugin_pool.register_plugin(FilerImagePlugin)
