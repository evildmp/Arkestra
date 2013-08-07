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
        
    #(r"^entity/(?P<slug>[-\w]+)/news/$", "news_and_events.views.news"), # in development


    # # old urls
    # url(
    #     r'^old-news-archive/$', 
    #     "news_archive", 
    #     {"slug": None},
    #     name="old-news-archive-base"
    #     ),
    #     
    # url(
    #     r'^old-news-archive/(?:(?P<slug>[-\w]+)/)$', 
    #     "news_archive", 
    #     name="old-news-archive"
    #     ),
    # 
    # url(
    #     r'^old-previous-events/$', 
    #     "previous_events", 
    #     {"slug": None}, 
    #     name="old-previous-events-base"
    #     ),
    # url(
    #     r'^old-previous-events/(?:(?P<slug>[-\w]+)/)$', 
    #     "previous_events", 
    #     name="old-previous-events"
    #     ),
    # 
    # # forthcoming events 
    # url(
    #     r'^old-forthcoming-events/$', 
    #     "all_forthcoming_events", 
    #     {"slug": None}, 
    #     name="old-forthcoming-events-base"
    #     ),
    # url(
    #     r'^old-forthcoming-events/(?:(?P<slug>[-\w]+)/)$', 
    #     "all_forthcoming_events", 
    #     name="old-forthcoming-events"
    #     ),
    # 
    #     
    # url(
    #     r"^old-news-and-events/$", 
    #     "news_and_events", 
    #     {"slug": None}, 
    #     name="old-news-and-events-base"
    #     ),
    # url(
    #     r"^old-news-and-events/(?:(?P<slug>[-\w]+)/)$", 
    #     "news_and_events", 
    #     name="old-news-and-events"
    #     ),
     
    # class-based views
        
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
        
    # # series events 
    # url(
    #     r"^series-events/(?:(?P<slug>[-\w]+)/)$",
    #     views.EventsSeriesView.as_view(), 
    #     name="events-series"
    #     ),
    # 
    # url(
    #     r'^series-events/$', 
    #     views.EventsSeriesView.as_view(), 
    #     {"slug": None},
    #     name="events-series-base"
    #     ),
    )
