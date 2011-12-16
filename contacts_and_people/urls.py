from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',

    # person
    (r"^person/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/?$", "contacts_and_people.views.person"),
    
    # place
    (r"^place/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/?$", "contacts_and_people.views.place"),    

    # lists of people in an entity
    (r"^people/(?P<slug>[-\w]+)/(?P<letter>[a-z])/$", "contacts_and_people.views.people"),
    (r"^people/(?P<slug>[-\w]+)/$", "contacts_and_people.views.people"), 
    
    # main contacts & people page
    (r'^contact/(?P<slug>[-\w]+)/$', "contacts_and_people.views.contacts_and_people"), # non-base entities
    (r'^contact/$', "contacts_and_people.views.contacts_and_people"), # base entity only

    # news, events, vacancies, studentships
    (r'^', include('news_and_events.urls')),
    (r'^', include('vacancies_and_studentships.urls')),

    # housekeeping
    (r'^', include('housekeeping.urls')),


    )

    # the old ways
    # (r"^entity/(?P<slug>[-\w]+)/contact/people/(?P<letter>[a-z])/$", "contacts_and_people.views.people"),
    # (r"^entity/(?P<slug>[-\w]+)/contact/people/$", "contacts_and_people.views.people"),
    # (r"^entity/(?P<slug>[-\w]+)/contact/$", "contacts_and_people.views.contacts_and_people"),
    # )


