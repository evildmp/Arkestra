import os
from django.test import TestCase
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.files import File as DjangoFile

from cms.models.placeholdermodel import Placeholder

from cms.api import add_plugin
from filer.models.imagemodels import Image
from filer.tests.helpers import create_image


from arkestra_image_plugin.models import EmbeddedVideoSetItem, ImageSetItem, ImageSetPlugin
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
    
class ImageSetPluginTests(TestCase):

    def setUp(self):
        self.item1 = ImageSetItem(
            image=Image(_width=100, _height=100))
        self.item2 = ImageSetItem(
            image=Image(_width=200, _height=100))

    def test_calculate_aspect_ratio(self):
        # calculated aspect ratio should be mean aspect ratio of all items
        self.assertEqual(
            ImageSetPlugin().calculate_aspect_ratio([self.item1, self.item2]), 
            1.5
        )    

class ImageSetPluginKindTests(TestCase):
    # test that the correct plugin kind/template is chosen
    
    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder, 
            u"ImageSetPublisher", 
            u"en", 
            width = 1000.0,
            kind="multiple"
        )
        self.plugin.save()
        self.img = Image(_width=100, _height=100)
        self.img.save()
        self.img2 = Image(_width=200, _height=100)
        self.img2.save()
        self.context = {"placeholder_width": 1000,} # fake context for testing widths  


    def test_imagelinkset_plugin_with_no_items(self):
        # no items? null.html
        instance = self.plugin.get_plugin_instance()[1]
        instance.render({}, self.plugin, self.placeholder)
        self.assertEquals(instance.render_template, "null.html")

    def test_imagelinkset_plugin_with_an_inactive_item(self):
        # no items? null.html
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            active=False,
            )
        item1.save()    
        instance.render({}, self.plugin, self.placeholder)
        self.assertEquals(instance.render_template, "null.html")

    def test_imagelinkset_plugin_with_one_active_item(self):
        # one item? arkestra_image_plugin/single_image.html
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        instance.render({}, self.plugin, self.placeholder)
        self.assertEquals(instance.render_template, "arkestra_image_plugin/single_image.html")

    def test_imagelinkset_plugin_with_one_active_item_reverts_to_single(self):
        # one item? we force arkestra_image_plugin/single_image.html
        instance = self.plugin.get_plugin_instance()[1]
        self.plugin.kind = "slider"
        self.plugin.save()
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        instance.render({}, self.plugin, self.placeholder)
        self.assertEquals(instance.render_template, "arkestra_image_plugin/single_image.html")

class ImageLinkSetContainerWidthTests(TestCase):
    # test that the correct plugin container width is calculated

    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder, 
            u"ImageSetPublisher", 
            u"en", 
            width = 1000.0,
        )
        self.plugin.save()
        self.img = Image(_width=100, _height=100)
        self.img.save()
        self.img2 = Image(_width=200, _height=100)
        self.img2.save()
        self.context = {"placeholder_width": 500,} # fake context for testing widths  

        
    def test_imagelinkset_plugin_container_width(self):
        # placeholder_width is 1000, so is container_width
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()
        instance.render(self.context, self.plugin, self.placeholder)
        self.assertEqual(self.plugin.container_width, 500)

    def test_imagelinkset_plugin_container_width_50_percent(self):
        # placeholder_width is 1000, container_width is half that
        self.plugin.width = 50.0
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()
        instance.render(self.context, self.plugin, self.placeholder)
        self.assertEqual(self.plugin.container_width, 250) 
        
    def test_imagelinkset_plugin_container_width_is_integer(self):
        # container_width should be an integer
        self.plugin.width = 33.3
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()
        instance.render(self.context, self.plugin, self.placeholder)
        self.assertEqual(self.plugin.container_width, 166)
        

class BasicLinkSetTests(TestCase):

    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder, 
            u"ImageSetPublisher", 
            u"en", 
            width = 1000.0,
        )
        self.plugin.save()
        self.plugin.container_width = 1000
        self.img = Image(_width=100, _height=100)
        self.img.save()
        self.img2 = Image(_width=200, _height=100)
        self.img2.save()
        self.context = {} # fake context for testing widths  

    def test_imagelinkset_plugin_returns_one_active_item(self):
        # single item is returned as imageset.item
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()
        self.plugin.single_image() 
        self.assertEqual(self.plugin.item, item1)                     

    def test_imagelinkset_plugin_image_size_with_one_active_item(self):
        # single item width is container_width
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()
        self.plugin.single_image() 
        item = self.plugin.item
        self.assertEqual(
            (item.width, item.height),
            (1000, 1000)
        )

    def test_imagelinkset_plugin_image_size_with_200x100_active_item(self):
        # single item width is container_width; height is proportional
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item1.save()    
        self.plugin.single_image() 
        item = self.plugin.item
        self.assertEqual(
            (item.width, item.height),
            (1000, 500)
        )

    def test_imagelinkset_plugin_with_two_active_items_chooses_one(self):
        # two active; chooses one
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
        self.plugin.single_image() 
        self.assertIn(self.plugin.item, [item1, item2])  

    def test_rendering_single_image(self):
        # render and test context
        instance = self.plugin.get_plugin_instance()[1]
        item1 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img.id,
            )
        item1.save()    
        imageset = instance.render({"placeholder_width": 500,}, self.plugin, self.placeholder)["imageset"]
        self.assertEqual(list(imageset.items), [item1])  
        self.assertEqual(imageset.item, item1)  
        

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
        self.plugin.container_width = 1000


    def test_imagelinkset_plugin_with_two_active_items(self):
        # two active items appear in multiple set
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
        self.plugin.multiple_images()
        self.assertListEqual(
            list(self.plugin.items),
            [item1, item2]
        )  
 
    def test_imagelinkset_plugin_with_two_active_items_reordered(self):
        # reverse their order
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
        self.plugin.multiple_images()
        self.assertListEqual(list(self.plugin.items), [item2, item1])
        
    def test_imagelinkset_plugin_with_two_active_items_width(self):
        # two items in a row; should fit side-by-side in container
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
        self.plugin.multiple_images()
        self.assertEqual(
            self.plugin.items[0].width,
            490
        )

    def test_imagelinkset_plugin_with_three_active_items_width(self):
        # three items in a row; should fit side-by-side in container
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
        item3 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item3.save()    
        self.plugin.multiple_images()
        self.assertEqual(
            self.plugin.items[0].width,
            320
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
        self.plugin.multiple_images()
        image1 = self.plugin.items[0]
        image2 = self.plugin.items[1]
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
        self.plugin.multiple_images()
        image1 = self.plugin.items[0]
        image2 = self.plugin.items[1]
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
        self.plugin.multiple_images()
        image1 = self.plugin.items[0]
        image2 = self.plugin.items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (490, 302)
        )
        self.assertEqual(
            (image2.width, image2.height),
            (490, 302)
        )        

class LightboxGalleryImageLinkSetTests(TestCase):

    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder, 
            u"ImageSetPublisher", 
            u"en", 
            width=1000.0,
            kind="lightbox"
            )
        self.plugin.save()
        self.img = Image(_width=100, _height=100)
        self.img.save()
        self.img2 = Image(_width=200, _height=100)
        self.img2.save()
        self.context = {"placeholder_width": 1000,} # fake context for testing widths
        self.plugin.container_width = 1000


    def test_imagelinkset_plugin_with_two_active_items(self):
        # two active items appear in multiple set
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
        self.plugin.multiple_images()
        self.assertListEqual(
            list(self.plugin.items),
            [item1, item2]
        )  
 
    def test_imagelinkset_plugin_with_two_active_items_reordered(self):
        # reverse their order
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
        self.plugin.multiple_images()
        self.assertListEqual(list(self.plugin.items), [item2, item1])
        
    def test_imagelinkset_plugin_with_two_active_items_width(self):
        # two items in a row; should fit side-by-side in container
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
        self.plugin.multiple_images()
        self.assertEqual(
            self.plugin.items[0].width,
            480
        )

    def test_imagelinkset_plugin_with_three_active_items_width(self):
        # three items in a row; should fit side-by-side in container
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
        item3 = ImageSetItem(
            plugin=self.plugin,
            image_id=self.img2.id,
            )
        item3.save()    
        self.plugin.multiple_images()
        self.assertEqual(
            self.plugin.items[0].width,
            313
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
        self.plugin.multiple_images()
        image1 = self.plugin.items[0]
        image2 = self.plugin.items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (480, 480)
        )
        self.assertEqual(
            (image2.width, image2.height),
            (480, 480)
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
        self.plugin.multiple_images()
        image1 = self.plugin.items[0]
        image2 = self.plugin.items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (480, 320)
        )
        self.assertEqual(
            (image2.width, image2.height),
            (480, 320)
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
        self.plugin.multiple_images()
        image1 = self.plugin.items[0]
        image2 = self.plugin.items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (480, 296)
        )
        self.assertEqual(
            (image2.width, image2.height),
            (480, 296)
        )        

class LightboxSingleImageLinkSetTests(TestCase):

    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder, 
            u"ImageSetPublisher", 
            u"en", 
            width=1000.0,
            kind="lightbox-single"
            )
        self.plugin.save()
        self.img = Image(_width=100, _height=100)
        self.img.save()
        self.img2 = Image(_width=200, _height=100)
        self.img2.save()
        self.context = {"placeholder_width": 1000,} # fake context for testing widths
        self.plugin.container_width = 1000


    def test_imagelinkset_plugin_with_two_active_items(self):
        # two active items appear in imageset.items
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
        self.plugin.lightbox_single()
        self.assertListEqual(
            list(self.plugin.items),
            [item1, item2]
        )  

    def test_imagelinkset_plugin_with_two_active_items_width(self):
        # imageset.item is first image
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
        self.plugin.lightbox_single()
        self.assertEqual(
            self.plugin.items[0].width,
            980
        )

    def test_imagelinkset_plugin_with_two_active_items_different_sizes(self):
        # aspect imageset.image should be first item's aspect ratio
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
        self.plugin.lightbox_single()
        image1 = self.plugin.items[0]
        image2 = self.plugin.items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (980, 980)
        )

    def test_imagelinkset_plugin_with_different_sizes_explicit_aspect_ratio(self):
        # aspect ratio of both images should be mean aspect ratio
        instance = self.plugin.get_plugin_instance()[1]
        self.plugin.aspect_ratio = 2
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
        self.plugin.lightbox_single()
        image1 = self.plugin.items[0]
        image2 = self.plugin.items[1]
        self.assertEqual(
            (image1.width, image1.height),
            (980, 490)
        )

class SliderImageLinkSetTests(TestCase):

    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder, 
            u"ImageSetPublisher", 
            u"en", 
            width=1000.0,
            kind="slider"
            )
        self.plugin.save()
        self.img = Image(_width=100, _height=100)
        self.img.save()
        self.img2 = Image(_width=200, _height=100)
        self.img2.save()
        self.context = {"placeholder_width": 1000,} # fake context for testing widths
        self.plugin.container_width = 1000


    def test_imagelinkset_plugin_with_two_active_items(self):
        # two active items appear in multiple set
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
        self.plugin.multiple_images()
        self.assertListEqual(
            list(self.plugin.items),
            [item1, item2]
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
