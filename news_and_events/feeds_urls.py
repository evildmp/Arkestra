from django.conf.urls.defaults import patterns
from news_and_events import feeds

# inlcude this in your base urls.py:
# 
# feed url: /news/rss/latest/

feeds = {
    'latest': feeds.LatestNewsArticles,
    'latest_by_entity': feeds.LatestNewsArticlesForEntity,
    'latest_by_contact_person': feeds.LatestNewsArticlesForContactPerson,
    'latest_by_related_person': feeds.LatestNewsArticlesForRelatedPerson,
}

urlpatterns = patterns('',
    (r'^(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)