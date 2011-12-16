from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    
    # vacancies and studentships 
    (r"^vacancy/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.vacancy"),
    (r"^studentship/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.studentship"),
    
    # named entities' vacancies and studentships
    (r"^vacancies-and-studentships/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.vacancies_and_studentships"),

    (r'^archived-vacancies/(?P<slug>[-\w]+)/$', "vacancies_and_studentships.views.archived_vacancies"),
    (r'^all-open-vacancies/(?P<slug>[-\w]+)/$', "vacancies_and_studentships.views.all_current_vacancies"),

    (r'^archived-studentships/(?P<slug>[-\w]+)/$', "vacancies_and_studentships.views.archived_studentships"),
    (r'^all-open-studentships/(?P<slug>[-\w]+)/$', "vacancies_and_studentships.views.all_current_studentships"),

    # base entity's vacancies and studentships
    (r'^vacancies-and-studentships/$', "vacancies_and_studentships.views.vacancies_and_studentships"),
    
    (r'^archived-vacancies/$', "vacancies_and_studentships.views.archived_vacancies"),
    (r'^all-open-vacancies/$', "vacancies_and_studentships.views.all_current_vacancies"),

    (r'^archived-studentships/$', "vacancies_and_studentships.views.archived_studentships"),
    (r'^all-open-studentships/$', "vacancies_and_studentships.views.all_current_studentships"),
)