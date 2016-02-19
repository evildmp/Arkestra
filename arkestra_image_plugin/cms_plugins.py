from __future__ import division

from django.contrib import admin
from django import forms
from django.db import models

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase


from widgetry import fk_lookup

from arkestra_utilities.settings import VIDEO_HOSTING_SERVICES
from arkestra_utilities.admin_mixins import AutocompleteMixin, SupplyRequestMixin

from links import schema

from models import ImageSetItem, ImageSetPlugin, EmbeddedVideoSetItem, EmbeddedVideoSetPlugin

class ImageSetItemPluginForm(forms.ModelForm):
    class Meta:
        model = ImageSetItem

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
    model = ImageSetItem
    form = ImageSetItemPluginForm
    extra=1

    fieldset_basic = ('', {'fields': ((
        'image',
        'alt_text',
        ),)})
    fieldset_advanced = ('Caption', {
        'fields': (
            ( 'auto_image_title', 'manual_image_title'),
            ( 'auto_image_caption', 'manual_image_caption'),
        ),
        'classes': ('collapse',)
        })
    fieldset_control = ('Control', {
        'fields': (
            ( 'inline_item_ordering', 'active'),
        ),
        'classes': ('collapse',)
        })

    fieldsets = (
        fieldset_basic,
        fieldset_advanced,
        ("Link", {
            'fields': (
                ('destination_content_type', 'destination_object_id',),
                ('auto_link_title', 'manual_link_title'), ( 'auto_link_description', 'manual_link_description'),
            ),
            'description': "Links will only be applied if <em>all</em> images in the set have links.",
            'classes': ('collapse',),
        }),
        fieldset_control,
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
    fieldset_basic = ('Size & proportions', {'fields': (
        ('kind', 'notes',),
        ('width', 'aspect_ratio',)
        ,)})
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

        kind = imageset.select_imageset_kind()
        if kind:
            getattr(imageset, kind)(context)
            context.update({
                'imageset':imageset,
                })
        self.render_template = imageset.template
        return context

    def __unicode__(self):
        return self

    def icon_src(self, instance):
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
            embeddedvideoset.get_container_width(context)
            width = embeddedvideoset.container_width
            height = int(embeddedvideoset.container_width/video.aspect_ratio)

            self.render_template = VIDEO_HOSTING_SERVICES[video.service]["template"]
            context.update({
                'embeddedvideoset': embeddedvideoset,
                'video': video,
                'width': width,
                'height': height,
                })

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
