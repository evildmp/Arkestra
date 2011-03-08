from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    #(r"^entity/(?P<slug>[-\w]+)/news/$", "news_and_events.views.news"), # in development
    (r"^news/article/(?P<slug>[-\w]+)/$", "news_and_events.views.newsarticle"), # old version
    (r"^events/event/(?P<slug>[-\w]+)/$", "news_and_events.views.event"), # old version
    (r"^news/(?P<slug>[-\w]+)/$", "news_and_events.views.newsarticle"),
    (r"^event/(?P<slug>[-\w]+)/$", "news_and_events.views.event"),
    (r'^news-and-events/$', "news_and_events.views.news_and_events"),
    (r"^entity/(?P<slug>[-\w]+)/news-and-events/$", "news_and_events.views.news_and_events"),
    (r"^entity/(?P<slug>[-\w]+)/news-and-events/news-archive/$", "news_and_events.views.news_archive"),
    (r"^entity/(?P<slug>[-\w]+)/news-and-events/previous-events/$", "news_and_events.views.previous_events"),
    (r"^entity/(?P<slug>[-\w]+)/news-and-events/all-forthcoming/$", "news_and_events.views.all_forthcoming_events"),
    )
