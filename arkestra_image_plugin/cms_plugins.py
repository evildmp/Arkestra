from __future__ import division
import os

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin, messages
from django import forms
from django.db import models

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin

from easy_thumbnails.files import get_thumbnailer

from widgetry.tabs.admin import ModelAdminWithTabs
from widgetry import fk_lookup

from arkestra_utilities.settings import IMAGESET_ITEM_PADDING, VIDEO_HOSTING_SERVICES

from arkestra_utilities.output_libraries.plugin_widths import get_placeholder_width, calculate_container_width
from arkestra_utilities.admin_mixins import AutocompleteMixin, SupplyRequestMixin

from links import schema

from models import FilerImage, ImageSetItem, ImageSetPlugin, EmbeddedVideoSetItem, EmbeddedVideoSetPlugin

# a dictionary to show how many items per row depending on the number of items
LIGHTBOX_COLUMNS = {1:1, 2:2, 3:3, 4:4, 5:5, 6:3, 7:4, 8:4, 9:3, 10:5, 11:4, 12:4, 13:5, 14:5, 15:5, 16:4, 17:6, 18:6, 19:5, 20:5, 21:6, 22:6, 23:6, 24:6, 25:5 }

def width_of_image_container(context, plugin):
    # Based on the plugin settings and placeholder width, calculate image container width
    
    # work out native image aspect ratio
    plugin.has_borders = False
    
    # width values
    # None:     use native width
    # <0:       an absolute value
    # <=100:    a percentage of placeholder's width
    # 1000:     automatic, based on placeholder's width
    
    placeholder_width = get_placeholder_width(context, plugin)

    if plugin.width > 0 and plugin.width <= 100:
        width = placeholder_width/100.0 * plugin.width
        auto = False
    else:
        width = placeholder_width
        auto = True
        
    # calculate the width of the block the image will be in
    width = calculate_container_width(context, plugin, width, auto)
    
    # return the width of the container
    # print "width_of_image_container", width
    return width

def width_of_image(plugin, image=None):
    # no plugin width? 
    # print "plugin width", plugin.width
    if not plugin.width:
        if image:
            # print "image", image
            # use native image width
            width = image.width
        else:
            # use container width
            width = plugin.container_width
    # negative numbers are absolutes
    elif plugin.width < 0:
        width = -plugin.width
    else:
        width = plugin.container_width 
    # print "width_of_image", width
    return width
    
def calculate_aspect_ratio(image):
    return float(image.width)/image.height

def shave_if_floated(plugin, width):
    # shave off 5 point if the image is floated, to make room for a margin
    # see arkestra.css, span.image.left and span.image.right
    if plugin.float and plugin.width > 0:
        # print "-5 for float"
            return width - 5
               
def calculate_height(given_width, given_height, given_aspect_ratio, width, aspect_ratio):
    # given_width, given_height, given_aspect_ratio are values set by the plugin
    # width and aspect_ratio are calculated values
    # using given values gives us a chance to use given values to override calculated ones 
       
    # rules:
    # if the instance has an aspect ratio, use that to calculate the height
    # if the instance has no aspect ratio, but does have a height, use the height
    # if the instance has no aspect ratio, we use the native aspect ratio

    # has aspect ratio
    # print  given_aspect_ratio
    
    if given_aspect_ratio == -1:
        height=width/aspect_ratio 
    elif given_aspect_ratio: 
        height = width / given_aspect_ratio
        # if the instance has no width, but does have a height, use the aspect ratio to calculate it
        if given_height and not given_width: 
            width = height * given_aspect_ratio
    # has height
    elif given_height: 
        height = given_height
        # if it had no width either, we can use the native aspect ratio to calculate that
        if not given_width: 
            width = aspect_ratio * height
    # use the native aspect ratio
    else:
        height = width / aspect_ratio
        
    return width, height



def slider(imageset):
    # loops over the items in the set, and calculates their sizes
    # for use in a slider
    imageset.template = "arkestra_image_plugin/slider.html"
    width = width_of_image(imageset)
    if imageset.aspect_ratio:
        height = imageset.container_width / imageset.aspect_ratio
    elif imageset.height:
        height = imageset.height    
    else:
        # use the aspect ratio of the widest image
        heights = []
        for item in imageset.items:
            divider = 1.0/float(item.image.width)
            height_multiplier = float(item.image.height)*divider
            heights.append(height_multiplier)
            
        heights.sort()
        height_multiplier = heights[0]
        height = width * height_multiplier
    imageset.size = (int(width),int(height))
    for item in imageset.items:
        item.image_size = imageset.size
    return imageset

    
def multiple_images(imageset, context):
    # for lightboxes and multiple image sets
    imageset.template = "arkestra_image_plugin/%s.html" %imageset.kind
    imageset.padding = IMAGESET_ITEM_PADDING
    padding_adjuster = IMAGESET_ITEM_PADDING * 2
    
    # each item will be the same width - the user gets no say in this
    # also, let's not have any nonsense about using the native widths
    # - and only percentage and automatic widths are allowed
    # we call width_of_image() without an image argument 
    each_item_width = width_of_image(imageset)           

    # if imageset.aspect_ratio is 0 (auto) get an average and use that
    if imageset.aspect_ratio == 0 and not imageset.height:
        aspect_ratio = sum([calculate_aspect_ratio(item.image) for item in imageset.items])/imageset.number_of_items
    # otherwise use supplied aspect ratio
    else:
        aspect_ratio = imageset.aspect_ratio                             

    # don't allow more items_per_row than there are items
    if imageset.items_per_row > imageset.number_of_items:
        imageset.items_per_row = imageset.number_of_items
    
    items_per_row = imageset.items_per_row or LIGHTBOX_COLUMNS.get(imageset.number_of_items, 8) 

    # if we are using automatic/percentage widths, base them on the placeholder
    if imageset.width > 0: 
        each_item_width = each_item_width / items_per_row

    # fancybox icons and multiple images with links have padding, so:
    if imageset.kind == "lightbox" or imageset.items_have_links:
        each_item_width = each_item_width - padding_adjuster                   
    else: 
        # otherwise give them a margin
        if imageset.width > 0:
            each_item_width = each_item_width - (items_per_row-1) * padding_adjuster/items_per_row  

    # if imageset.aspect_ratio  is not -1 (forced native) calculate height/width for all
    if not imageset.aspect_ratio == -1:
        each_item_width, each_item_height = calculate_height(imageset.width, imageset.height, imageset.aspect_ratio, each_item_width, aspect_ratio)

    # set up each item
    # for counter, item in enumerate(imageset.items, start = 1): # enable this when we no longer need to support Python 2.5
    for counter, item in enumerate(imageset.items):
        counter=counter+1
        # mark end-of-row items in case the CSS needs it    
        # only when we are using percentage widths
        if imageset.width > 0 and not counter%items_per_row:
            item.lastinrow = True

        if imageset.aspect_ratio == -1:
            aspect_ratio = calculate_aspect_ratio(item.image) 
            item.width,item.height = calculate_height(imageset.width, imageset.height, imageset.aspect_ratio, each_item_width, aspect_ratio)
            item.width,item.height = int(item.width), int(item.height)
            # print item.width,item.height
        else:            
            item.width,item.height = int(each_item_width), int(each_item_height)
            # print item.width,item.height
        item.image_size = u'%sx%s' %(item.width, item.height) 
        item.caption_width=item.width

    # # if forced_native, set each individually
    # else:
    #     for counter, item in enumerate(imageset.items):
    #         counter=counter+1
    #         # mark end-of-row items in case the CSS needs it    
    #         # only when we are using percentage widths
    #         if imageset.width > 0 and not counter%items_per_row:
    #             item.lastinrow = True
    # 
    #         aspect_ratio = calculate_aspect_ratio(item.image)
    #         item.width,item.height = calculate_height(imageset.width, imageset.height, imageset.aspect_ratio, each_item_width, aspect_ratio)
    #         item.width,item.height = int(item.width), int(item.height)
    #         item.image_size = u'%sx%s' %(item.width, item.height) 
    #         item.caption_width=item.width   


    return imageset
    
def lightbox_single(imageset, context):
    # for lightboxes and multiple image sets
    imageset.template = "arkestra_image_plugin/%s.html" %"lightbox"            
    imageset.padding = IMAGESET_ITEM_PADDING
    padding_adjuster = IMAGESET_ITEM_PADDING * 2
    
    # choose the first image from the set
    item = imageset.items[0]

    # calculate its native aspect ratio
    aspect_ratio = calculate_aspect_ratio(item.image)
    # get width
    # print "item.image",  item.image
    width = width_of_image(imageset, item.image)        
    # print "width = width_of_image(imageset, item.image",     width
    # shave if floated
    width = shave_if_floated(imageset, width) or width

    # fancybox icons  have padding, so:
    width = width - padding_adjuster
    
    # calculate height 
    item.width, item.height = calculate_height(imageset.width, imageset.height, imageset.aspect_ratio, width, aspect_ratio)
    item.image_size = u'%sx%s' % (int(item.width), int(item.height))

    # item.caption = set_image_caption(imageset.item)
    item.width,item.height = int(item.width), int(item.height)
    item.caption_width = item.width

    return imageset


def single_image(imageset, context):                 
    imageset.template = "arkestra_image_plugin/single_image.html"
    # choose an image at random from the set
    imageset.item = imageset.imageset_item.order_by('?')[0]

    # calculate its native aspect ratio
    aspect_ratio = calculate_aspect_ratio(imageset.item.image)
    # get width
    width = width_of_image(imageset, imageset.item.image)
    # shave if floated
    width = shave_if_floated(imageset, width) or width
                
    # calculate height 
    imageset.item.width, imageset.item.height = calculate_height(imageset.width, imageset.height, imageset.aspect_ratio, width, aspect_ratio)
    imageset.item.image_size = u'%sx%s' % (int(imageset.item.width), int(imageset.item.height))

    # imageset.item.caption = set_image_caption(imageset.item)
    imageset.item.width,imageset.item.height = int(imageset.item.width), int(imageset.item.height)
    imageset.item.caption_width = imageset.item.width
    return imageset
                
        
    
class ImageSetItemPluginForm(forms.ModelForm):
    class Meta:
        model=ImageSetItem
        
    def __init__(self, *args, **kwargs):
        super(ImageSetItemPluginForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None and self.instance.destination_content_type:
            destination_content_type = self.instance.destination_content_type.model_class()
        else:
            destination_content_type = None
        self.fields['destination_object_id'].widget = fk_lookup.GenericFkLookup('id_%s-destination_content_type' % self.prefix, destination_content_type)
        self.fields['destination_content_type'].widget.choices = schema.content_type_choices()

    def clean(self):
        super(ImageSetItemPluginForm, self).clean()
        # the Link is optional, but unless both fields both Type and Item fields are provided, 
        # reset them to None
        if not self.cleaned_data["destination_content_type"] or not self.cleaned_data["destination_object_id"]:
            self.cleaned_data["destination_content_type"]=None
            self.cleaned_data["destination_object_id"]=None


        if "click here" in self.cleaned_data["alt_text"].lower():
            raise forms.ValidationError("'Click here'?! In alt text?! You cannot be serious. Fix this at once.")


            
        return self.cleaned_data    


class ImageSetItemFormFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        super(ImageSetItemFormFormSet, self).clean()

        some_have_links = False
        some_do_not_have_links = False

        for form in self.forms:            
            # if a subform is invalid Django explicity raises
            # an AttributeError for cleaned_data
            try:    
                # only forms with an image field count - the others might be blank
                if form.cleaned_data:
                    if form.cleaned_data.get("destination_content_type") and form.cleaned_data.get("destination_object_id"):
                        some_have_links = True
                    else:
                        some_do_not_have_links = True
            except AttributeError:
                pass
        
        # #  if some_have_links and some_do_not_have_links then that's inconsistent      
        # if some_have_links and some_do_not_have_links:
        #     message = "I won't put links on any of your images until they all have links"
        #     messages.add_message(self.request, messages.WARNING, message)
            

class ImageSetItemEditor(SupplyRequestMixin, admin.StackedInline, AutocompleteMixin):
    form = ImageSetItemPluginForm
    # formset = ImageSetItemFormFormSet
    # related_search_fields = ['destination_content_type']
    model=ImageSetItem
    extra=1
    
    
    fieldset_basic = ('', {'fields': ((
        'image',                        
        'inline_item_ordering', 
        'active',
        ),)})
    fieldset_advanced = ('Caption', {
        'fields': (
            ( 'auto_image_title', 'manual_image_title'), 
            ( 'auto_image_caption', 'manual_image_caption'),
        ), 
        'classes': ('collapse',)
        })
    fieldsets = (
                fieldset_basic, 
                fieldset_advanced,         
                ("Link", {
                    'fields': (
                        ('destination_content_type', 'destination_object_id',), 
                        'alt_text',
                        ('auto_link_title', 'manual_link_title'), ( 'auto_link_description', 'manual_link_description'),
                    ),
                    'description': "Links will only be applied if <em>all</em> images in the set have links.",
                    'classes': ('collapse',),
            }),
)
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'cols':30, 'rows':3,},),},
    }

class ImageSetPluginForm(forms.ModelForm):
    class Meta:
        model=ImageSetPlugin
    # when the user adds link to some but not items, we need to issue a warning
    # this should warn them, but allow them to force a save
    # def clean(self):
    #     force = self.cleaned_data.get('force_save')
    #     if not force:
    #         self.fields['force_save'] = forms.BooleanField(initial=True, widget=forms.HiddenInput())
    #         raise forms.ValidationError('You gotta check something')
    #     return self.cleaned_data


class ImageSetPublisher(SupplyRequestMixin, CMSPluginBase):
    form = ImageSetPluginForm
    model = ImageSetPlugin
    name = "Image/link set"
    text_enabled = True
    raw_id_fields = ('image',)
    inlines = (ImageSetItemEditor,)
    admin_preview = False         
    fieldset_basic = ('Size & proportions', {'fields': ('notes', ('kind', 'width', 'aspect_ratio',),)})
    fieldset_advanced = ('Advanced', {'fields': (( 'float', 'height'),), 'classes': ('collapse',)})
    fieldset_items_per_row = ('For Multiple and Lightbox plugins only', {'fields': ('items_per_row',), 'classes': ('collapse',)})
    fieldsets = (fieldset_basic, fieldset_items_per_row, fieldset_advanced)
    readonly_fields = ["notes", ]
    
    def __init__(self, model = None, admin_site = None):
        self.admin_preview = False
        self.text_enabled = True
        super(ImageSetPublisher, self).__init__(model, admin_site)

    def notes(self,instance):
        if not instance.imageset_item.count():
            message = u"There are currently no items in this set."
        elif instance.imageset_item.count() == 1:
            message = u"There is currently only one item in this set."
        else:
            message = u"There are currently %s items in this set." % instance.imageset_item.count()
        return message
        
    def render(self, context, imageset, placeholder):

        # don't do anything if there are no items in the imageset
        if imageset.imageset_item.count():
            # calculate the width of the block the image will be in
            imageset.container_width = int(width_of_image_container(context, imageset))
            # copy the queryset to a list. You know it makes sense
            imageset.items = list(imageset.imageset_item.all())
            
            # at least two items are required for a slider
            if imageset.kind == "slider" and imageset.number_of_items > 1:
                imageset = slider(imageset)

            elif imageset.kind == "lightbox" or (imageset.kind == "multiple" and imageset.number_of_items > 1):
                imageset = multiple_images(imageset, context)

            elif imageset.kind == "lightbox-single":
                imageset = lightbox_single(imageset, context)

            else:
                imageset = single_image(imageset, context)

            self.render_template = imageset.template  
            context.update({
                'imageset':imageset,
                })

        # no items, use a null template    
        else:
            # print "using a null template" , imageset
            self.render_template = "null.html"  
            # context.update({
            #     'placeholder':placeholder,
            # })
        return context

            
    def __unicode__(self):
        return self

    def icon_src(self, instance):
        # print instance.kind
        if instance.imageset_item.count() == 1:
            try:
                return instance.imageset_item.all()[0].image.thumbnails['admin_tiny_icon']
            except KeyError:
                pass
        elif instance.kind == "basic":
            return "/static/plugin_icons/imageset_basic.png"
        elif instance.kind == "lightbox-single":
            return "/static/plugin_icons/lightbox.png"
        elif instance.kind == "lightbox":
            return "/static/plugin_icons/lightbox.png"
        elif instance.kind == "slider":
            return "/static/plugin_icons/image_slider.png"
        else:
            return "/static/plugin_icons/imageset.png"
        
plugin_pool.register_plugin(ImageSetPublisher)


def set_image_caption(image):
    # prefer the manually-entered caption on the plugin, otherwise the one from the filer
    if image.caption or (image.use_description_as_caption and image.image.description):
        return image.caption or image.image.description

class FilerImagePlugin(CMSPluginBase):
    model = FilerImage
    name = _("Image")
    render_template = "cmsplugin_filer_image/image.html"
    text_enabled = True
    raw_id_fields = ('image',)
    admin_preview = False   
         
    def render(self, context, instance, placeholder):
        self.render_template = "cmsplugin_filer_image/image.html"
        instance.has_borders = False
        
        # calculate its width and aspect ratio
        instance.container_width = width_of_image_container(context, instance)

        # calculate its native aspect ratio
        aspect_ratio = calculate_aspect_ratio(instance.image)
        # get width
        width = width_of_image(instance, instance.image)
        # shave if floated
        width = shave_if_floated(instance, width) or width
        
        # calculate height 
        instance.width, instance.height = calculate_height(instance.width, instance.height, instance.aspect_ratio, width, aspect_ratio)
        # set caption
        instance.caption = set_image_caption(instance)
        instance.subject_location = instance.image.subject_location
        instance.width, instance.height = int(instance.width), int(instance.height)   
        context.update({
            'object':instance, 
            'image_size': u'%sx%s' % (int(instance.width), int(instance.height)),
            'caption_width': int(width),
            'placeholder':placeholder,
            'subject_location': instance.image.subject_location,
            'imageset':instance,
            'imageset_item': instance, 
            'caption_width': int(instance.width),
            'placeholder':placeholder,
        })
        return context

    def get_thumbnail(self, context, instance):
        if instance.image:
            return instance.image.image.thumbnails['admin_tiny_icon']

    def icon_src(self, instance):
        if instance.image:
            try:
                return instance.image.image.thumbnails['admin_tiny_icon']
            except KeyError:
                pass

plugin_pool.register_plugin(FilerImagePlugin)   


class EmbeddedVideoSetItemEditor(SupplyRequestMixin, admin.StackedInline, AutocompleteMixin):
    model=EmbeddedVideoSetItem
    extra=1
    fieldsets = (
        (None, {
            'fields': (
                ('service', 'video_code', 'aspect_ratio'),  
                ('video_title', 'video_autoplay'),
                ('active', 'inline_item_ordering'),
            ),
        }),
    ) 
   
    
class EmbeddedVideoPlugin(CMSPluginBase):
    model = EmbeddedVideoSetPlugin
    admin_preview = False   

    name = "Embedded video set"
    text_enabled = True
    inlines = (EmbeddedVideoSetItemEditor,)
    
    
    def notes(self,instance):
        if not instance.embeddedvideoset_item.count():
            message = u"There are currently no items in this set."
        elif instance.imageset_item.count() == 1:
            message = u"There is currently only one item in this set."
        else:
            message = u"There are currently %s items in this set." % instance.imageset_item.count()
        return message
        
    def render(self, context, embeddedvideoset, placeholder):

        # don't do anything if there are no items in the embeddedvideoset
        if embeddedvideoset.active_items:
            video = embeddedvideoset.active_items.order_by('?')[0]

            # calculate the width of the block the image will be in
            width = int(width_of_image_container(context, embeddedvideoset))
            height = int(width/video.aspect_ratio)

            self.render_template = VIDEO_HOSTING_SERVICES[video.service]["template"]
            context.update({
                'embeddedvideoset': embeddedvideoset,
                'video': video,
                'width': width,
                'height': height,
                })

        # no items, use a null template    
        else:
            self.render_template = "null.html"  
        return context

            
    def __unicode__(self):
        return self

    def icon_src(self, instance):
        return "/static/plugin_icons/embedded_videos.png"
        

plugin_pool.register_plugin(EmbeddedVideoPlugin)


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
