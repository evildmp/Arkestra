from django.conf.urls.defaults import patterns

urlpatterns = patterns('vacancies_and_studentships.views',
    
    # vacancies and studentships 
    (r"^vacancy/(?P<slug>[-\w]+)/$", "vacancy", {}, "vacancy"),
    (r"^studentship/(?P<slug>[-\w]+)/$", "studentship", {}, "studentship"),
    
    # named entities' vacancies and studentships
    (r"^vacancies-and-studentships/(?P<slug>[-\w]+)/$", "vacancies_and_studentships", {}, "vacancies-and-studentships"),
    # base entity's vacancies and studentships
    (r'^vacancies-and-studentships/$', "vacancies_and_studentships", {}, "vacancies-and-studentships_base"),

    (r'^archived-vacancies/(?P<slug>[-\w]+)/$', "archived_vacancies"),
    (r'^all-open-vacancies/(?P<slug>[-\w]+)/$', "all_current_vacancies"),
    
    (r'^archived-vacancies/$', "archived_vacancies"),
    (r'^all-open-vacancies/$', "all_current_vacancies"),

    (r'^archived-studentships/(?P<slug>[-\w]+)/$', "archived_studentships"),
    (r'^all-open-studentships/(?P<slug>[-\w]+)/$', "all_current_studentships"),

    (r'^archived-studentships/$', "archived_studentships"),
    (r'^all-open-studentships/$', "all_current_studentships"),
)