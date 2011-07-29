from django import template
from news_and_events.models import NewsAndEventsPlugin
# from entity_tags import work_out_entity
from news_and_events.cms_plugins import CMSNewsAndEventsPlugin

#from django.template.defaultfilters import date

register = template.Library()
    
@register.inclusion_tag('arkestra/universal_plugin_lister.html', takes_context=True)
def news_and_events(context, display="news-and-events", heading=3,
        format="details", current_or_archive="current", max_items=None,
        order_by="importance/date", entity=None):
    """
    Depends on Cardiff's row/column CSS
    Publishes a date-ordered list of news and events
    """
    instance = NewsAndEventsPlugin()
    if not entity:
        entity = work_out_entity(context, entity)
    instance.order_by = order_by
    instance.entity = entity
    instance.heading_level = heading
    instance.display = display
    instance.limit_to = max_items
    instance.format = format
    instance.layout = "sidebyside"
    instance.current_or_archive = current_or_archive
    instance.show_more_items = False # because we know that these hardcoded lists don't require it
    CMSNewsAndEventsPlugin().render(context, instance, None)
    return context
    
@register.inclusion_tag('arkestra/universal_plugin_lister.html', takes_context=True)
def person_events(context):
    """
    Depends on Cardiff's row/column CSS
    Publishes a date-ordered list of news and events
    """
    instance = NewsAndEventsPlugin()
    instance.type = "for_person"
    instance.heading_level = 3
    instance.display = "events"
    instance.view = "all_forthcoming"
    instance.order_by = "date"
    instance.format = "details"
    instance.show_images = False
    instance.person = context["person"]
    # get_news_and_events(instance)
    CMSNewsAndEventsPlugin().render(context, instance, None)
    return context
    

@register.inclusion_tag('arkestra/universal_plugin_lister.html', takes_context=True)
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
    
@register.inclusion_tag('event_index.html', takes_context=True)
def event_index(context):
    """
    """
    index_items = context["news_and_events"].events_index_items
    return {
        "index_items": index_items,
        "indexer": "start_date.year",
        }
