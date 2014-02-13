from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    'contacts_and_people.views',

    # person
    url(r"^person/(?P<slug>[-\w]+)/$", "person", name="contact-person"),
    url(r"^person/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/$", "person",
        name="contact-person-tab"),

    # place
    url(r"^place/(?P<slug>[-\w]+)/$", "place", name="contact-place"),
    url(r"^place/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/$", "place",
        name="contact-place-tab"),

    # lists of people in an entity
    url(r"^people/(?P<slug>[-\w]+)/$", "people", name="contact-people"),
    url(
        r"^people/(?P<slug>[-\w]+)/(?P<letter>\w)/$",
        "people", name="contact-people-letter"),

    # main contacts & people page
    # non-base entities
    url(r'^contact/(?P<slug>[-\w]+)/$', "contacts_and_people",
        name="contact-entity"),
    # base entity only
    url(r'^contact/$', "contacts_and_people", name="contact-entity-base"),

    # news, events, vacancies, studentships
    (r'^', include('news_and_events.urls')),
    (r'^', include('vacancies_and_studentships.urls')),

    # housekeeping
    (r'^', include('housekeeping.urls')),
    (r'^', include('arkestra_image_plugin.urls')),
    )
