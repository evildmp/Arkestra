# register all interesting models for search
#print "LOADING link_schemas.py for %s" % __name__

from news_and_events import models, admin
from links import schema, LinkWrapper
from django.utils.encoding import smart_unicode


schema.register(models.NewsArticle, search_fields=admin.NewsArticleAdmin.search_fields,
    metadata='subtitle', heading='"Related news"',
    short_text = 'short_title', description='subtitle',
    )
schema.register(models.Event, search_fields=admin.EventAdmin.search_fields, 
    metadata='subtitle', heading='"Related events"',
    short_text = 'short_title', description='subtitle',
    )