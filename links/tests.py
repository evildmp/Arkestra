from django.test import TestCase

from django.contrib.contenttypes.models import ContentType

from cms.api import create_page, add_plugin

from links.models import Link

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