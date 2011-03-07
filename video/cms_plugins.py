print "in VideoPluginPlublisher"
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
import models
from arkestra_utilities.output_libraries.plugin_widths import *

class VideoPluginPublisher(CMSPluginBase):
    model = models.VideoPluginEditor
    name = _("Video new")
    render_template = "video/video.html"
    text_enabled = False
    raw_id_fields = ('image',)
            
    def render(self, context, instance, placeholder):
        context.update({
            'object':instance,
            'placeholder':placeholder,
            })
        return context

    def icon_src(self, instance):
        return "instance.image.thumbnails['admin_tiny_icon']"

plugin_pool.register_plugin(VideoPluginPublisher)
