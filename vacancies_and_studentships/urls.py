from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r"^entity/(?P<slug>[-\w]+)/vacancies-and-studentships/$", "vacancies_and_studentships.views.vacancies_and_studentships"),
    (r"^studentship/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.studentship"),
    (r"^vacancy/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.vacancy"),
    )