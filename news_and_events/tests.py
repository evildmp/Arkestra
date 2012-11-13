from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from django.conf import settings
from django.contrib.auth.models import User

# we're testing the behaviour of a method that uses date-related functions
import datetime

from models import NewsArticle
from contacts_and_people.models import Entity

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
            date = datetime.datetime.now() + datetime.timedelta(days=30),
            )
        print self.tootharticle.date
    def test_generic_attributes(self):
        self.tootharticle.save()
        # the item has no informative content
        self.assertEqual(self.tootharticle.is_uninformative, True)
        
        # there are no Entities in the database, so this can't be hosted_by anything
        self.assertEqual(self.tootharticle.hosted_by, None)

        # since there are no Entities in the database, default to settings's template
        self.assertEqual(self.tootharticle.get_template, settings.CMS_TEMPLATES[0][0])
    
class NewsEventsViewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        
        self.school = Entity(
            name="School of Medicine", 
            slug="medicine",
            )

        # create a news item
        self.tootharticle = NewsArticle(
            title = "All about teeth",
            slug = "all-about-teeth"
            )
        
        self.adminuser = User.objects.create_user('arkestra', 'arkestra@example.com', 'arkestra')
        self.adminuser.is_staff=True
        self.adminuser.save()

    def test_newsarticle_views(self):
        self.tootharticle.save()
        
        # Issue a GET request.
        response = self.client.get('/news/all-about-teeth/')  

        # Check that the response is 404 because it's not published
        self.assertEqual(response.status_code, 404)

        # log in a staff user
        self.client.login(username='arkestra', password='arkestra')        
        response = self.client.get('/news/all-about-teeth/')  
        self.assertEqual(response.status_code, 200)
        
        # log out the staff user
        self.client.logout()
        self.tootharticle.published = True
        self.tootharticle.save()
                
        # Check that the response is 200 OK.
        response = self.client.get('/news/all-about-teeth/')  
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['newsarticle'], self.tootharticle)
    
    def test_news_and_events_views_in_multiple_entity_mode(self):
        self.school.save()

        response = self.client.get('/news-and-events/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/news-and-events/medicine/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/news-and-events/xxxx/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/news-archive/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/news-archive/medicine/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/news-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/previous-events/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/previous-events/medicine/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/previous-events/xxxx/')
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get('/forthcoming-events/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/forthcoming-events/medicine/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/forthcoming-events/xxx/')
        self.assertEqual(response.status_code, 404)

