from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('contacts_and_people.views',

    # person
    (r"^person/(?P<slug>[-\w]+)/?$", "person", {}, "contact_person"),
    (r"^person/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/?$", "person", {}, "contact_person_tab"),
    
    # place
    (r"^place/(?P<slug>[-\w]+)/?$", "place", {}, "contact_place"),    
    (r"^place/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/?$", "place", {}, "contact_place_tab"),    

    # lists of people in an entity
    (r"^people/(?P<slug>[-\w]+)/$", "people", {}, "contact_people"), 
    (r"^people/(?P<slug>[-\w]+)/(?P<letter>\w)/$", "people", {}, "contact_people_letter"),
    
    # main contacts & people page
    (r'^contact/(?P<slug>[-\w]+)/$', "contacts_and_people", {}, "contact"), 
    # non-base entities
    (r'^contact/$', "contacts_and_people", {}, "contact_base"), # base entity only

    # news, events, vacancies, studentships
    (r'^', include('news_and_events.urls')),
    (r'^', include('vacancies_and_studentships.urls')),

    # housekeeping
    (r'^', include('housekeeping.urls')),
    (r'^', include('arkestra_image_plugin.urls')),


    )

    # the old ways
    # (r"^entity/(?P<slug>[-\w]+)/contact/people/(?P<letter>[a-z])/$", "contacts_and_people.views.people"),
    # (r"^entity/(?P<slug>[-\w]+)/contact/people/$", "contacts_and_people.views.people"),
    # (r"^entity/(?P<slug>[-\w]+)/contact/$", "contacts_and_people.views.contacts_and_people"),
    # )


