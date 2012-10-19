from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

from news_and_events.models import NewsArticle
from contacts_and_people.models import Entity, Person

from arkestra_utilities.settings import STANDARD_FEED_ENTRY_COUNT

class LatestNewsArticles(Feed):
    title = "cardiff news"
    description = "all the cardiff news in one place"
    link = '/'
    
    title_template = 'news_and_events/feeds/entry_title.html'
    description_template = 'news_and_events/feeds/entry_description.html'
    
    def items(self):
        return NewsArticle.objects.order_by('-date')


class LatestNewsArticlesForEntity(LatestNewsArticles):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Entity.objects.get(slug__exact=bits[0])

    def items(self, obj):
        return NewsArticle.objects.filter(publish_to=obj).order_by('-date')[:STANDARD_FEED_ENTRY_COUNT]
    
    def title(self, obj):
        return u'%s' % obj
    
    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()
    
    def description(self, obj):
        return 'News relevant for the entity "%s"' % obj


class LatestNewsArticlesForContactPerson(LatestNewsArticles):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Person.objects.get(slug__exact=bits[0])
    
    def items(self, obj):
        return NewsArticle.objects.filter(please_contact=obj).order_by('-date')[:STANDARD_FEED_ENTRY_COUNT]
    
    def title(self, obj):
        return u'%s' % obj
    
    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()
    
    def description(self, obj):
        return 'News with the contact "%s"' % obj


class LatestNewsArticlesForRelatedPerson(LatestNewsArticles):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Person.objects.get(slug__exact=bits[0])
    
    def items(self, obj):
        return NewsArticle.objects.filter(related_people=obj).order_by('-date')[:STANDARD_FEED_ENTRY_COUNT]
    
    def title(self, obj):
        return u'%s' % obj
    
    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()
    
    def description(self, obj):
        return 'News with the the related person "%s"' % obj

