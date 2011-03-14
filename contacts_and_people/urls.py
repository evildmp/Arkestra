from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',

    # contacts & people
    (r"^person/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/?$", "contacts_and_people.views.person"),
    (r"^entity/(?P<slug>[-\w]+)/contact/people/(?P<letter>[a-z])/$", "contacts_and_people.views.people"),
    (r"^entity/(?P<slug>[-\w]+)/contact/people/$", "contacts_and_people.views.people"),
    (r"^entity/(?P<slug>[-\w]+)/contact/$", "contacts_and_people.views.contacts_and_people"),
    (r"^place/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/?$", "contacts_and_people.views.place"),
    # (r"^entity/(?P<slug>[-\w]+)/$", "contacts_and_people.views.entity"),    
    
    )

if "news_and_events" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^', include('news_and_events.urls')),
    )

if "vacancies_and_studentships" in settings.INSTALLED_APPS:
    print "yes"
    urlpatterns += patterns('',
        url(r'^', include('vacancies_and_studentships.urls')),
    )

if "publications" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^', include('vacancies_and_studentships.urls')),
    )
