from django.test import TestCase
from django import forms
from django.core.files import File as DjangoFile

from cms.models.placeholdermodel import Placeholder
from cms.api import add_plugin

from filer.models.imagemodels import Image
from filer.tests.helpers import create_image


from arkestra_image_plugin.models import EmbeddedVideoSetItem, ImageSetItem, ImageSetPlugin, ImageSetTypePluginMixin


class ImageSetTypePluginMixinContainerWidthTests(TestCase):
    def setUp(self):
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder,
            u"ImageSetPublisher",
            u"en",
            kind="basic"
        )
        self.context = {"placeholder_width": 500,} # fake context for testing widths


    def test_imagelinkset_plugin_container_width_1000(self):
        # automatic - will *usually* be 100%
        self.plugin.width = 1000.0
        self.plugin.get_container_width({"placeholder_width": 500,})
        self.assertEqual(self.plugin.container_width, 500)

    def test_imagelinkset_plugin_container_width_100_of_500(self):
        # 100% of 500
        self.plugin.width = 100
        self.plugin.get_container_width({"placeholder_width": 500,})
        self.assertEqual(self.plugin.container_width, 500)

    def test_imagelinkset_plugin_container_width_100_of_800(self):
        # 100% of 800
        self.plugin.width = 100
        self.plugin.get_container_width({"placeholder_width": 800,})
        self.assertEqual(self.plugin.container_width, 800)

    def test_imagelinkset_plugin_container_width_50_of_500(self):
        # 50% of 500
        self.plugin.width = 50
        self.plugin.get_container_width({"placeholder_width": 500,})
        self.assertEqual(self.plugin.container_width, 250)

    def test_imagelinkset_plugin_container_width_33_of_500(self):
        # 33.3% of 500 - coerced to integer
        self.plugin.width = 33.3
        self.plugin.get_container_width({"placeholder_width": 500,})
        self.assertEqual(self.plugin.container_width, 166)


class ImageSetTypePluginMixinContainerGetPluginWidthTests(TestCase):
    """
    For testing methods of the Imageset plugin that don't require fully-
    constructed plugin instances
    """
    def setUp(self):
        # create & save plugin
        self.plugin = ImageSetPlugin()
        self.plugin.save()
        # create & save images
        self.image1 = Image(_width=100, _height=100)
        self.image1.save()

    # output: 0 = auto, +ve if set explicitly
    # native only acts if an image is provided

    def test_defaults(self):
        # automatic
        self.assertEqual(self.plugin.get_plugin_width(), 0)

    def test_defaults_with_image(self):
        # automatic; ignore image
        self.assertEqual(self.plugin.get_plugin_width(self.image1), 0)

    def test_no_image_native_plugin_width(self):
        # native but no image so auto
        self.plugin.width = 0
        self.assertEqual(self.plugin.get_plugin_width(), 0)

    def test_no_image_absolute_plugin_width(self):
        # absolute
        self.plugin.width = -250
        self.assertEqual(self.plugin.get_plugin_width(), 250)

    def test_image_native_plugin_width(self):
        # native and image so use image's width
        self.plugin.width = 0
        self.assertEqual(self.plugin.get_plugin_width(self.image1), 100)

    def test_image_absolute_width(self):
        # absolute; ignore image
        self.plugin.width = -250
        self.assertEqual(self.plugin.get_plugin_width(self.image1), 250)

class ImageSetTypePluginEasyMethodTests(TestCase):
    """
    For testing methods of the Imageset plugin that don't require fully-
    constructed plugin instances
    """
    def setUp(self):
        # create & save plugin
        self.plugin = ImageSetPlugin()
        self.plugin.save()
        # create & save images
        self.image1 = Image(_width=100, _height=100)
        self.image2 = Image(_width=200, _height=100)
        self.image3 = Image(_width=200, _height=100)
        self.image1.save()
        self.image2.save()
        self.image3.save()
        # create & save plugin items
        self.item1 = ImageSetItem(
            plugin=self.plugin,
            image=self.image1)
        self.item2 = ImageSetItem(
            plugin=self.plugin,
            image=self.image2)
        self.item3 = ImageSetItem(
            plugin=self.plugin,
            image=self.image3)
        self.item1.save()
        self.item2.save()
        self.item3.save()

    def test_calculate_aspect_ratio(self):
        # calculated aspect ratio should be mean aspect ratio of all items
        self.assertEqual(
            self.plugin.calculate_aspect_ratio([self.item1, self.item2]),
            1.5
        )

    def test_active_items(self):
        self.assertListEqual(
            list(self.plugin.active_items),
            [self.item1, self.item2, self.item3]
        )

    def test_active_items_one_inactive(self):
        self.item2.active = False
        self.item2.save()
        self.assertListEqual(
            list(self.plugin.active_items),
            [self.item1, self.item3]
        )

    def test_active_items_reordered(self):
        self.item1.inline_item_ordering = 1
        self.item1.save()
        self.assertListEqual(
            list(self.plugin.active_items),
            [self.item2, self.item3, self.item1]
        )

    def test_imagelinkset_select_imageset_kind_single(self):
        # basic = single_image, single_image.html
        self.plugin.kind = "basic"
        self.item1.save()
        self.item2.save()
        self.item3.save()
        self.assertEquals(self.plugin.select_imageset_kind(), "single_image")
        self.assertEquals(self.plugin.template, "arkestra_image_plugin/single_image.html")

    def test_imagelinkset_select_imageset_kind_multiple(self):
        # multiple = multiple_images, multiple_images.html
        self.plugin.kind = "multiple"
        self.item1.save()
        self.item2.save()
        self.item3.save()
        self.assertEquals(self.plugin.select_imageset_kind(), "multiple_images")
        self.assertEquals(self.plugin.template, "arkestra_image_plugin/multiple.html")

    def test_imagelinkset_select_imageset_kind_lightbox(self):
        # lightbox = lightbox, lightbox.html
        self.plugin.kind = "lightbox"
        self.item1.save()
        self.item2.save()
        self.item3.save()
        self.assertEquals(self.plugin.select_imageset_kind(), "multiple_images")
        self.assertEquals(self.plugin.template, "arkestra_image_plugin/lightbox.html")

    def test_imagelinkset_select_imageset_kind_lightbox_single(self):
        # lightbox = lightbox, lightbox.html
        self.plugin.kind = "lightbox-single"
        self.item1.save()
        self.item2.save()
        self.item3.save()
        self.assertEquals(self.plugin.select_imageset_kind(), "lightbox_single")
        self.assertEquals(self.plugin.template, "arkestra_image_plugin/lightbox.html")

    def test_imagelinkset_select_imageset_kind_items_no_kind(self):
        # no kind declared? single_image, single_image.html
        self.assertEquals(self.plugin.select_imageset_kind(), "single_image")
        self.assertEquals(self.plugin.template, "arkestra_image_plugin/single_image.html")

    def test_imagelinkset_select_imageset_kind_no_items(self):
        # no active_items? None, null.html
        self.item1.active = False
        self.item2.active = False
        self.item3.active = False
        self.item1.save()
        self.item2.save()
        self.item3.save()
        self.assertEquals(self.plugin.select_imageset_kind(), None)
        self.assertEquals(self.plugin.template, "null.html")

    def test_imagelinkset_select_imageset_kind_multiple_one_item(self):
        # only one item? single_image, single_image.html
        self.plugin.kind = "multiple"
        self.item1.active = False
        self.item2.active = False
        self.item1.save()
        self.item2.save()
        self.assertEquals(self.plugin.select_imageset_kind(), "single_image")
        self.assertEquals(self.plugin.template, "arkestra_image_plugin/single_image.html")

    def test_imagelinkset_select_imageset_kind_lightbox_single_one_item(self):
        # only one item lightbox single item? use lightbox_single
        self.plugin.kind = "lightbox-single"
        self.item1.active = False
        self.item2.active = False
        self.item1.save()
        self.item2.save()
        self.assertEquals(self.plugin.select_imageset_kind(), "lightbox_single")
        self.assertEquals(self.plugin.template, "arkestra_image_plugin/lightbox.html")

    def test_imagelinkset_calculate_plugin_dimensions_positive_self_aspect_ratio(self):
        # calculated_width and self.aspect_ratio determine height
        self.plugin.width = 1000.0 # automatic
        self.plugin.aspect_ratio = 2
        self.plugin.height = 0
        self.assertEquals(
            self.plugin.calculate_plugin_dimensions(299, 7.353),
            (299,149)
        )

    def test_imagelinkset_calculate_plugin_dimensions_height_no_aspect_ratio_width(self):
        # self.height and calculated_width determine size
        self.plugin.width = 1000.0 # automatic
        self.plugin.aspect_ratio = 0
        self.plugin.height = 200.1
        self.assertEquals(
            self.plugin.calculate_plugin_dimensions(130.7, 7.353),
            (130,200)
        )

    def test_imagelinkset_calculate_plugin_dimensions_height_no_aspect_ratio_no_width(self):
        # self.height and calculated_width determine size
        self.plugin.width = 0 # native
        self.plugin.aspect_ratio = 0
        self.plugin.height = 200
        self.assertEquals(
            self.plugin.calculate_plugin_dimensions(130, 7.353),
            (1470,200)
        )

    def test_imagelinkset_calculate_plugin_dimensions_no_height_no_aspect_ratio_no_width(self):
        # self.height and calculated_width determine size
        self.plugin.width = 0 # native
        self.plugin.aspect_ratio = 0
        self.plugin.height = None
        self.assertEquals(
            self.plugin.calculate_plugin_dimensions(500.5, 2.5),
            (500,200)
        )

    def test_imagelinkset_calculate_plugin_dimensions_no_height_aspect_ratio_no_width(self):
        # self.height and calculated_width determine size
        self.plugin.width = 0 # native
        self.plugin.aspect_ratio = 1
        self.plugin.height = None
        self.assertEquals(
            self.plugin.calculate_plugin_dimensions(505.5, 2),
            (505,505)
        )

class ImagesetsReturnCorrectItems(TestCase):

    def setUp(self):
        # create & save plugin
        self.plugin = ImageSetPlugin()
        self.plugin.save()
        # create & save images
        self.image1 = Image(_width=100, _height=100)
        self.image2 = Image(_width=200, _height=100)
        self.image3 = Image(_width=300, _height=100)
        self.image1.save()
        self.image2.save()
        self.image3.save()
        # create & save plugin items
        self.item1 = ImageSetItem(
            plugin=self.plugin,
            image=self.image1)
        self.item2 = ImageSetItem(
            plugin=self.plugin,
            image=self.image2)
        self.item3 = ImageSetItem(
            plugin=self.plugin,
            image=self.image3)
        self.item1.save()
        self.item2.save()
        self.item3.save()

    # basic
    # multiple
    # slider
    # lightbox single

    # are the right items being returned?

    def test_imagelinkset_plugin_basic_returns_one_active_item(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.single_image()
        self.assertIn(self.plugin.item, self.plugin.active_items)

    def test_imagelinkset_plugin_multiple_returns_all_active_item(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.multiple_images()
        self.assertListEqual(
            list(self.plugin.items),
            list(self.plugin.active_items)
        )

    def test_imagelinkset_plugin_slider_returns_all_active_item(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.slider()
        self.assertListEqual(
            list(self.plugin.items),
            list(self.plugin.active_items)
        )

    def test_imagelinkset_plugin_lightbox_single_one_active_item(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.lightbox_single()
        self.assertListEqual(
            list(self.plugin.items),
            list(self.plugin.active_items)
        )
        self.assertEqual(
            self.plugin.item,
            list(self.plugin.active_items)[0]
        )

class ImagesetsReturnCorrectImageSizesAutomaticWidthAndAspectRatio(TestCase):

    def setUp(self):
        # create & save plugin
        self.plugin = ImageSetPlugin()
        self.plugin.save()
        # create & save images
        self.image1 = Image(_width=100, _height=100)
        self.image2 = Image(_width=200, _height=100)
        self.image3 = Image(_width=300, _height=100)
        self.image1.save()
        self.image2.save()
        self.image3.save()
        # create & save plugin items
        self.item1 = ImageSetItem(
            plugin=self.plugin,
            image=self.image1)
        self.item2 = ImageSetItem(
            plugin=self.plugin,
            image=self.image2)
        self.item3 = ImageSetItem(
            plugin=self.plugin,
            image=self.image3)
        self.item1.save()
        self.item2.save()
        self.item3.save()

    def test_imagelinkset_plugin_item_size(self):
        self.item1.active = self.item2.active = False
        self.item1.save()
        self.item2.save()
        self.plugin.items = self.plugin.active_items
        self.plugin.single_image()
        item = self.plugin.item
        self.assertEqual(
            (item.width, item.height),
            (500,166)
        )

    def test_imagelinkset_plugin_multiple_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.multiple_images()
        item = self.plugin.items[0]
        self.assertEqual(
            (item.width, item.height),
            (152, 83)
        )

    def test_imagelinkset_plugin_slider_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.slider()
        item = self.plugin.items[0]
        self.assertEqual(
            self.plugin.size,
            (500,250)
        )
        self.assertEqual(
            (item.width, item.height),
            (500, 250)
        )

    def test_imagelinkset_plugin_lightbox_single_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.lightbox_single()
        item = self.plugin.items[0]
        self.assertEqual(
            (item.width, item.height),
            (480,480)
        )

class ImagesetsReturnCorrectImageSizesOneThirdWidthAndAspectRatio(TestCase):

    def setUp(self):
        # create & save plugin
        self.plugin = ImageSetPlugin()
        self.plugin.width = 33.3
        self.plugin.save()
        # create & save images
        self.image1 = Image(_width=100, _height=100)
        self.image2 = Image(_width=200, _height=100)
        self.image3 = Image(_width=300, _height=100)
        self.image1.save()
        self.image2.save()
        self.image3.save()
        # create & save plugin items
        self.item1 = ImageSetItem(
            plugin=self.plugin,
            image=self.image1)
        self.item2 = ImageSetItem(
            plugin=self.plugin,
            image=self.image2)
        self.item3 = ImageSetItem(
            plugin=self.plugin,
            image=self.image3)
        self.item1.save()
        self.item2.save()
        self.item3.save()

    def test_imagelinkset_plugin_item_size(self):
        self.item1.active = self.item2.active = False
        self.item1.save()
        self.item2.save()
        self.plugin.items = self.plugin.active_items
        self.plugin.single_image()
        item = self.plugin.item
        self.assertEqual(
            (item.width, item.height),
            (166, 55)
        )

    def test_imagelinkset_plugin_multiple_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.multiple_images()
        item = self.plugin.items[0]
        self.assertEqual(
            (item.width, item.height),
            (41, 27)
        )

    def test_imagelinkset_plugin_slider_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.slider()
        item = self.plugin.items[0]
        self.assertEqual(
            self.plugin.size,
            (166, 83)
        )
        self.assertEqual(
            (item.width, item.height),
            (166, 83)
        )

    def test_imagelinkset_plugin_lightbox_single_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.lightbox_single()
        item = self.plugin.items[0]
        self.assertEqual(
            (item.width, item.height),
            (146, 146)
        )


class ImagesetsReturnCorrectImageSizesAutomaticWidthNativeRatio(TestCase):

    def setUp(self):
        # create & save plugin
        self.plugin = ImageSetPlugin()
        self.plugin.aspect_ratio = -1.0
        self.plugin.save()
        # create & save images
        self.image1 = Image(_width=100, _height=100)
        self.image2 = Image(_width=200, _height=100)
        self.image3 = Image(_width=300, _height=100)
        self.image1.save()
        self.image2.save()
        self.image3.save()
        # create & save plugin items
        self.item1 = ImageSetItem(
            plugin=self.plugin,
            image=self.image1)
        self.item2 = ImageSetItem(
            plugin=self.plugin,
            image=self.image2)
        self.item3 = ImageSetItem(
            plugin=self.plugin,
            image=self.image3)
        self.item1.save()
        self.item2.save()
        self.item3.save()

    def test_imagelinkset_plugin_item_size(self):
        self.item1.active = self.item2.active = False
        self.item1.save()
        self.item2.save()
        self.plugin.items = self.plugin.active_items
        self.plugin.single_image()
        item = self.plugin.item
        self.assertEqual(
            (item.width, item.height),
            (500, 166)
        )

    def test_imagelinkset_plugin_multiple_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.multiple_images()
        item = self.plugin.items[0]
        self.assertEqual(
            (item.width, item.height),
            (152, 83)
        )

    def test_imagelinkset_plugin_slider_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.slider()
        item = self.plugin.items[0]
        self.assertEqual(
            self.plugin.size,
            (500,250)
        )
        self.assertEqual(
            (item.width, item.height),
            (500, 250)
        )

    def test_imagelinkset_plugin_lightbox_single_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.lightbox_single()
        item = self.plugin.items[0]
        self.assertEqual(
            (item.width, item.height),
            (480,480)
        )

class ImagesetsReturnCorrectImageSizesAutomaticForcedAspectRatio(TestCase):

    def setUp(self):
        # create & save plugin
        self.plugin = ImageSetPlugin()
        self.plugin.aspect_ratio = 1.333
        self.plugin.save()
        # create & save images
        self.image1 = Image(_width=100, _height=100)
        self.image2 = Image(_width=200, _height=100)
        self.image3 = Image(_width=300, _height=100)
        self.image1.save()
        self.image2.save()
        self.image3.save()
        # create & save plugin items
        self.item1 = ImageSetItem(
            plugin=self.plugin,
            image=self.image1)
        self.item2 = ImageSetItem(
            plugin=self.plugin,
            image=self.image2)
        self.item3 = ImageSetItem(
            plugin=self.plugin,
            image=self.image3)
        self.item1.save()
        self.item2.save()
        self.item3.save()

    def test_imagelinkset_plugin_item_size(self):
        self.item1.active = self.item2.active = False
        self.item1.save()
        self.item2.save()
        self.plugin.items = self.plugin.active_items
        self.plugin.single_image()
        item = self.plugin.item
        self.assertEqual(
            (item.width, item.height),
            (500, 375)
        )

    def test_imagelinkset_plugin_multiple_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.multiple_images()
        item = self.plugin.items[0]
        self.assertEqual(
            (item.width, item.height),
            (152, 125)
        )

    def test_imagelinkset_plugin_slider_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.slider()
        item = self.plugin.items[0]
        self.assertEqual(
            self.plugin.size,
            (500,375)
        )
        self.assertEqual(
            (item.width, item.height),
            (500, 375)
        )

    def test_imagelinkset_plugin_lightbox_single_image_sizes(self):
        self.plugin.items = self.plugin.active_items
        self.plugin.lightbox_single()
        item = self.plugin.items[0]
        self.assertEqual(
            (item.width, item.height),
            (480, 360)
        )


class ImageLinkSetItemTests(TestCase):
    def test_imagelinkset_image_size(self):
        item1 = ImageSetItem()
        item1.width, item1.height = 160, 30
        self.assertEquals(
            item1.image_size,
            u"160x30"
        )

    def test_imagelinkset_image_size_is_integers(self):
        item1 = ImageSetItem()
        item1.width, item1.height = 160.4, 30.33
        self.assertEquals(
            item1.image_size,
            u"160x30"
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
