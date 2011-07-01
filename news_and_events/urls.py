from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    # news and events items
    (r"^news/(?P<slug>[-\w]+)/$", "news_and_events.views.newsarticle"),
    (r"^event/(?P<slug>[-\w]+)/$", "news_and_events.views.event"),
    
    # named entities' news and events
    (r'^news-archive/(?P<slug>[-\w]+)/$', "news_and_events.views.news_archive"),
    (r'^previous-events/(?P<slug>[-\w]+)/$', "news_and_events.views.previous_events"),
    (r'^forthcoming-events/(?P<slug>[-\w]+)/$', "news_and_events.views.all_forthcoming_events"),
    (r"^news-and-events/(?P<slug>[-\w]+)/$", "news_and_events.views.news_and_events"),

    # base entity's news and events
    (r'^news-archive/$', "news_and_events.views.news_archive"),
    (r'^previous-events/$', "news_and_events.views.previous_events"),
    (r'^forthcoming-events/$', "news_and_events.views.all_forthcoming_events"),
    (r'^news-and-events/$', "news_and_events.views.news_and_events"),

    )
    #(r"^entity/(?P<slug>[-\w]+)/news/$", "news_and_events.views.news"), # in development
