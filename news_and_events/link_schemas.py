# register all interesting models for search

from news_and_events import models, admin
from links import schema, LinkWrapper

schema.register(models.NewsArticle, search_fields=admin.NewsArticleAdmin.search_fields,
    metadata='subtitle', heading='"Related news"',
    short_text = 'short_title', description='subtitle',
    )
schema.register(models.Event, search_fields=admin.EventAdmin.search_fields, 
    metadata='subtitle', heading='"Related events"',
    short_text = 'short_title', description='subtitle',
    )
