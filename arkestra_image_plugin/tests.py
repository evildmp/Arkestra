import os
from django.test import TestCase
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.files import File as DjangoFile

from cms.models.placeholdermodel import Placeholder

from cms.api import add_plugin
from filer.models.imagemodels import Image
from filer.tests.helpers import create_image


from arkestra_image_plugin.models import EmbeddedVideoSetItem, ImageSetItem
"""
create a plugin, with no items, should not render
with items - check urls that are generated
"""
class ImageLinkSetItemTests(TestCase):  
    def test_imagelinkset_plugin_with_one_inactive_item(self):
        item1 = ImageSetItem()
        item1.width, item1.height = 160, 30 
        self.assertEquals(
            item1.image_size,
            u"160x30"
        )    
    
class BasicImageLinkSetTests(TestCase):

    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(self.placeholder, u"ImageSetPublisher", u"en", width = 1000.0)
        self.plugin.save()
        self.img = Image(_width=100, _height=100)
        self.img.save()
        self.img2 = Image(_width=200, _height=100)
        self.img2.save()
        self.context = {"placeholder_width": 1000,} # fake context for testing widths

    def test_imagelinkset_plugin_with_no_items(self):
        instance = self.plugin.get_plugin_instance()[1]
        self.assertEquals(instance.render({}, self.plugin, self.placeholder), {}) 
       
    def test_imagelinkset_plugin_with_one_inactive_item(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            active=False,
            )
        item1.save()    
        self.assertEquals(instance.render({}, self.plugin, self.placeholder), {}) 

    def test_imagelinkset_plugin_with_one_active_item(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        self.assertEqual(
            instance.render({}, self.plugin, self.placeholder)["imageset"].item,
            item1
        )

    def test_imagelinkset_plugin_container_width_with_one_active_item(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        self.assertEqual(
            instance.render(self.context, self.plugin, self.placeholder)["imageset"].container_width,
            1000
        )

    def test_imagelinkset_plugin_template_with_one_active_item(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()   
        rendered_instance = instance.render({}, self.plugin, self.placeholder)
        self.assertEqual(
            instance.render_template,
            rendered_instance["imageset"].template,
            "arkestra_image_plugin/single_image.html"
        )                     

    def test_imagelinkset_plugin_image_size_with_one_active_item(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item = instance.render(self.context, self.plugin, self.placeholder)["imageset"].item
        self.assertEqual(
            (item.width, item.height),
            (1000, 1000)
        )

    def test_imagelinkset_plugin_image_size_with_200x100_active_item(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item1.save()    
        item = instance.render(self.context, self.plugin, self.placeholder)["imageset"].item
        self.assertEqual(
            (item.width, item.height),
            (1000, 500)
        )

    def test_imagelinkset_plugin_converted_image_size_with_one_active_item(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item = instance.render(self.context, self.plugin, self.placeholder)["imageset"].item
        self.assertEqual(
            item.image_size,
            u"1000x1000"
        )

    def test_imagelinkset_plugin_image_size_with_one_active_item_is_integer(self):
        instance = self.plugin.get_plugin_instance()[1]
        self.plugin.width = 33.3 # 1/3 width
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item = instance.render(self.context, self.plugin, self.placeholder)["imageset"].item
        self.assertEqual(
            (item.width, item.height),
            (333, 333)  # must come out as integer
        )

    def test_imagelinkset_plugin_with_two_active_items_chooses_one(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item2 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item2.save()    
        self.assertIn(
            instance.render({}, self.plugin, self.placeholder)["imageset"].item,
            [item1, item2]
        )  

class MultipleImageLinkSetTests(TestCase):

    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder, 
            u"ImageSetPublisher", 
            u"en", 
            width=1000.0,
            kind="multiple"
            )
        self.plugin.save()
        self.img = Image(_width=100, _height=100)
        self.img.save()
        self.img2 = Image(_width=200, _height=100)
        self.img2.save()
        self.context = {"placeholder_width": 1000,} # fake context for testing widths

    def test_imagelinkset_plugin_with_one_active_item(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        self.assertEqual(
            instance.render({}, self.plugin, self.placeholder)["imageset"].item,
            item1
        )

    def test_imagelinkset_plugin_with_two_active_items(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item2 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item2.save()    
        self.assertListEqual(
            instance.render({}, self.plugin, self.placeholder)["imageset"].items,
            [item1, item2]
        )  

    def test_imagelinkset_plugin_width_with_two_active_items(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item2 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item2.save()    
        self.assertListEqual(
            instance.render({}, self.plugin, self.placeholder)["imageset"].items,
            [item1, item2]
        )  

    def test_imagelinkset_plugin_with_two_active_items_reordered(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id, 
            inline_item_ordering=1,
            )
        item1.save()    
        item2 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item2.save()    
        self.assertListEqual(
            instance.render({}, self.plugin, self.placeholder)["imageset"].items,
            [item2, item1]
        )
        
    def test_imagelinkset_plugin_with_two_active_items_container_width(self):
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item2 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item2.save()    
        self.assertEqual(
            instance.render(self.context, self.plugin, self.placeholder)["imageset"].container_width,
            1000
        )

    def test_imagelinkset_plugin_with_two_active_items_same_sizes(self):
        # both images should come out square
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item2 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item2.save()
        image1=instance.render(self.context, self.plugin, self.placeholder)["imageset"].items[0]
        image2=instance.render(self.context, self.plugin, self.placeholder)["imageset"].items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (490, 490)
        )
        self.assertEqual(
            (image2.width, image2.height),
            (490, 490)
        )

    def test_imagelinkset_plugin_with_two_active_items_different_sizes(self):
        # aspect ratio of both images should be mean aspect ratio
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item2 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item2.save()
        image1=instance.render(self.context, self.plugin, self.placeholder)["imageset"].items[0]
        image2=instance.render(self.context, self.plugin, self.placeholder)["imageset"].items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (490, 326)
        )
        self.assertEqual(
            (image2.width, image2.height),
            (490, 326)
        )

    def test_imagelinkset_plugin_with_different_sizes_explicit_aspect_ratio(self):
        # aspect ratio of both images should be mean aspect ratio
        instance = self.plugin.get_plugin_instance()[1]
        self.plugin.aspect_ratio = 1.618
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        item2 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item2.save()
        image1=instance.render(self.context, self.plugin, self.placeholder)["imageset"].items[0]
        image2=instance.render(self.context, self.plugin, self.placeholder)["imageset"].items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (490, 302)
        )
        self.assertEqual(
            (image2.width, image2.height),
            (490, 302)
        )




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
        self.assertEquals(instance.render({}, plugin, placeholder), {}) 
        self.assertEquals(instance.render_template, "null.html") 

        # now the item is active
        item1.active=True
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
        self.assertEquals(instance.render_template, "embedded_video/vimeo.html") 
        
        # change aspect_ratio
        item1.aspect_ratio=1.0
        item1.save()    
        self.assertDictEqual(
            instance.render({}, plugin, placeholder), 
            {
                'width': 100,
                'video': item1,
                'embeddedvideoset': plugin,
                'height': 100,
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
