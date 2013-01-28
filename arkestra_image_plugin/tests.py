from django.test import TestCase
from django import forms
from django.contrib.contenttypes.models import ContentType

from cms.models.placeholdermodel import Placeholder

from cms.api import add_plugin

from models import EmbeddedVideoSetItem
"""
create a plugin, with no items, should not render
with items - check urls that are generated
"""


class EmbeddedVideoTests(TestCase):
    def test_embedded_video_plugin_item(self):
        """
        test the output of the embedded video plugin 
        """
        # create a placeholder
        placeholder = Placeholder(slot=u"some_slot")
        placeholder.save() # a good idea, if not strictly necessary

        # add the plugin
        plugin = add_plugin(placeholder, u"EmbeddedVideoPlugin", u"en",
            width = 1000.0,
            )
        plugin.save()

        # get the corresponding plugin instance
        instance = plugin.get_plugin_instance()[1]

        self.assertEquals(plugin.number_of_items, 0) 
        self.assertEquals(instance.render({}, plugin, placeholder), {}) 
       
        # add a video to the plugin
        item1 = EmbeddedVideoSetItem(
            plugin=plugin,
            service="vimeo",
            video_code="1234",
            video_title="one",
            )
        item1.save()    

        self.assertDictEqual(
            instance.render({}, plugin, placeholder), 
            {
                'width': 100,
                'video': item1,
                'embeddedvideoset': plugin,
                'height': 75,
            }
            ) 
        
