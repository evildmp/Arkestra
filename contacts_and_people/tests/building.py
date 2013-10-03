from django.test import TestCase

from contacts_and_people.models import Site, Building


class BuildingIdentifierTests(TestCase):
    """tests for Building.identifier()"""
    def test_identifier_with_name_returns_name(self):
        building = Building(
            name="Main Building",
            street="St Mary's Street",
            number="37a",
            postcode="CF5 1QE",
            )
        self.assertEqual(building.identifier(), "Main Building")

    def test_identifier_with_no_name_returns_street_address(self):
        building = Building(
            street="St Mary's Street",
            number="37a",
            postcode="CF5 1QE",
            )
        self.assertEqual(building.identifier(), "37a St Mary's Street")

    def test_identifier_with_no_name_or_street_returns_postcode(self):
        building = Building(
            postcode="CF5 1QE",
            )
        self.assertEqual(building.identifier(), "CF5 1QE")


class BuildingGetPostalAddressTests(TestCase):
    """for the Building model"""
    def setUp(self):
        # a geographical Site
        self.cardiff = Site(
            site_name="Main site",
            post_town="Cardiff",
            country="UK",
            )

    def test_get_postal_address_with_name_includes_name(self):
        building = Building(
            name="Main Building",
            street="St Mary's Street",
            number="37a",
            postcode="CF5 1QE",
            site=self.cardiff
            )
        self.assertEqual(
            ['Main Building', "37a St Mary's Street", 'Cardiff CF5 1QE'],
            building.get_postal_address
        )

    def test_get_postal_address_with_missing_components(self):
        building = Building(
            site=self.cardiff
            )
        self.assertEqual(
            ['Cardiff'],
            building.get_postal_address
        )

class BuildingTests(TestCase):
    """Other tests of smaller methods etc"""
    def test_has_map_is_always_boolean(self):
        building = Building(
            latitude=None,
            longitude=None,
            zoom=17,
            map=False
            )
        self.assertFalse(building.has_map())

        building.map = True
        self.assertFalse(building.has_map())

        building.longitude = 0
        building.latitude = 0
        self.assertTrue(building.has_map())

        building.longitude = 1
        building.latitude = 1
        self.assertTrue(building.has_map())
