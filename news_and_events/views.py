import django.http as http
from django.shortcuts import render_to_response, get_object_or_404
from news_and_events.models import NewsAndEventsPlugin, Event, NewsArticle # should improve 
from contacts_and_people.models import Entity, default_entity
from django.conf import settings
from links.link_functions import object_links
from django.template import RequestContext, Context
from datetime import datetime
from functions import get_news_and_events

news_and_events_list_default_limit = getattr(settings, "NEWS_AND_EVENT_LIMIT_TO", 8)
layout = getattr(settings, "NEWS_AND_EVENTS_LAYOUT", "sidebyside")
h_main_body = settings.H_MAIN_BODY

def common_settings(request, slug = getattr(default_entity,"slug", None)):
    # general values - entity, request, template
    entity = Entity.objects.get(slug=slug)
    # request.current_page = entity.get_website() # for the menu, so it knows where we are
    request.current_page = default_entity.get_website()
    context = RequestContext(request)
    instance = NewsAndEventsPlugin()
    instance.limit_to = news_and_events_list_default_limit
    instance.default_limit = news_and_events_list_default_limit
    instance.order_by = "importance/date"
    instance.entity = entity
    instance.heading_level = h_main_body
    instance.display = "news-and-events"
    instance.format = "details"
    instance.layout = layout
    instance.view = "current"
    return instance, context, entity

def news_and_events(request, slug):
    instance, context, entity = common_settings(request, slug)    
    main_page_body_file = "news_and_event_lists.html"

    instance.type = "main_page"
    instance.show_images = True
    get_news_and_events(instance)

    meta = {"description": "Recent news and forthcoming events",}
    title = str(entity)  + " news & events"
    pagetitle = str(entity) + " news & events"
    return render_to_response(
        "contacts_and_people/entity_information.html",
        {"entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": main_page_body_file,
        "news_and_events": instance,
        },
        context,
        )

def previous_events(request, slug):
    instance, context, entity = common_settings(request, slug)
    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "events"
    instance.limit_to = None
    get_news_and_events(instance)

    meta = {"description": "Archive of previous events",}
    title = str(entity)  + " previous events"
    pagetitle = str(entity) + " previous events"
    main_page_body_file = "news_and_event_lists.html"

    return render_to_response(
        "contacts_and_people/entity_information.html",
        {"entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": main_page_body_file,
        "news_and_events": instance,
        },
        context,
        )
        
def all_forthcoming_events(request, slug):
    instance, context, entity = common_settings(request, slug)
    instance.type = "sub_page"
    instance.view = "current"
    instance.display = "events"
    instance.limit_to = None
    get_news_and_events(instance)

    meta = {"description": "All forthcoming events",}
    title = str(entity)  + " forthcoming events"
    pagetitle = str(entity) + " forthcoming events"
    main_page_body_file = "news_and_event_lists.html"

    return render_to_response(
        "contacts_and_people/entity_information.html",
        {"entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": main_page_body_file,
        "news_and_events": instance,
        },
        context,
        )

def news_archive(request, slug):
    instance, context, entity = common_settings(request, slug)
    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "news"
    instance.limit_to = None
    instance.order_by = "date"
    get_news_and_events(instance)

    meta = {"description": "Archive of news items",}
    title = str(entity)  + " - news archive"
    pagetitle = str(entity) + " - news archive"
    main_page_body_file = "news_and_event_lists.html"

    return render_to_response(
        "contacts_and_people/entity_information.html",
        {"entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": main_page_body_file,
        "news_and_events": instance,
        },
        context,
        )

def newsarticle(request, slug):
    """
    Responsible for publishing news article
    """
    print " -------- views.newsarticle --------"
    newsarticle = get_object_or_404(NewsArticle, slug=slug)
    print newsarticle.date - datetime.now()
    entity = newsarticle.hosted_by
    links = object_links(newsarticle)
    print links
    request.current_page = default_entity.get_website()
    meta = {"description": newsarticle.subtitle,}
    
    template = getattr(entity, "__get_template__", getattr(settings, "CMS_DEFAULT_TEMPLATE", "base.html"))
    return render_to_response(
        "news_and_events/newsarticle.html",
        {"newsarticle":newsarticle,
        "template": template,
        "content_object": newsarticle,
        "entity": entity,
        "links": links,
        "meta": meta,
        },
        RequestContext(request),
        )

def event(request, slug):
    """
    Responsible for publishing an event
    """
    print " -------- views.event --------"
    event = get_object_or_404(Event, slug=slug)
    featuring = event.get_featuring()
    entity = event.hosted_by
    template = getattr(entity, "__get_template__", getattr(settings, "CMS_DEFAULT_TEMPLATE", "base.html"))  # this perhaps should reflect either the default_entity or the new article's hosted_by
    links = object_links(event)
    meta = {"description": event.subtitle,}
    # request.current_page = default_entity.get_website()
    return render_to_response(
        "news_and_events/event.html",
        {"event": event,
        "content_object": event,
        "featuring": featuring,
        "template": template,
        "entity" : entity,
        "links": links,
        "meta": meta,
        },
        RequestContext(request),
        )