import os
from django.test import TestCase
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.files import File as DjangoFile

from cms.models.placeholdermodel import Placeholder

from cms.api import add_plugin
from filer.models.imagemodels import Image
from filer.tests.helpers import create_image


from models import EmbeddedVideoSetItem, ImageSetItem
"""
create a plugin, with no items, should not render
with items - check urls that are generated
"""
class ImageLinkSetTests(TestCase):

    def create_filer_image(self):
        self.img = create_image()
        self.image_name = 'test_file.jpg'
        self.filename = os.path.join(os.path.dirname(__file__),
                                 self.image_name)
        self.img.save(self.filename, 'JPEG')
        file_obj= DjangoFile(open(self.filename), name=self.image_name)
        image = Image.objects.create(owner=self.superuser,
                                     original_filename=self.image_name,
                                     file=file_obj)
        return image

    def test_imagelinkset_plugin_item(self):
        """
        test the output of the image link set plugin 
        """
        img = Image()
        img.save()
        # create a placeholder
        placeholder = Placeholder(slot=u"some_slot")
        placeholder.save() # a good idea, if not strictly necessary

        # add the plugin
        plugin = add_plugin(placeholder, u"ImageSetPublisher", u"en",
            width = 1000.0,
            )
        plugin.save()

        # get the corresponding plugin instance
        instance = plugin.get_plugin_instance()[1]

        self.assertEquals(plugin.active_items.count(), 0) 
        self.assertEquals(instance.render({}, plugin, placeholder), {}) 
       
        # add an image to the plugin
        item1 = ImageSetItem(
            plugin=plugin,
            image_id=img.id,
            active=False,
            )
        self.assertEquals(list(plugin.active_items), []) 

        # now the item is active
        item1.active=True
        item1.save() 
        self.assertListEqual(list(plugin.active_items), [item1]) 

        # add a second image to the plugin
        item2 = ImageSetItem(
            plugin=plugin,
            image_id=img.id,
            )
        item2.save()    
        self.assertListEqual(list(plugin.active_items), [item1, item2]) 

        # now the ordering should be reversed
        item1.inline_item_ordering=1
        item1.save() 
        self.assertListEqual(list(plugin.active_items), [item2, item1]) 


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
        self.assertEquals(plugin.active_items.count(), 0) 
        self.assertEquals(instance.render({}, plugin, placeholder), {}) 
       
        # add a video to the plugin - but it's not active
        item1 = EmbeddedVideoSetItem(
            plugin=plugin,
            service="vimeo",
            video_code="1234",
            video_title="one",
            active=False,
            inline_item_ordering=1
            )
        item1.save()    
        self.assertEquals(plugin.active_items.count(), 0) 
        self.assertEquals(instance.render({}, plugin, placeholder), {}) 

        # now the item is active
        item1.active=True
        item1.save()    
        self.assertEquals(list(plugin.active_items), [item1]) 
        self.assertDictEqual(
            instance.render({}, plugin, placeholder), 
            {
                'width': 100,
                'video': item1,
                'embeddedvideoset': plugin,
                'height': 75,
            }
            ) 
        
        # add a second video to the plugin
        item2 = EmbeddedVideoSetItem(
            plugin=plugin,
            service="vimeo",
            video_code="5678",
            video_title="two",
            )
        item2.save()    
        self.assertEquals(list(plugin.active_items), [item2, item1]) 
