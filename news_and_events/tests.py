from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from django.conf import settings
from django.core.urlresolvers import resolve, reverse
from django.contrib.auth.models import User
from django.http import HttpRequest, QueryDict

from cms.api import create_page

from news_and_events.models import NewsArticle, Event
from news_and_events.lister import (
    NewsAndEventsPluginLister, NewsList, NewsListArchive,
    EventsList, EventsFilterList
    )
from contacts_and_people.models import Entity, Person, Building, Site


@override_settings(USE_TZ=False)
class NewsTests(TestCase):
    def setUp(self):
        # create a news item
        self.tootharticle = NewsArticle(
            title="All about teeth",
            slug="all-about-teeth",
            date=datetime.now(),
            )

    def test_generic_attributes(self):
        self.tootharticle.save()
        # the item has no informative content
        self.assertEqual(self.tootharticle.is_uninformative, True)

        # no Entities in the database, so this can't be hosted_by anything
        self.assertEqual(self.tootharticle.hosted_by, None)

        #  no Entities in the database, so default to settings's template
        self.assertEqual(
            self.tootharticle.get_template,
            settings.CMS_TEMPLATES[0][0]
            )

    def test_date_related_attributes(self):
        self.tootharticle.date = datetime(year=2012, month=12, day=12)
        self.assertEqual(self.tootharticle.get_when, "December 2012")

    def test_link_to_more(self):
        self.assertEqual(
            self.tootharticle.auto_page_view_name,
            "news-and-events"
            )
        self.tootharticle.hosted_by = Entity(slug="slug")
        self.assertEqual(
            self.tootharticle.link_to_more(),
            "/news-and-events/slug/"
            )


@override_settings(CMS_TEMPLATES=(('null.html', "Null"),))
class NewsEventsItemsViewsTests(TestCase):
    def setUp(self):
        # create a news item
        self.tootharticle = NewsArticle(
            title="All about teeth",
            slug="all-about-teeth"
            )

        self.adminuser = User.objects.create_user(
            'arkestra',
            'arkestra@example.com',
            'arkestra'
            )
        self.adminuser.is_staff = True
        self.adminuser.save()

    # news article tests
    def test_unpublished_newsarticle_404(self):
        self.tootharticle.save()

        # Issue a GET request.
        response = self.client.get('/news/all-about-teeth/')

        # Check that the response is 404 because it's not published
        self.assertEqual(response.status_code, 404)

    def test_unpublished_newsarticle_200_for_admin(self):
        self.tootharticle.save()

        # log in a staff user
        self.client.login(username='arkestra', password='arkestra')
        response = self.client.get('/news/all-about-teeth/')
        self.assertEqual(response.status_code, 200)

    def test_published_newsarticle_200_for_everyone(self):
        self.tootharticle.published = True
        self.tootharticle.save()

        # Check that the response is 200 OK.
        response = self.client.get('/news/all-about-teeth/')
        self.assertEqual(response.status_code, 200)

    def test_published_newsarticle_context(self):
        self.tootharticle.published = True
        self.tootharticle.save()
        response = self.client.get('/news/all-about-teeth/')
        self.assertEqual(response.context['newsarticle'], self.tootharticle)


class ResolveURLsTests(TestCase):
    def test_resolve_news_and_events_base_entity(self):
        resolver = resolve('/news-and-events/')
        self.assertEqual(resolver.view_name, "news-and-events")

    def test_resolve_news_and_events_named_entity(self):
        resolver = resolve('/news-and-events/slug/')
        self.assertEqual(resolver.view_name, "news-and-events")

    def test_resolve_news_archive_base_entity(self):
        resolver = resolve('/news-archive/')
        self.assertEqual(resolver.view_name, "news-archive")

    def test_resolve_news_archive_named_entity(self):
        resolver = resolve('/news-archive/slug/')
        self.assertEqual(resolver.view_name, "news-archive")

    def test_resolve_events_archive_base_entity(self):
        resolver = resolve('/previous-events/')
        self.assertEqual(resolver.view_name, "events-archive")

    def test_resolve_events_archive_named_entity(self):
        resolver = resolve('/previous-events/slug/')
        self.assertEqual(resolver.view_name, "events-archive")

    def test_resolve_events_forthcoming_base_entity(self):
        resolver = resolve('/forthcoming-events/')
        self.assertEqual(resolver.view_name, "events-forthcoming")

    def test_resolve_events_forthcoming_named_entity(self):
        resolver = resolve('/forthcoming-events/slug/')
        self.assertEqual(resolver.view_name, "events-forthcoming")


class ReverseURLsTests(TestCase):
    def test_newsarticle_reverse_url(self):
        self.assertEqual(
            reverse("news", kwargs={"slug": "all-about-teeth"}),
            "/news/all-about-teeth/"
            )

    def test_event_reverse_url(self):
        self.assertEqual(
            reverse("event", kwargs={"slug": "all-about-teeth"}),
            "/event/all-about-teeth/"
            )

    def test_news_archive_base_reverse_url(self):
        self.assertEqual(
            reverse("news-archive"),
            "/news-archive/"
            )

    def test_news_archive_slug_reverse_url(self):
        self.assertEqual(
            reverse("news-archive", kwargs={"slug": "some-slug"}),
            "/news-archive/some-slug/"
            )

    def test_previous_events_base_reverse_url(self):
        self.assertEqual(
            reverse("events-archive"),
            "/previous-events/"
            )

    def test_previous_events_reverse_url(self):
        self.assertEqual(
            reverse("events-archive", kwargs={"slug": "some-slug"}),
            "/previous-events/some-slug/"
            )

    def test_forthcoming_events_base_reverse_url(self):
        self.assertEqual(
            reverse("events-forthcoming"),
            "/forthcoming-events/"
            )

    def test_forthcoming_events_reverse_url(self):
        self.assertEqual(
            reverse("events-forthcoming", kwargs={"slug": "some-slug"}),
            "/forthcoming-events/some-slug/"
            )

    def test_base_reverse_url(self):
        self.assertEqual(
            reverse("news-and-events"),
            "/news-and-events/"
            )

    def test_reverse_url(self):
        self.assertEqual(
            reverse("news-and-events", kwargs={"slug": "some-slug"}),
            "/news-and-events/some-slug/"
            )


@override_settings(CMS_TEMPLATES=(('null.html', "Null"),))
class NewsEventsEntityPagesViewsTests(TestCase):
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
            auto_news_page=True,
            website=home_page
            )

    # entity news and events URLs - has news and events pages
    def test_main_url(self):
        self.school.save()
        response = self.client.get('/news-and-events/')
        self.assertEqual(response.status_code, 200)

    def test_entity_url(self):
        self.school.save()
        response = self.client.get('/news-and-events/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/news-and-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_main_archive_url(self):
        self.school.save()
        response = self.client.get('/news-archive/')
        self.assertEqual(response.status_code, 200)

    def test_entity__news_archive_url(self):
        self.school.save()
        response = self.client.get('/news-archive/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_news_archive_url(self):
        self.school.save()
        response = self.client.get('/news-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_main_previous_events_url(self):
        self.school.save()
        response = self.client.get('/previous-events/')
        self.assertEqual(response.status_code, 200)

    def test_entity_previous_events_url(self):
        self.school.save()
        response = self.client.get('/previous-events/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_events_archive_url(self):
        self.school.save()
        response = self.client.get('/previous-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_main_forthcoming_events_url(self):
        self.school.save()
        response = self.client.get('/forthcoming-events/')
        self.assertEqual(response.status_code, 200)

    def test_entity_forthcoming_events_url(self):
        self.school.save()
        response = self.client.get('/forthcoming-events/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_forthcoming_events_url(self):
        self.school.save()
        response = self.client.get('/forthcoming-events/xxx/')
        self.assertEqual(response.status_code, 404)

    # entity news and events URLs - no news and events pages
    def test_no_auto_page_main_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/news-and-events/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/news-and-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/news-and-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_main_archive_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/news-archive/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity__news_archive_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/news-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_news_archive_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/news-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_main_previous_events_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/previous-events/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_previous_events_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/previous-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_events_archive_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/previous-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_main_forthcoming_events_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/forthcoming-events/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_forthcoming_events_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/forthcoming-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_forthcoming_events_url(self):
        self.school.auto_news_page = False
        self.school.save()
        response = self.client.get('/forthcoming-events/xxx/')
        self.assertEqual(response.status_code, 404)

    # entity news and events URLs - no entity home page
    def test_no_entity_home_page_main_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-and-events/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_entity_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-and-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_bogus_entity_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-and-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_main_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-archive/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_entity__news_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_bogus_entity_news_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_main_previous_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/previous-events/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_entity_previous_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/previous-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_bogus_entity_events_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/previous-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_main_forthcoming_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/forthcoming-events/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_entity_forthcoming_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/forthcoming-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_entity_home_page_bogus_entity_forthcoming_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/forthcoming-events/xxx/')
        self.assertEqual(response.status_code, 404)


class NewsListTests(TestCase):
    def setUp(self):
        self.item1 = NewsArticle(
            title="newer, less important",
            in_lists=True,
            published=True,
            date=datetime.now()
            )
        self.item1.save()

        self.item2 = NewsArticle(
            title="older, more important",
            in_lists=True,
            published=True,
            date=datetime.now()-timedelta(days=200),
            importance=3,
            slug="item2"
            )
        self.item2.save()

        self.itemlist = NewsList()
        self.itemlist.items = NewsArticle.objects.all()

    def test_all_items_order(self):
        # check we have both items in items
        self.assertEqual(
            list(self.itemlist.items),
            [self.item1, self.item2]
            )

    def test_remove_expired(self):
        # check that the expired item has been removed
        self.itemlist.remove_expired()

        self.assertItemsEqual(
            self.itemlist.items,
            [self.item1]
            )

    def test_reorder_by_importance_date_only(self):
        # check the re-ordered items are not changed
        self.itemlist.re_order_by_importance()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item1, self.item2]
            )

    def test_reorder_by_importance_date_and_importance(self):
        # check that items are re-ordered by importance
        self.itemlist.order_by = "importance/date"
        self.itemlist.re_order_by_importance()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item2, self.item1]
            )

    def test_truncate_items(self):
        # check that items are re-ordered by importance
        self.itemlist.order_by = "importance/date"
        self.itemlist.limit_to = 1
        self.itemlist.re_order_by_importance()
        self.itemlist.truncate_items()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item2]
            )

    def test_build(self):
        self.itemlist.build()
        self.assertEqual(list(self.itemlist.items), [self.item1])

    def test_other_items(self):
        school = Entity(name="School of Medicine")
        school.save()

        self.itemlist.entity = school
        self.itemlist.other_item_kinds = ("archive")
        self.item1.hosted_by = school
        self.item2.hosted_by = school
        self.item1.save()
        self.item2.save()

        self.itemlist.build()
        self.assertEqual(
            self.itemlist.other_items(),
            [{'count': 2, 'link': '/news-archive/', 'title': 'News archive'}]
            )


class NewsFilterListTests(TestCase):
    def setUp(self):
        self.item1 = NewsArticle(
            title="newer, less important",
            in_lists=True,
            published=True,
            date=datetime.now()
            )
        self.item1.save()

        self.item2 = NewsArticle(
            title="older, more important",
            summary="newer",
            in_lists=True,
            published=True,
            date=datetime.now()-timedelta(days=200),
            importance=3,
            slug="item2"
            )
        self.item2.save()

        self.itemlist = NewsListArchive()
        self.itemlist.items = NewsArticle.objects.all()
        self.itemlist.request = HttpRequest()

    def test_filter_on_search_terms_no_terms(self):
        query = QueryDict("")
        self.itemlist.request.GET = query
        self.itemlist.filter_on_search_terms()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item1, self.item2]
            )

    def test_filter_on_search_terms_1_match(self):
        query = QueryDict("text=ss")
        self.itemlist.request.GET = query
        self.itemlist.filter_on_search_terms()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item1]
            )

    def test_filter_on_search_terms_2_matches(self):
        query = QueryDict('text=newer')
        self.itemlist.request.GET = query
        self.itemlist.filter_on_search_terms()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item1, self.item2]
            )


class EventsListTests(TestCase):
    def setUp(self):
        self.item1 = Event(
            title="sooner, less important",
            type_id=1,
            in_lists=True,
            published=True,
            date=datetime.now()+timedelta(days=10),
            )
        self.item1.save()

        self.item2 = Event(
            title="later, more important",
            type_id=2,
            in_lists=True,
            published=True,
            date=datetime.now()+timedelta(days=20),
            single_day_event=True,
            importance=3,
            slug="item2"
            )
        self.item2.save()

        self.item3 = Event(
            title="past",
            type_id=2,
            in_lists=True,
            published=True,
            date=datetime.now()-timedelta(days=20),
            single_day_event=True,
            importance=3,
            slug="item3"
            )
        self.item3.save()

        self.item4 = Event(
            title="already started but not finished",
            type_id=3,
            in_lists=True,
            published=True,
            date=datetime.now()-timedelta(days=2),
            end_date=datetime.now()+timedelta(days=2),
            single_day_event=False,
            importance=1,
            slug="item4"
            )
        self.item4.save()

        self.item5 = Event(
            title="series",
            type_id=3,
            in_lists=True,
            published=True,
            series=True,
            importance=1,
            slug="item5"
            )
        self.item5.save()

        self.itemlist = EventsList()
        self.itemlist.items = Event.objects.all()

    def test_all_items_order(self):
        self.assertEqual(
            list(self.itemlist.items),
            [self.item5, self.item3, self.item4, self.item1, self.item2]
            )

    def test_create_item_collections(self):
        self.itemlist.create_item_collections()

        self.assertEqual(
            list(self.itemlist.actual_events),
            [self.item3, self.item4, self.item1, self.item2]
            )

        self.assertEqual(
            list(self.itemlist.forthcoming_events),
            [self.item4, self.item1, self.item2]
            )

        self.assertEqual(
            list(self.itemlist.previous_events),
            [self.item3]
            )

    def test_truncate_items(self):
        self.itemlist.create_item_collections()
        self.itemlist.limit_to = 1
        self.itemlist.truncate_items()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item3]
            )

    def test_truncate_items_forthcoming(self):
        self.itemlist.item_collections = ["forthcoming_events"]
        self.itemlist.create_item_collections()
        self.itemlist.limit_to = 2
        self.itemlist.truncate_items()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item4, self.item1]
            )

    def test_set_items_for_person_featuring(self):
        p = Person()
        p.save()
        self.item1.featuring.add(p)

        self.itemlist.person = p
        self.itemlist.set_items_for_person()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item1]
        )

    def test_set_items_for_person_contact(self):
        p = Person()
        p.save()
        self.item1.please_contact.add(p)

        self.itemlist.person = p
        self.itemlist.set_items_for_person()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item1]
        )

    def test_set_items_for_place(self):
        s = Site(id=1)
        p = Building(site=s)
        p.save()
        self.item1.building = p
        self.item1.save()

        self.itemlist.place = s
        self.itemlist.set_items_for_place()

        self.assertEqual(
            list(self.itemlist.items),
            [self.item1]
        )

    def test_other_items(self):
        school = Entity(name="School of Medicine")
        school.save()

        self.itemlist.entity = school
        self.itemlist.other_item_kinds = ("previous_events", "forthcoming_events")
        self.itemlist.build()

        # there is nothing to show in other_items()
        self.assertEqual(
            self.itemlist.other_items(),
            [],
        )

        # create some items that will count as other_items()
        self.item1.hosted_by = school
        self.item2.hosted_by = school
        self.item3.hosted_by = school
        self.item1.save()
        self.item2.save()
        self.item3.save()

        self.assertEqual(
            self.itemlist.other_items(),
            [{
                'count': 2,
                'link': '/forthcoming-events/',
                'title': 'All forthcoming events'
            },
            {
                'count': 1,
                'link': '/previous-events/',
                'title': 'Previous events'
            }]
        )


class EventsFilterListTests(TestCase):
    def setUp(self):
        self.item1 = Event(
            title="sooner, less important",
            type_id=1,
            in_lists=True,
            published=True,
            date=datetime.now()+timedelta(days=10),
            )
        self.item1.save()

        self.item2 = Event(
            title="later, more important",
            type_id=2,
            in_lists=True,
            published=True,
            date=datetime.now()+timedelta(days=20),
            single_day_event=True,
            importance=3,
            slug="item2"
            )
        self.item2.save()

        self.item3 = Event(
            title="past",
            type_id=2,
            in_lists=True,
            published=True,
            date=datetime.now()-timedelta(days=20),
            single_day_event=True,
            importance=3,
            slug="item3"
            )
        self.item3.save()

        self.item4 = Event(
            title="already started but not finished",
            summary="finished soon",
            type_id=3,
            in_lists=True,
            published=True,
            date=datetime.now()-timedelta(days=2),
            end_date=datetime.now()+timedelta(days=2),
            single_day_event=False,
            importance=1,
            slug="item4"
            )
        self.item4.save()

        self.item5 = Event(
            title="series",
            type_id=3,
            in_lists=True,
            published=True,
            series=True,
            importance=1,
            slug="item5"
            )
        self.item5.save()
        self.itemlist = EventsFilterList()
        self.itemlist.request = HttpRequest()

    def test_filter_on_search_terms_no_terms(self):
        query = QueryDict("")
        self.itemlist.request.GET = query
        self.itemlist.build()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item3, self.item4, self.item1, self.item2]
            )

    def test_filter_on_search_terms_1_match(self):
        query = QueryDict("text=past")
        self.itemlist.request.GET = query
        self.itemlist.build()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item3]
            )

    def test_filter_on_search_terms_2_matches(self):
        query = QueryDict('text=soon')
        self.itemlist.request.GET = query
        self.itemlist.build()
        self.assertEqual(
            list(self.itemlist.items),
            [self.item4, self.item1]
            )


class PluginListerTests(TestCase):

    def test_other_items(self):
        lister = NewsAndEventsPluginLister(
            entity=Entity(slug="test")
            )

        self.assertItemsEqual(
            lister.other_items(),
            [{
                'css_class': 'main',
                'link': '/news-and-events/test/',
                'title': 'More '
            }]
        )
