from django.test import TestCase
from django import forms
from django.contrib.contenttypes.models import ContentType

from cms.api import create_page, add_plugin

from links.models import Link
from links.admin import check_urls

from contacts_and_people.models import Site, Person, Building, Entity, Membership
from contacts_and_people.tests import EntityTestObjectsMixin

class SearchTests(EntityTestObjectsMixin, TestCase):
    
    def test_entity_description(self):
        
        link_to_school = Link(
            destination_content_type = ContentType.objects.get_for_model(self.school),
            destination_object_id = self.school.id,
            )
        
        self.assertEquals(link_to_school.text(), self.school.name)

        # home_page = create_page("title", "arkestra.html", "en", menu_title=None, slug=None, apphook=None, redirect=None, meta_description="Description")
        # 
        # 
        # self.assertEquals(link_to_school.description(), "Description")

        link_to_building = Link(
            destination_content_type = ContentType.objects.get_for_model(self.main_building),
            destination_object_id = self.main_building.id,
            )
        
        self.assertEquals(link_to_building.text(), self.main_building.get_name())
        self.assertEquals(link_to_building.description(), u"St Mary's Street, Cardiff")

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
            {'message': "Warning: this email address hasn't been checked. I hope it's correct.", 'level': 30}
            )
        