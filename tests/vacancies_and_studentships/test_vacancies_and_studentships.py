from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpRequest, QueryDict

from cms.api import create_page

from contacts_and_people.models import Person

from vacancies_and_studentships.models import Vacancy, Studentship
from vacancies_and_studentships.lister import (
    List, VacanciesAndStudentshipsPluginLister, FilterList
    )

from contacts_and_people.models import Entity

from arkestra_utilities.utilities import get_fallback_template


class VacanciesTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        self.toothjob = Vacancy(
            title = "Pulling teeth",
            slug = "pulling-teeth",
            date = datetime.now() + timedelta(days=30),
            )

    def test_generic_attributes(self):
        self.toothjob.save()
        # the item has no informative content
        self.assertEqual(self.toothjob.is_uninformative, True)

        # there are no Entities in the database, so this can't be hosted_by anything
        self.assertEqual(self.toothjob.hosted_by, None)

        # since there are no Entities in the database, default to settings's template
        self.assertEqual(self.toothjob.get_template, get_fallback_template())

    def test_date_related_attributes(self):
        self.toothjob.date = datetime(year=2012, month=12, day=12)
        self.assertEqual(self.toothjob.get_when, "December 2012")

    def test_link_to_more(self):
        self.assertEqual(
            self.toothjob.auto_page_view_name,
            "vacancies-and-studentships"
            )
        self.toothjob.hosted_by = Entity(slug="slug")
        self.assertEqual(
            self.toothjob.link_to_more(),
            "/vacancies-and-studentships/slug/"
            )


@override_settings(CMS_TEMPLATES = (('null.html', "Null"),))
class VacanciesItemsViewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        # create a vacancy item
        self.toothjob = Vacancy(
            title = "Pulling teeth",
            slug = "pulling-teeth",
            date = datetime.now() + timedelta(days=30),
            )

        self.adminuser = User.objects.create_user('arkestra', 'arkestra@example.com', 'arkestra')
        self.adminuser.is_staff=True
        self.adminuser.save()

    # vacancy tests
    def test_unpublished_vacancy_404(self):
        self.toothjob.save()

        # Issue a GET request.
        response = self.client.get('/vacancy/pulling-teeth/')

        # Check that the response is 404 because it's not published
        self.assertEqual(response.status_code, 404)

    def test_unpublished_vacancy_200_for_admin(self):
        self.toothjob.save()

        # log in a staff user
        self.client.login(username='arkestra', password='arkestra')
        response = self.client.get('/vacancy/pulling-teeth/')
        self.assertEqual(response.status_code, 200)

    def test_published_vacancy_200_for_everyone(self):
        self.toothjob.published = True
        self.toothjob.save()

        # Check that the response is 200 OK.
        response = self.client.get('/vacancy/pulling-teeth/')
        self.assertEqual(response.status_code, 200)

    def test_published_vacancy_context(self):
        self.toothjob.published = True
        self.toothjob.save()
        response = self.client.get('/vacancy/pulling-teeth/')
        self.assertEqual(response.context['vacancy'], self.toothjob)


@override_settings(CMS_TEMPLATES = (('null.html', "Null"),))
class StudentshipsItemsViewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        # create a studentship item
        self.toothjob = Studentship(
            title = "Pulling teeth",
            slug = "pulling-teeth",
            date = datetime.now() + timedelta(days=30),
            )

        self.adminuser = User.objects.create_user('arkestra', 'arkestra@example.com', 'arkestra')
        self.adminuser.is_staff=True
        self.adminuser.save()

    # studentship tests
    def test_unpublished_studentship_404(self):
        self.toothjob.save()

        # Issue a GET request.
        response = self.client.get('/studentship/pulling-teeth/')

        # Check that the response is 404 because it's not published
        self.assertEqual(response.status_code, 404)

    def test_unpublished_studentship_200_for_admin(self):
        self.toothjob.save()

        # log in a staff user
        self.client.login(username='arkestra', password='arkestra')
        response = self.client.get('/studentship/pulling-teeth/')
        self.assertEqual(response.status_code, 200)

    def test_published_studentship_200_for_everyone(self):
        self.toothjob.published = True
        self.toothjob.save()

        # Check that the response is 200 OK.
        response = self.client.get('/studentship/pulling-teeth/')
        self.assertEqual(response.status_code, 200)

    def test_published_studentship_context(self):
        self.toothjob.published = True
        self.toothjob.save()
        response = self.client.get('/studentship/pulling-teeth/')
        self.assertEqual(response.context['studentship'], self.toothjob)


class ReverseURLsTests(TestCase):
    def test_vacancy_reverse_url(self):
        self.assertEqual(
            reverse("vacancy", kwargs={"slug": "tooth-puller"}),
            "/vacancy/tooth-puller/"
            )

    def test_studentship_reverse_url(self):
        self.assertEqual(
            reverse("studentship", kwargs={"slug": "tooth-puller"}),
            "/studentship/tooth-puller/"
            )

    def test_archived_vacancies_base_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-archive"),
            "/archived-vacancies/"
            )

    def test_archived_vacancies_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-archive", kwargs={"slug": "some-slug"}),
            "/archived-vacancies/some-slug/"
            )

    def test_current_vacancies_base_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-current"),
            "/vacancies/"
            )

    def test_current_vacancies_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-current", kwargs={"slug": "some-slug"}),
            "/vacancies/some-slug/"
            )

    def test_archived_studentships_base_reverse_url(self):
        self.assertEqual(
            reverse("studentships-archive"),
            "/archived-studentships/"
            )

    def test_archived_studentships_reverse_url(self):
        self.assertEqual(
            reverse("studentships-archive", kwargs={"slug": "some-slug"}),
            "/archived-studentships/some-slug/"
            )

    def test_current_studentships_base_reverse_url(self):
        self.assertEqual(
            reverse("studentships-current"),
            "/studentships/"
            )

    def test_current_studentships_reverse_url(self):
        self.assertEqual(
            reverse("studentships-current", kwargs={"slug": "some-slug"}),
            "/studentships/some-slug/"
            )

    def test_base_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-and-studentships"),
            "/vacancies-and-studentships/"
            )

    def test_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-and-studentships", kwargs={"slug": "some-slug"}),
            "/vacancies-and-studentships/some-slug/"
            )


@override_settings(CMS_TEMPLATES = (('null.html', "Null"),))
class VacanciesStudentshipsEntityPagesViewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        home_page = create_page(
            "School home page",
            "null.html",
            "en",
            published=True
            )

        self.school = Entity(
            name="School of Medicine",
            slug="medicine",
            auto_vacancies_page=True,
            website=home_page
            )


    # entity vacancies and studentships URLs - has vacancies and studentships pages
    def test_main_url(self):
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/')
        self.assertEqual(response.status_code, 200)

    def test_entity_url(self):
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_main_archive_url(self):
        self.school.save()
        response = self.client.get('/archived-vacancies/')
        self.assertEqual(response.status_code, 200)

    def test_entity_vacancies_archive_url(self):
        self.school.save()
        response = self.client.get('/archived-vacancies/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_vacancies_archive_url(self):
        self.school.save()
        response = self.client.get('/archived-vacancies/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_main_archived_studentships_url(self):
        self.school.save()
        response = self.client.get('/archived-studentships/')
        self.assertEqual(response.status_code, 200)

    def test_entity_archived_studentships_url(self):
        self.school.save()
        response = self.client.get('/archived-studentships/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_archived_studentships_url(self):
        self.school.save()
        response = self.client.get('/archived-studentships/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_main_all_current_studentships_url(self):
        self.school.save()
        response = self.client.get('/studentships/')
        self.assertEqual(response.status_code, 200)

    def test_entity_all_current_studentships_url(self):
        self.school.save()
        response = self.client.get('/studentships/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_all_current_studentships_url(self):
        self.school.save()
        response = self.client.get('/current-studentships/xxx/')
        self.assertEqual(response.status_code, 404)

    # entity vacancies and studentships URLs - no vacancies and studentships pages
    def test_no_auto_page_main_url(self):
        self.school.auto_vacancies_page = False
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_main_archive_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/archived-vacancies/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_vacancies_archive_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/archived-vacancies/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_vacancies_archive_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/archived-vacancies/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_main_archived_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/studentships-archive/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_archived_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/studentships-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_archived_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/studentships-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_main_all_current_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/current-studentships/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_all_current_studentships_url(self):
        self.school.auto_vacancies_page = False
        self.school.save()
        response = self.client.get('/current-studentships/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_all_current_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/current-studentships/xxx/')
        self.assertEqual(response.status_code, 404)

    # entity vacancies and studentships URLs - no entity home page
    def test_no_entity_home_page_main_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_entity_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_bogus_entity_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_main_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/archived-vacancies/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_entity_vacancies_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/archived-vacancies/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_bogus_entity_vacancies_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/archived-vacancies/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_main_archived_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/studentships-archive/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_entity_archived_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/studentships-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_bogus_entity_archived_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/studentships-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_main_all_current_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/current-studentships/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_entity_all_current_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/current-studentships/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_bogus_entity_all_current_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/current-studentships/xxx/')
        self.assertEqual(response.status_code, 404)


class ListTests(TestCase):
    def setUp(self):
        self.item1 = Vacancy(
            title="closes today, less important",
            in_lists=True,
            published=True,
            date=datetime.now()
            )
        self.item1.save()

        self.item2 = Vacancy(
            title="closed 20 days ago, important",
            summary="a job for today",
            in_lists=True,
            published=True,
            date=datetime.now()-timedelta(days=20),
            importance=3,
            slug="item2"
            )
        self.item2.save()

        self.item3 = Vacancy(
            title="closes in the future",
            in_lists=True,
            published=True,
            date=datetime.now()+timedelta(days=20),
            importance=3,
            slug="item3"
            )
        self.item3.save()

        self.itemlist = List()
        self.itemlist.model = Vacancy
        self.itemlist.items = Vacancy.objects.all()

    def test_all_items_order(self):
        self.assertEqual(
            list(self.itemlist.items),
            [self.item2, self.item1, self.item3]
            )

    def test_reorder_by_importance_date_only(self):
        # check the re-ordered items are not changed
        self.itemlist.re_order_by_importance()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item2, self.item1, self.item3]
            )

    def test_reorder_by_importance_date_makes_no_difference(self):
        # check that items are re-ordered by importance
        self.itemlist.order_by = "importance/date"
        self.itemlist.re_order_by_importance()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item2, self.item1, self.item3]
            )

    def test_truncate_items(self):
        # check that items are re-ordered by importance
        self.itemlist.limit_to = 1
        self.itemlist.truncate_items()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item2]
            )

    def test_set_items_for_person(self):
        p = Person()
        p.save()
        self.item1.please_contact.add(p)

        self.itemlist.person = p
        self.itemlist.set_items_for_person()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item1]
        )

    def test_build(self):
        self.itemlist.build()
        self.assertEqual(list(self.itemlist.items), [self.item1, self.item3])

    def test_other_items(self):
        school = Entity(name="School of Medicine", short_name="Medicine")
        school.save()

        self.itemlist.entity = school
        self.itemlist.other_item_kinds = ["archived", "open", "main"]

        self.itemlist.build()

        # "main" other items are always created; the others need tests to
        # see if any exist
        self.assertEqual(
            self.itemlist.other_items(),
            [{
                'link': '/vacancies-and-studentships/',
                'title': u'Medicine vacancies & studentships',
                'css_class': 'main',
                }]
            )

        # now we save some items
        self.item1.hosted_by = school
        self.item2.hosted_by = school
        self.item3.hosted_by = school
        self.item1.save()
        self.item2.save()
        self.item3.save()

        self.itemlist.build()
        self.assertEqual(list(self.itemlist.items), [self.item1, self.item3])
        self.assertEqual(list(self.itemlist.archived), [self.item2])
        self.assertEqual(
            list(self.itemlist.other_items()),
            [{
                'count': 2,
                'link': '/vacancies/',
                'title': 'All open vacancies'
                },
            {
                'count': 1,
                'link': '/archived-vacancies/',
                'title': 'Archived vacancies'
                },
            {
                'link': '/vacancies-and-studentships/',
                'title': u'Medicine vacancies & studentships',
                'css_class': 'main',
                },
            ]
            )


class FilterListTests(TestCase):
    def setUp(self):
        self.item1 = Vacancy(
            title="closes today, less important",
            in_lists=True,
            published=True,
            date=datetime.now()
            )
        self.item1.save()

        self.item2 = Vacancy(
            title="closed 20 days ago, important",
            summary="a job for today",
            in_lists=True,
            published=True,
            date=datetime.now()-timedelta(days=20),
            importance=3,
            slug="item2"
            )
        self.item2.save()

        self.item3 = Vacancy(
            title="closes in the future",
            in_lists=True,
            published=True,
            date=datetime.now()+timedelta(days=20),
            importance=3,
            slug="item3"
            )
        self.item3.save()

        self.itemlist = FilterList()
        self.itemlist.model = Vacancy
        self.itemlist.request = HttpRequest()

    def test_filter_on_search_terms_no_terms(self):
        query = QueryDict("")
        self.itemlist.request.GET = query
        self.itemlist.build()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item1, self.item3]
            )

    def test_filter_on_search_terms_1_match(self):
        query = QueryDict("text=today")
        self.itemlist.request.GET = query
        self.itemlist.build()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item1]
            )


class PluginListerTests(TestCase):
    def test_other_items(self):
        lister = VacanciesAndStudentshipsPluginLister(
            entity=Entity(slug="test")
            )

        self.assertItemsEqual(
            lister.other_items(),
            [{
                'css_class': 'main',
                'link': '/vacancies-and-studentships/test/',
                'title': 'More '
            }]
        )

