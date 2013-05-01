from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    
    # vacancies and studentships items
    url(r"^vacancy/(?P<slug>[-\w]+)/$", views.vacancy, name="vacancy"),
    url(r"^studentship/(?P<slug>[-\w]+)/$", views.studentship, name="studentship"),
    
    # entities' vacancies and studentships
    url(r'^archived-vacancies/(?:(?P<slug>[-\w]+)/)?$', views.archived_vacancies, name="archived_vacancies"),
    url(r'^all-open-vacancies/(?:(?P<slug>[-\w]+)/)?$', views.all_current_vacancies, name="all_current_vacancies"),
    url(r'^archived-studentships/(?:(?P<slug>[-\w]+)/)?$', views.archived_studentships, name="archived_studentships"),
    url(r"^all-open-studentships/(?:(?P<slug>[-\w]+)/)?$", views.all_current_studentships, name="all_current_studentships"),
    url(r"^vacancies-and-studentships/(?:(?P<slug>[-\w]+)/)?$", views.vacancies_and_studentships, name="vacancies_and_studentships"),
    )
    