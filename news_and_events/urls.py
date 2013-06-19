from django.conf.urls.defaults import *
# from  news_and_events.views import NewsAndEventsViews

urlpatterns = patterns('news_and_events.views',
    
    # news and events items
    url(r"^news/(?P<slug>[-\w]+)/$", "newsarticle", {}, "news" ),
    url(r"^event/(?P<slug>[-\w]+)/$", "event", {}, "event"),
    
    # entities' news and events
    url(
        r'^news-archive/?$', 
        "news_archive", 
        {"slug": None},
        "news-archive_base"
        ),
    url(
        r'^news-archive/(?:(?P<slug>[-\w]+)/)?$', 
        "news_archive", 
        {}, 
        "news-archive"
        ),

    url(
        r'^previous-events/?$', 
        "previous_events", 
        {"slug": None}, 
        "previous-events_base"
        ),
    url(
        r'^previous-events/(?:(?P<slug>[-\w]+)/)?$', 
        "previous_events", 
        {}, 
        "previous-events"
        ),

    url(
        r'^forthcoming-events/?$', 
        "all_forthcoming_events", 
        {"slug": None}, 
        "forthcoming-events_base"
        ),
    url(
        r'^forthcoming-events/(?:(?P<slug>[-\w]+)/)?$', 
        "all_forthcoming_events", 
        {}, 
        "forthcoming-events"
        ),

    url(
        r"^news-and-events/?$", 
        "news_and_events", 
        {"slug": None}, 
        "news-and-events_base"
        ),
    url(
        r"^news-and-events/(?:(?P<slug>[-\w]+)/)?$", 
        "news_and_events", 
        {}, 
        "news-and-events"
        ),
    )
