from django import template
from django.shortcuts import render_to_response
from django.db.models import Q
from news_and_events.models import Event, NewsArticle, NewsAndEventsPlugin
from contacts_and_people.models import Entity
from entity_tags import work_out_entity
from cms.models import Page
from datetime import datetime

from news_and_events.cms_plugins import CMSNewsAndEventsPlugin

from itertools import chain
#from django.template.defaultfilters import date

register = template.Library()
    
@register.inclusion_tag('news_and_event_lists.html', takes_context = True)
def news_and_events(context, display = "news-and-events", heading = 3, format = "details", current_or_archive = "current", max_items = None, order_by = "importance/date", entity = None):
    """
    Depends on Cardiff's row/column CSS
    Publishes a date-ordered list of news and events
    """
    print "news_and_events_tags.news_and_events"
    instance = NewsAndEventsPlugin()
    if not entity:
        entity = work_out_entity(context, entity)
    instance.order_by = order_by
    instance.entity = entity
    instance.heading_level = heading
    instance.display = display
    print "instance.display", instance.display
    instance.limit_to = max_items
    instance.format = format
    instance.layout = "sidebyside"
    instance.current_or_archive = current_or_archive
    instance.show_more_items = False # because we know that these hardcoded lists don't require it
    CMSNewsAndEventsPlugin().render(context, instance, None)
    return context