from django.test import TestCase
from django.http import HttpRequest, QueryDict

from contacts_and_people.models import Entity, Person

from arkestra_utilities.text import concatenate
from generic_lister import (
    ArkestraGenericLister, ArkestraGenericList, ArkestraGenericFilterSet,
    ArkestraGenericFilterList
    )
from generic_models import ArkestraGenericModel


class TestConcatenate(TestCase):
    def test_concatenate_with_no_arguments(self):
        self.assertEqual(concatenate(), "")

    def test_concatenate_with_no_strings(self):
        self.assertEqual(
            concatenate(with_string="-"),
            ""
            )

    def test_concatenate_with_strings(self):
        self.assertEqual(
            concatenate(strings=["La", "vita", "nuda"]),
            "Lavitanuda"
            )

    def test_concatenate_with_strings_and_with_strings(self):
        self.assertEqual(
            concatenate(with_string="-", strings=["La", "vita", "nuda"]),
            "La-vita-nuda"
            )

    def test_concatenate_with_unnamed_arguments(self):
        self.assertEqual(
            concatenate(["La", "vita", "nuda"], "-"),
            "La-vita-nuda"
            )


class TestModel(ArkestraGenericModel):
    pass


class TestFilterSet(ArkestraGenericFilterSet):
    fields = ['title']


class ItemList(ArkestraGenericList):
    model = TestModel
    filter_set = TestFilterSet


class ListBuildItemsTests(TestCase):
    def test_build_no_items(self):

        # items and listable_objects() should be []
        itemlist = ItemList()
        itemlist.build()

        self.assertItemsEqual(
            itemlist.items,
            itemlist.model.objects.listable_objects()
            )
        self.assertItemsEqual(itemlist.items, [])

    def test_build_items(self):
        # build() should assign all objects to items
        item = TestModel(in_lists=True, published=True)
        item.save()

        itemlist = ItemList()
        itemlist.build()

        self.assertItemsEqual(
            itemlist.items,
            itemlist.model.objects.listable_objects()
            )
        self.assertItemsEqual(itemlist.items, [item])


class ListSetItemsTests(TestCase):
    def setUp(self):
        self.school = Entity(name="School of Medicine")
        self.school.save()

        self.item1 = TestModel(title="1")
        self.item1.save()
        self.item2 = TestModel(title="2")
        self.item2.save()

    def test_item_not_for_entity_is_not_listed(self):
        # the object is not for this entity, should not be in items
        itemlist = ItemList(entity=self.school)
        itemlist.items = TestModel.objects.all()

        itemlist.set_items_for_entity()

        self.assertItemsEqual(
            itemlist.items,
            []
            )

    def test_hosted_by_item_is_listed(self):
        # object is hosted_by, should be published
        self.item1.hosted_by = self.school
        self.item1.save()
        itemlist = ItemList(entity=self.school)
        itemlist.items = TestModel.objects.all()

        itemlist.set_items_for_entity()

        self.assertItemsEqual(
            itemlist.items,
            [self.item1]
            )

    def test_set_items_for_entity_in_publish_to(self):
        # object has publish_to, should be published
        self.item1.publish_to.add(self.school)
        itemlist = ItemList(entity=self.school)
        itemlist.items = TestModel.objects.all()

        itemlist.set_items_for_entity()

        self.assertItemsEqual(
            itemlist.items,
            [self.item1]
            )

    def test_set_items_for_entity_wrong_entity(self):
        # the object is different entity, should not be in items
        itemlist = ItemList(entity=100)
        itemlist.items = TestModel.objects.all()

        itemlist.set_items_for_entity()

        self.assertItemsEqual(
            itemlist.items,
            []
            )

    def test_set_items_for_person(self):
        p = Person()
        p.save()
        self.item1.please_contact.add(p)

        itemlist = ItemList()
        itemlist.items = TestModel.objects.all()
        itemlist.person = p
        itemlist.set_items_for_person()

        self.assertEqual(
            list(itemlist.items),
            [self.item1]
        )


class FilterListTests(TestCase):
    def setUp(self):
        self.item1 = TestModel(title="1")
        self.item2 = TestModel(title="2")
        self.item3 = TestModel(title="3", summary="1")
        self.item1.save()
        self.item2.save()
        self.item3.save()

        self.itemlist = ItemList()
        self.itemlist.search_fields = [
            {
                "field_name": "text",
                "field_label": "Title/summary",
                "placeholder": "Search",
                "search_keys": [
                    "title__icontains",
                    "summary__icontains",
                    ],
                },
            ]
        self.itemlist.items = TestModel.objects.all()
        self.itemlist.request = HttpRequest()

    def test_filter_on_search_terms_no_matches(self):
        query = QueryDict('text=4')
        self.itemlist.request.GET = query
        self.itemlist.filter_on_search_terms()
        self.assertItemsEqual(
            self.itemlist.items,
            []
            )

    def test_filter_on_search_terms_matches_1(self):
        query = QueryDict('text=2')
        self.itemlist.request.GET = query
        self.itemlist.filter_on_search_terms()
        self.assertItemsEqual(
            self.itemlist.items,
            [self.item2]
            )

    def test_filter_on_search_terms_matches_2(self):
        query = QueryDict('text=1')
        self.itemlist.request.GET = query
        self.itemlist.filter_on_search_terms()
        self.assertItemsEqual(
            self.itemlist.items,
            [self.item1, self.item3]
            )


class ListShowWhenTests(TestCase):
    def test_no_show_when(self):
        item1 = TestModel()
        item2 = TestModel()
        item3 = TestModel()

        itemlist = ItemList()
        itemlist.group_dates = True
        itemlist.items = [item1, item2, item3]
        itemlist.set_show_when()

        self.assertFalse(itemlist.show_when)

    def test_show_when(self):
        item1 = TestModel()
        item2 = TestModel()
        item3 = TestModel()

        item1.get_when = 1
        item2.get_when = 2
        item3.get_when = 3

        itemlist = ItemList()
        itemlist.group_dates = True
        itemlist.items = [item1, item2, item3]
        itemlist.set_show_when()

        self.assertTrue(itemlist.show_when)


class ListTruncateItems(TestCase):
    # truncate_items() should use .count() on querysets and len() on lists
    # it should act on the order_by attribute of the List
    def setUp(self):
        self.item1 = TestModel(title="1")
        self.item1.save()
        self.item2 = TestModel(title="2")
        self.item2.save()
        self.itemlist = ItemList()
        self.itemlist.items = TestModel.objects.all()

    def test_stays_a_queryset(self):
        self.itemlist.order_by = "date"
        self.itemlist.limit_to = 2
        self.itemlist.truncate_items()

        self.assertIsNone(self.itemlist.items._result_cache)
        self.assertEqual(list(self.itemlist.items), [self.item1, self.item2])

    def test_becomes_a_list(self):
        self.itemlist.order_by = "importance/date"
        self.itemlist.limit_to = 2
        self.itemlist.truncate_items()

        self.assertIsNotNone(self.itemlist.items._result_cache)
        self.assertEqual(list(self.itemlist.items), [self.item1, self.item2])


class ListIsShowable(TestCase):
    def test_is_showable(self):
        self.itemlist = ItemList()
        self.itemlist.items = TestModel.objects.all()

        self.assertFalse(self.itemlist.is_showable())

        self.item1 = TestModel(title="1")
        self.item1.save()
        self.itemlist.items = TestModel.objects.all()
        self.assertTrue(self.itemlist.is_showable())

        self.itemlist.items = [1, 2, 3]
        self.assertTrue(self.itemlist.is_showable())


class ListerTests(TestCase):

    def test_empty_lists_do_not_appear_in_lister(self):
        lister = ArkestraGenericLister(
            listkinds=[
                ("list1", ItemList)
            ],
            display="list1"
        )

        self.assertEqual(
            lister.lists, []
        )




# these classes and the FilterSetTests check that ArkestraGenericFilterSet
# does not inadvertantly get interfered with
class BasicFilterSet(ArkestraGenericFilterSet):
    pass


class BasicList(ArkestraGenericFilterList):
    model = TestModel
    filter_set = BasicFilterSet


class BasicGenericList(ArkestraGenericFilterList):
    model = TestModel


class FilterSetTests(TestCase):

    def test_filter_has_correct_fields(self):
        self.assertItemsEqual(BasicGenericList.filter_set.fields, [])

    def test_filter_has_correct_fields(self):
        self.assertItemsEqual(BasicList.filter_set.fields, [])
