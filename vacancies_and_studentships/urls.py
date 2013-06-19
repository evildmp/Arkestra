from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('vacancies_and_studentships.views',
    
    url(r"^vacancy/(?P<slug>[-\w]+)/$", views.vacancy, name="vacancy"),
    url(r"^studentship/(?P<slug>[-\w]+)/$", views.studentship, name="studentship"),
    
    # named entities' vacancies and studentships
    url(r"^vacancies-and-studentships/(?P<slug>[-\w]+)/$", "vacancies_and_studentships", {}, "vacancies-and-studentships"),
    # base entity's vacancies and studentships
    url(r'^vacancies-and-studentships/$', "vacancies_and_studentships", {}, "vacancies-and-studentships_base"),

    url(r'^archived-vacancies/(?P<slug>[-\w]+)/$', "archived_vacancies"),
    url(r'^all-open-vacancies/(?P<slug>[-\w]+)/$', "all_current_vacancies"),
    
    url(r'^archived-vacancies/$', "archived_vacancies"),
    url(r'^all-open-vacancies/$', "all_current_vacancies"),

    url(r'^archived-studentships/(?P<slug>[-\w]+)/$', "archived_studentships"),
    url(r'^all-open-studentships/(?P<slug>[-\w]+)/$', "all_current_studentships"),

    url(r'^archived-studentships/$', "archived_studentships"),
    url(r'^all-open-studentships/$', "all_current_studentships"),
)
