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
        r"^news-and-events/(?:(?P<slug>[-\w]+)/)$",
        views.NewsAndEventsView.as_view(),
        name="news-and-events"
        ),

    url(
        r"^news-and-events/$",
        views.NewsAndEventsView.as_view(),
        {"slug": None},
        name="news-and-events-base"
        ),

    # news archives
    url(
        r"^news-archive/(?:(?P<slug>[-\w]+)/)$",
        views.NewsArchiveView.as_view(),
        name="news-archive"
        ),

    url(
        r'^news-archive/$',
        views.NewsArchiveView.as_view(),
        {"slug": None},
        name="news-archive-base"
        ),

    # previous events
    url(
        r"^previous-events/(?:(?P<slug>[-\w]+)/)$",
        views.EventsArchiveView.as_view(),
        name="events-archive"
        ),

    url(
        r'^previous-events/$',
        views.EventsArchiveView.as_view(),
        {"slug": None},
        name="events-archive-base"
        ),

    # forthcoming events
    url(
        r"^forthcoming-events/(?:(?P<slug>[-\w]+)/)$",
        views.EventsForthcomingView.as_view(),
        name="events-forthcoming"
        ),

    url(
        r'^forthcoming-events/$',
        views.EventsForthcomingView.as_view(),
        {"slug": None},
        name="events-forthcoming-base"
        ),
    )
