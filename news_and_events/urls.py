from django.conf.urls.defaults import patterns, url

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
    
    # news archives 
    url(
        r'^news-archive/$', 
        "news_archive", 
        {"slug": None},
        name="news-archive-base"
        ),
    url(
        r'^news-archive/(?:(?P<slug>[-\w]+)/)$', 
        "news_archive", 
        name="news-archive"
        ),

    # previous events 
    url(
        r'^previous-events/$', 
        "previous_events", 
        {"slug": None}, 
        name="previous-events-base"
        ),
    url(
        r'^previous-events/(?:(?P<slug>[-\w]+)/)$', 
        "previous_events", 
        name="previous-events"
        ),

    # forthcoming events 
    url(
        r'^forthcoming-events/$', 
        "all_forthcoming_events", 
        {"slug": None}, 
        name="forthcoming-events-base"
        ),
    url(
        r'^forthcoming-events/(?:(?P<slug>[-\w]+)/)$', 
        "all_forthcoming_events", 
        name="forthcoming-events"
        ),

    # main news and events 
    url(
        r"^news-and-events/$", 
        "news_and_events", 
        {"slug": None}, 
        name="news-and-events-base"
        ),
    url(
        r"^news-and-events/(?:(?P<slug>[-\w]+)/)$", 
        "news_and_events", 
        name="news-and-events"
        ),
    )
