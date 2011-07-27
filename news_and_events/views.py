from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.template import RequestContext

from contacts_and_people.models import Entity, default_entity
from links.link_functions import object_links

from models import NewsAndEventsPlugin, Event, NewsArticle
from cms_plugins import CMSNewsAndEventsPlugin

layout = getattr(settings, "NEWS_AND_EVENTS_LAYOUT", "sidebyside")

MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH = settings.MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
IN_BODY_HEADING_LEVEL = settings.IN_BODY_HEADING_LEVEL
class NewsAndEventsViews(object):
    def test(self):
        pass


def common_settings(request, slug):
    entity = Entity.objects.get(slug=slug) or default_entity
    request.current_page = entity.get_website() # for the menu, so it knows where we are
    context = RequestContext(request)
    instance = NewsAndEventsPlugin()
    instance.limit_to = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.default_limit = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.order_by = "importance/date"
    instance.entity = entity
    instance.heading_level = IN_BODY_HEADING_LEVEL
    instance.display = "news-and-events"
    instance.format = "details image"
    instance.layout = layout
    instance.view = "current"
    instance.main_page_body_file = "arkestra/universal_plugin_lister.html"
    return instance, context, entity


def news_and_events(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)    

    instance.type = "main_page"
    # get_news_and_events(instance)

    meta = {"description": "Recent news and forthcoming events",}
    title = str(entity)  + " news & events"
    pagetitle = str(entity) + " news & events"
    
    CMSNewsAndEventsPlugin().render(context, instance, None)
    # get_news_and_events(instance)
    
    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )

def previous_events(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "events"
    instance.limit_to = None

    meta = {"description": "Archive of previous events",}
    title = str(entity)  + " previous events"
    pagetitle = str(entity) + " previous events"

    CMSNewsAndEventsPlugin().render(context, instance, None)

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )
        
def all_forthcoming_events(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)
    main_page_body_file = "arkestra/universal_plugin_lister.html"

    instance.type = "sub_page"
    instance.view = "current"
    instance.display = "events"
    instance.limit_to = None

    CMSNewsAndEventsPlugin().render(context, instance, None)

    meta = {"description": "All forthcoming events",}
    title = str(entity)  + " forthcoming events"
    pagetitle = str(entity) + " forthcoming events"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )

def news_archive(request, slug=getattr(default_entity,"slug", None)):
    instance, context, entity = common_settings(request, slug)
    main_page_body_file = "arkestra/universal_plugin_lister.html"

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "news"
    instance.limit_to = None
    instance.order_by = "date"

    CMSNewsAndEventsPlugin().render(context, instance, None)

    meta = {"description": "Archive of news items",}
    title = str(entity)  + " - news archive"
    pagetitle = str(entity) + " - news archive"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )

def newsarticle_and_event(item):
    item.links = object_links(item) # not needed if using get_links templatetag
    item.hosted_by = item.hosted_by or default_entity
    item.link_to_news_and_events_page = item.hosted_by.get_related_info_page_url("news-and-events")
    item.template = item.hosted_by.get_template()
    return item

def newsarticle(request, slug):
    """
    Responsible for publishing news article
    """
    newsarticle = get_object_or_404(NewsArticle, slug=slug)
    newsarticle = newsarticle_and_event(newsarticle)
    
    return render_to_response(
        "news_and_events/newsarticle.html",
        {
        "newsarticle":newsarticle,
        "entity": newsarticle.hosted_by,
        "meta": {"description": newsarticle.subtitle,}
        },
        RequestContext(request),
        )

def event(request, slug):
    """
    Responsible for publishing an event
    """
    print " -------- views.event --------"
    event = get_object_or_404(Event, slug=slug)
    event = newsarticle_and_event(event)
    
    # featuring = event.get_featuring()

    return render_to_response(
        "news_and_events/event.html",
        {"event": event,
        "entity": event.hosted_by,
        "meta": {"description": event.subtitle,},
        },
        RequestContext(request),
        )

print "end of views"