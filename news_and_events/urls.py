from django.conf.urls.defaults import *
from news_and_events import views
# from  news_and_events.views import NewsAndEventsViews

urlpatterns = patterns('',
    
    # news and events items
    url(r"^news/(?P<slug>[-\w]+)/$", views.newsarticle, name="newsarticle"),
    url(r"^event/(?P<slug>[-\w]+)/$", views.event, name="event"),
    
    # entities' news and events
    url(r'^news-archive/(?:(?P<slug>[-\w]+)/)?$', views.news_archive, name="news_archive"),
    url(r'^previous-events/(?:(?P<slug>[-\w]+)/)?$', views.previous_events, name="previous_events"),
    url(r'^forthcoming-events/(?:(?P<slug>[-\w]+)/)?$', views.all_forthcoming_events, name="forthcoming_event"),
    url(r"^news-and-events/(?:(?P<slug>[-\w]+)/)?$", views.news_and_events, name="news_and_events"),
    url(r"^new-news-and-events/(?:(?P<slug>[-\w]+)/)?$", views.new_news_and_events, name="new_news_and_events"),
    )
    #(r"^entity/(?P<slug>[-\w]+)/news/$", "news_and_events.views.news"), # in development

