from django import template
from django.shortcuts import render_to_response
from django.db.models import Q
from news_and_events.models import Event, NewsArticle, NewsAndEventsPlugin
from contacts_and_people.models import Entity
# from entity_tags import work_out_entity
from cms.models import Page
from datetime import datetime
from news_and_events.functions import get_news_and_events
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
    
@register.inclusion_tag('news_and_event_lists.html', takes_context = True)
def person_events(context):
    """
    Depends on Cardiff's row/column CSS
    Publishes a date-ordered list of news and events
    """
    instance = NewsAndEventsPlugin()
    instance.type = "for_person"
    instance.display = "events"
    instance.view = "all_forthcoming"
    instance.order_by = "date"
    instance.format = "details"
    instance.show_images = False
    instance.person = context["person"]
    # get_news_and_events(instance)
    CMSNewsAndEventsPlugin().render(context, instance, None)
    return context
    

@register.inclusion_tag('news_and_event_lists.html', takes_context = True)
def place_events(context):
    """
    Depends on Cardiff's row/column CSS
    Publishes a date-ordered list of news and events
    """
    instance = NewsAndEventsPlugin()
    instance.type = "for_place"
    instance.display = "events"
    instance.view = "current"
    instance.order_by = "date"
    instance.format = "details"
    instance.show_images = False
    instance.limit_to = None
    instance.show_venue = False
    instance.place = context["place"]
    # get_news_and_events(instance)
    CMSNewsAndEventsPlugin().render(context, instance, None)
    return context
    
@register.inclusion_tag('event_index.html', takes_context = True)
def event_index(context):
    """
    """
    events = context["news_and_events"].events
    index_items = context["news_and_events"].events_index_items
    return {
        "index_items": index_items,
        "indexer": "start_date.year",
        }