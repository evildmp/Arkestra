from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    
    # vacancies and studentships 
    (r"^vacancy/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.vacancy"),
    (r"^studentship/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.studentship"),
    
    # named entities' vacancies and studentships
    (r"^vacancies-and-studentships/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.vacancies_and_studentships"),

    # base entity's vacancies and studentships
    (r'^vacancies-and-studentships/$', "vacancies_and_studentships.views.vacancies_and_studentships"),
    (r'^vacancy-archive/$', "vacancies_and_studentships.views.archived_vacancies"),
    (r'^studentship-archive/$', "vacancies_and_studentships.views.archived_studentships"),
    )