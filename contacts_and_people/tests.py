from datetime import datetime

from django.test import TestCase

from contacts_and_people.models import Person

class TestTest(TestCase):

    def setUp(self):
        self.person = Person(surname="Smith")

    def test_models(self):
        self.assertEqual(self.person.surname, "Smith")
