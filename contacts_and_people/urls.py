from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    'contacts_and_people.views',

    # person
    url(r"^person/(?P<slug>[-\w]+)/$",
        view="person",
        name="contact-person"
        ),
    url(r"^person/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/$",
        view="person",
        name="contact-person-tab"
        ),

    # place
    url(r"^place/(?P<slug>[-\w]+)/$",
        view="place",
        name="contact-place"
        ),
    url(r"^place/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/$",
        view="place",
        name="contact-place-tab"
        ),

    # lists of people in an entity
    url(
        r"^people/(?P<slug>[-\w]+)/$",
        view="people",
        name="contact-people"
        ),
    url(
        r"^people/(?P<slug>[-\w]+)/(?P<letter>\w)/$",
        view="people",
        name="contact-people-letter"
        ),

    # main contacts & people page
    url(
        r"^contact/(?:(?P<slug>[-\w]+)/)?$",
        view="contacts_and_people",
        name="contact-entity"
        ),

    # news, events, vacancies, studentships
    (r'^', include('news_and_events.urls')),
    (r'^', include('vacancies_and_studentships.urls')),

    # housekeeping
    (r'^', include('housekeeping.urls')),
    (r'^', include('arkestra_image_plugin.urls')),
    )
