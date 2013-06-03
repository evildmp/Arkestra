from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from django.conf import settings
from django.contrib.auth.models import User

# we're testing the behaviour of a method that uses date-related functions
from datetime import datetime, timedelta

from cms.api import create_page

from news_and_events.models import NewsArticle
from contacts_and_people.models import Entity

@override_settings(
    USE_TZ = False
)


class NewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        
        # self.school = Entity(
        #     name="School of Medicine", 
        #     slug="medicine",
        #     )
        # self.school.save()

        # create a news item
        self.tootharticle = NewsArticle(
            title = "All about teeth",
            slug = "all-about-teeth",
            date = datetime.now(),
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
            
@override_settings(
    CMS_TEMPLATES = (('null.html', "Null"),)
)
class NewsEventsItemsViewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        
        # create a news item
        self.tootharticle = NewsArticle(
            title = "All about teeth",
            slug = "all-about-teeth"
            )
        
        self.adminuser = User.objects.create_user('arkestra', 'arkestra@example.com', 'arkestra')
        self.adminuser.is_staff=True
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
    
@override_settings(
    CMS_TEMPLATES = (('null.html', "Null"),)
)
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
    def test_news_and_events_main_url(self):
        self.school.save()
        response = self.client.get('/news-and-events/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events_entity_url(self):
        self.school.save()
        response = self.client.get('/news-and-events/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/news-and-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_main_archive_url(self):
        self.school.save()
        response = self.client.get('/news-archive/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events_entity__news_archive_url(self):
        self.school.save()
        response = self.client.get('/news-archive/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events_bogus_entity_news_archive_url(self):
        self.school.save()
        response = self.client.get('/news-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_main_previous_events_url(self):
        self.school.save()
        response = self.client.get('/previous-events/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events_entity_previous_events_url(self):
        self.school.save()
        response = self.client.get('/previous-events/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events_bogus_entity_events_archive_url(self):
        self.school.save()
        response = self.client.get('/previous-events/xxxx/')
        self.assertEqual(response.status_code, 404)
        
    def test_news_and_events_main_forthcoming_events_url(self):
        self.school.save()
        response = self.client.get('/forthcoming-events/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events_entity_forthcoming_events_url(self):
        self.school.save()
        response = self.client.get('/forthcoming-events/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events_bogus_entity_forthcoming_events_url(self):
        self.school.save()
        response = self.client.get('/forthcoming-events/xxx/')
        self.assertEqual(response.status_code, 404)

    # entity news and events URLs - no news and events pages
    def test_news_and_events_no_auto_page_main_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/news-and-events/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_entity_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/news-and-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_bogus_entity_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/news-and-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_main_archive_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/news-archive/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_entity__news_archive_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/news-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_bogus_entity_news_archive_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/news-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_main_previous_events_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/previous-events/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_entity_previous_events_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/previous-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_bogus_entity_events_archive_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/previous-events/xxxx/')
        self.assertEqual(response.status_code, 404)
        
    def test_news_and_events_no_auto_page_main_forthcoming_events_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/forthcoming-events/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_entity_forthcoming_events_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/forthcoming-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_auto_page_bogus_entity_forthcoming_events_url(self):
        self.school.auto_news_page= False
        self.school.save()
        response = self.client.get('/forthcoming-events/xxx/')
        self.assertEqual(response.status_code, 404)

    # entity news and events URLs - no entity home page
    def test_news_and_events_no_entity_home_page_main_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-and-events/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_entity_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-and-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_bogus_entity_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-and-events/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_main_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-archive/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_entity__news_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_bogus_entity_news_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/news-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_main_previous_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/previous-events/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_entity_previous_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/previous-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_bogus_entity_events_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/previous-events/xxxx/')
        self.assertEqual(response.status_code, 404)
        
    def test_news_and_events_no_entity_home_page_main_forthcoming_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/forthcoming-events/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_entity_forthcoming_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/forthcoming-events/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_news_and_events_no_entity_home_page_bogus_entity_forthcoming_events_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/forthcoming-events/xxx/')
        self.assertEqual(response.status_code, 404)

