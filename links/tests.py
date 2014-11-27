from django.test import TestCase
from django import forms
from django.contrib.contenttypes.models import ContentType

from cms.models.placeholdermodel import Placeholder
from cms.api import add_plugin

from filer.models.imagemodels import Image

from links.models import Link, GenericLinkListPluginItem, CarouselPluginItem
from links.admin import check_urls

from contacts_and_people.models import (
    Site, Person, Building, Entity, Membership
    )
from contacts_and_people.tests import EntityTestObjectsMixin


class SearchTests(EntityTestObjectsMixin, TestCase):

    def test_entity_description(self):

        link_to_school = Link(
            destination_content_type=ContentType.objects.get_for_model(
                self.school
                ),
            destination_object_id=self.school.id,
            )

        self.assertEquals(link_to_school.__unicode__(), self.school.name)

        link_to_building = Link(
            destination_content_type = ContentType.objects.get_for_model(self.main_building),
            destination_object_id = self.main_building.id,
            )

        self.assertEquals(
            link_to_building.__unicode__(),
            self.main_building.__unicode__()
            )
        self.assertEquals(
            link_to_building.summary(),
            u"St Mary's Street, Cardiff"
            )

        """
        Currently autocomplete searches on description, but this isn't good enough.

        Sometimes when searching in the admin, we need to return useful information for the user, such as warnings about some of the objects.

        However, searching on the front end should not necessarily return warnings in the same way.

        So we should have an "admin_description" (or something) attribute on which to search as well.
        """
class ExternalLinkTests(TestCase):

    def test_good_url(self):
        # http://vurt.org/ should be accepted without a murmur
        self.assertEquals([], check_urls("http://vurt.org/"))

    def test_unknown_scheme(self):
        # an unknown urlscheme should raise a forms.ValidationError
        self.assertRaisesMessage(
            forms.ValidationError,
            u'Sorry, link type bogusurlscheme is not permitted. Permitted types are https, http, mailto and ftp.',
            check_urls,
            "bogusurlscheme://vurt.org/"
            )

    def test_missing_scheme(self):
        # a missing urlscheme should raise a forms.ValidationError
        self.assertRaisesMessage(
            forms.ValidationError,
            u'Please provide a complete URL, such as "http://example.com/" or "mailto:example@example.com". Permitted schemes are https, http, mailto and ftp.',
            check_urls,
            "vurt.org/"
            )

    def test_host_not_found(self):
        # a hostname we can't find should raise a forms.ValidationError
        self.assertRaisesMessage(
            forms.ValidationError,
            u'Hostname vurt.vurt.vurt.vurt.org not found. Please check that it is correct.',
            check_urls,
            "http://vurt.vurt.vurt.vurt.org/"
            )

    def test_404(self):
        # a link we can't open shouuld return a message
        self.assertDictEqual(
            check_urls("http://vurt.org/zxcvbnmmnbvcxz/")[0],
            {'message': 'Warning: the link http://vurt.org/zxcvbnmmnbvcxz/ appears not to work. Please check that it is correct.', 'level': 30}
)

    # def test_does_not_match(self):
    #     a link we can't open shouuld return a message
    #     not sure how this can be tested
    #     "Warning: your URL " + url + " doesn't match the site's, which is: " + url_test.geturl()

    def test_mail_to(self):
        # a link we can't open should return a message
        self.assertDictEqual(
            check_urls("mailto:daniele@vurt.org")[0],
            {'message': """
                Warning: this email address hasn't been checked. I hope it's correct.
                """,
             'level': 30}
            )



class LinkListPluginTests(EntityTestObjectsMixin, TestCase):

    def test_links_plugin_item(self):
        """
        test the output of the link set plugin
        """
        placeholder = Placeholder(slot=u"some_slot")
        placeholder.save() # a good idea, if not strictly necessary

        # add the plugin
        plugin = add_plugin(placeholder, u"LinksPlugin", u"en",
            )
        plugin.save()

        # get the corresponding plugin instance
        instance = plugin.get_plugin_instance()[1]


        # add an item to the plugin
        item1 = GenericLinkListPluginItem(
            plugin=plugin,
            destination_content_type = ContentType.objects.get_for_model(self.school),
            destination_object_id = self.school.id,
            active=False,
            )
        item1.save()
        self.assertEquals(
            instance.render({}, plugin, placeholder),
            {}
        )

        # now the item is active
        item1.active=True
        item1.save()
        self.assertEqual(
            instance.render({}, plugin, placeholder)["links"],
            [item1]
        )

        # add a second image to the plugin
        item2 = GenericLinkListPluginItem(
            plugin=plugin,
            destination_content_type = ContentType.objects.get_for_model(self.school),
            destination_object_id = self.school.id,
            )
        item2.save()
        self.assertListEqual(
            instance.render({}, plugin, placeholder)["links"],
            [item1, item2]
        )

        # now the ordering should be reversed
        item1.inline_item_ordering=1
        item1.save()
        self.assertListEqual(
            instance.render({}, plugin, placeholder)["links"],
            [item2, item1]
        )


class CarouselPluginTests(EntityTestObjectsMixin, TestCase):
    def test_carousel_plugin(self):
        """
        test the output of the link set plugin
        """
        img = Image(_width=100, _height=100)
        img.save()

        placeholder = Placeholder(slot=u"some_slot")
        placeholder.save() # a good idea, if not strictly necessary

        # add the plugin
        plugin = add_plugin(
            placeholder,
            u"CarouselPluginPublisher",
            u"en",
            width = 1000.0
        )
        plugin.save()

        # get the corresponding plugin instance
        instance = plugin.get_plugin_instance()[1]
        self.assertEquals(instance.render({}, plugin, placeholder), {})

        # add an item to the plugin
        item1 = CarouselPluginItem(
            plugin=plugin,
            destination_content_type = ContentType.objects.get_for_model(self.school),
            destination_object_id = self.school.id,
            link_title=u"item1 link title",
            active=False,
            image_id=img.id,
            )
        item1.save()
        self.assertEquals(instance.render({}, plugin, placeholder), {})

        # now the item is active
        item1.active=True
        item1.save()
        self.assertEquals(instance.render({}, plugin, placeholder), {})

        # add a second image to the plugin
        item2 = CarouselPluginItem(
            plugin=plugin,
            destination_content_type = ContentType.objects.get_for_model(self.school),
            destination_object_id = self.school.id,
            link_title=u"item1 link title",
            image_id=img.id,
            )
        item2.save()
        self.assertListEqual(
            instance.render({}, plugin, placeholder)["segments"],
            [item1, item2]
        )

        # now the ordering should be reversed
        item1.inline_item_ordering=1
        item1.save()
        rendered_plugin = instance.render({}, plugin, placeholder)
        self.assertListEqual(
            rendered_plugin["segments"],
            [item2, item1]
        )

        # check size calculations
        self.assertEqual(
            rendered_plugin["size"],
            (98,65)
        )
        # if we delete the image the items should be deleted too
        img.delete()
        self.assertEquals(instance.render({}, plugin, placeholder), {})
