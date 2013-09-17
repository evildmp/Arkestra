from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# we're testing the behaviour of a method that uses date-related functions
import datetime

from cms.api import create_page

from models import Vacancy, Studentship
from contacts_and_people.models import Entity

class VacanciesTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        
        self.toothjob = Vacancy(
            title = "Pulling teeth",
            slug = "pulling-teeth",
            date = datetime.datetime.now() + datetime.timedelta(days=30),
            )

    def test_generic_attributes(self):
        self.toothjob.save()
        # the item has no informative content
        self.assertEqual(self.toothjob.is_uninformative, True)
        
        # there are no Entities in the database, so this can't be hosted_by anything
        self.assertEqual(self.toothjob.hosted_by, None)

        # since there are no Entities in the database, default to settings's template
        self.assertEqual(self.toothjob.get_template, settings.CMS_TEMPLATES[0][0])

    def test_date_related_attributes(self):
        self.toothjob.date = datetime.datetime(year=2012, month=12, day=12)
        self.assertEqual(self.toothjob.get_when, "December 2012")
            
@override_settings(CMS_TEMPLATES = (('null.html', "Null"),))
class VacanciesItemsViewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        
        # create a vacancy item
        self.toothjob = Vacancy(
            title = "Pulling teeth",
            slug = "pulling-teeth",
            date = datetime.datetime.now() + datetime.timedelta(days=30),
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
            date = datetime.datetime.now() + datetime.timedelta(days=30),
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
            reverse("vacancies-archive-base"),
            "/archived-vacancies/"
            )

    def test_archived_vacancies_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-archive", kwargs={"slug": "some-slug"}),
            "/archived-vacancies/some-slug/"
            )

    def test_current_vacancies_base_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-current-base"),
            "/vacancies/"
            )

    def test_current_vacancies_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-current", kwargs={"slug": "some-slug"}),
            "/vacancies/some-slug/"
            )

    def test_archived_studentships_base_reverse_url(self):
        self.assertEqual(
            reverse("studentships-archive-base"),
            "/archived-studentships/"
            )

    def test_archived_studentships_reverse_url(self):
        self.assertEqual(
            reverse("studentships-archive", kwargs={"slug": "some-slug"}),
            "/archived-studentships/some-slug/"
            )

    def test_current_studentships_base_reverse_url(self):
        self.assertEqual(
            reverse("studentships-current-base"),
            "/studentships/"
            )

    def test_current_studentships_reverse_url(self):
        self.assertEqual(
            reverse("studentships-current", kwargs={"slug": "some-slug"}),
            "/studentships/some-slug/"
            )

    def test_vacancies_and_studentships_base_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-and-studentships-base"),
            "/vacancies-and-studentships/"
            )

    def test_vacancies_and_studentships_reverse_url(self):
        self.assertEqual(
            reverse("vacancies-and-studentships", kwargs={"slug": "some-slug"}),
            "/vacancies-and-studentships/some-slug/"
            )


@override_settings(
    CMS_TEMPLATES = (('null.html', "Null"),)
)
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
    def test_vacancies_and_studentships_main_url(self):
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_and_studentships_entity_url(self):
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_and_studentships_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_main_archive_url(self):
        self.school.save()
        response = self.client.get('/archived-vacancies/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_and_studentships_entity_vacancies_archive_url(self):
        self.school.save()
        response = self.client.get('/archived-vacancies/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_and_studentships_bogus_entity_vacancies_archive_url(self):
        self.school.save()
        response = self.client.get('/archived-vacancies/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_main_archived_studentships_url(self):
        self.school.save()
        response = self.client.get('/archived-studentships/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_and_studentships_entity_archived_studentships_url(self):
        self.school.save()
        response = self.client.get('/archived-studentships/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_and_studentships_bogus_entity_archived_studentships_url(self):
        self.school.save()
        response = self.client.get('/archived-studentships/xxxx/')
        self.assertEqual(response.status_code, 404)
        
    def test_vacancies_and_studentships_main_all_current_studentships_url(self):
        self.school.save()
        response = self.client.get('/studentships/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_and_studentships_entity_all_current_studentships_url(self):
        self.school.save()
        response = self.client.get('/studentships/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_and_studentships_bogus_entity_all_current_studentships_url(self):
        self.school.save()
        response = self.client.get('/current-studentships/xxx/')
        self.assertEqual(response.status_code, 404)

    # entity vacancies and studentships URLs - no vacancies and studentships pages
    def test_vacancies_and_studentships_no_auto_page_main_url(self):
        self.school.auto_vacancies_page = False
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_entity_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_bogus_entity_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_main_archive_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/archived-vacancies/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_entity_vacancies_archive_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/archived-vacancies/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_bogus_entity_vacancies_archive_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/archived-vacancies/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_main_archived_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/studentships-archive/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_entity_archived_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/studentships-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_bogus_entity_archived_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/studentships-archive/xxxx/')
        self.assertEqual(response.status_code, 404)
        
    def test_vacancies_and_studentships_no_auto_page_main_all_current_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/current-studentships/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_entity_all_current_studentships_url(self):
        self.school.auto_vacancies_page = False
        self.school.save()
        response = self.client.get('/current-studentships/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_auto_page_bogus_entity_all_current_studentships_url(self):
        self.school.auto_vacancies_page= False
        self.school.save()
        response = self.client.get('/current-studentships/xxx/')
        self.assertEqual(response.status_code, 404)

    # entity vacancies and studentships URLs - no entity home page
    def test_vacancies_and_studentships_no_entity_home_page_main_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_entity_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_bogus_entity_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/vacancies-and-studentships/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_main_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/archived-vacancies/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_entity_vacancies_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/archived-vacancies/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_bogus_entity_vacancies_archive_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/archived-vacancies/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_main_archived_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/studentships-archive/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_entity_archived_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/studentships-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_bogus_entity_archived_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/studentships-archive/xxxx/')
        self.assertEqual(response.status_code, 404)
        
    def test_vacancies_and_studentships_no_entity_home_page_main_all_current_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/current-studentships/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_entity_all_current_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/current-studentships/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_vacancies_and_studentships_no_entity_home_page_bogus_entity_all_current_studentships_url(self):
        self.school.website = None
        self.school.save()
        response = self.client.get('/current-studentships/xxx/')
        self.assertEqual(response.status_code, 404)

