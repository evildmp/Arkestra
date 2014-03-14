from django.conf.urls.defaults import patterns, url

from news_and_events import views

urlpatterns = patterns('news_and_events.views',

    # news and events items
    url(
        r"^news/(?P<slug>[-\w]+)/$",
        "newsarticle",
        name="news"
        ),
    url(
        r"^event/(?P<slug>[-\w]+)/$",
        "event",
        name="event"
        ),

    # main news and events
    url(
        r"^news-and-events/(?:(?P<slug>[-\w]+)/)?$",
        views.NewsAndEventsView.as_view(),
        name="news-and-events"
        ),

    # news archives
    url(
        r"^news-archive/(?:(?P<slug>[-\w]+)/)?$",
        views.NewsArchiveView.as_view(),
        name="news-archive"
        ),

    # previous events
    url(
        r"^previous-events/(?:(?P<slug>[-\w]+)/)?$",
        views.EventsArchiveView.as_view(),
        name="events-archive"
        ),

    # forthcoming events
    url(
        r"^forthcoming-events/(?:(?P<slug>[-\w]+)/)?$",
        views.EventsForthcomingView.as_view(),
        name="events-forthcoming"
        ),
    )
