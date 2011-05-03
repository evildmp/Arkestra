To install these applications:

First, you need to have Django CMS 2 installed and working.
And get django-widgetry (http://github.com/stefanfoulis/django-widgetry)


Place contacts_and_people and news_and_events onto your PYTHONPATH.

Add:

    'news_and_events',
    'contacts_and_people',

to your INSTALLED_APPS.

Add:

    (r"^entity/(?P<slug>[-\w]+)/$", "contacts_and_people.views.entity"),
    (r"^person/(?P<slug>[-\w]+)/$", "contacts_and_people.views.person"),
    (r"^news/article/(?P<slug>[-\w]+)/$", "news_and_events.views.newsarticle"),
    (r"^events/event/(?P<slug>[-\w]+)/$", "news_and_events.views.event"),

    (r'^news/rss/', include('news_and_events.feeds_urls')),

to your urlpatterns = patterns in urls.py.

A syncdb will be required.


these rss feeds are available:

/news/rss/latest/										all news
/news/rss/latest_by_entity/<entity-slug>/				all news entries for the entity
/news/rss/latest_by_contact_person/<person-slug>/		all news entries where the person is the contact person
/news/rss/latest_by_related_person/<person-slug>/		all news entries where the person is mentioned in related person

