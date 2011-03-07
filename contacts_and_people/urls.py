from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',

    # contacts & people
    (r"^person/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/?$", "contacts_and_people.views.person"),
    (r"^place/(?P<slug>[-\w]+)/$", "contacts_and_people.views.place"),
    (r"^entity/(?P<slug>[-\w]+)/contact/people/(?P<letter>[a-z])/$", "contacts_and_people.views.people"),
    (r"^entity/(?P<slug>[-\w]+)/contact/people/$", "contacts_and_people.views.people"),
    (r"^entity/(?P<slug>[-\w]+)/contact/$", "contacts_and_people.views.contacts_and_people"),
    # (r"^entity/(?P<slug>[-\w]+)/$", "contacts_and_people.views.entity"),    
    
    # news & events
    (r'^news-and-events/$', "news_and_events.views.news_and_events"),
    (r"^entity/(?P<slug>[-\w]+)/news-and-events/$", "news_and_events.views.news_and_events"),
    (r"^entity/(?P<slug>[-\w]+)/news-and-events/news-archive/$", "news_and_events.views.news_archive"),
    (r"^entity/(?P<slug>[-\w]+)/news-and-events/previous-events/$", "news_and_events.views.previous_events"),
    (r"^entity/(?P<slug>[-\w]+)/news-and-events/all-forthcoming/$", "news_and_events.views.all_forthcoming_events"),

    #(r"^entity/(?P<slug>[-\w]+)/news/$", "news_and_events.views.news"), # in development
    (r"^news/article/(?P<slug>[-\w]+)/$", "news_and_events.views.newsarticle"), # old version
    (r"^events/event/(?P<slug>[-\w]+)/$", "news_and_events.views.event"), # old version
    (r"^news/(?P<slug>[-\w]+)/$", "news_and_events.views.newsarticle"),
    (r"^event/(?P<slug>[-\w]+)/$", "news_and_events.views.event"),
    
    (r"^entity/(?P<slug>[-\w]+)/vacancies-and-studentships/$", "vacancies_and_studentships.views.vacancies_and_studentships"),
    (r"^studentship/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.studentship"),
    (r"^vacancy/(?P<slug>[-\w]+)/$", "vacancies_and_studentships.views.vacancy"),
    
    (r"^entity/(?P<slug>[-\w]+)/publications/$", "contacts_and_people.views.publications"),
)