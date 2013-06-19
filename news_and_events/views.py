import datetime
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404

from contacts_and_people.models import Entity

from models import NewsAndEventsPlugin, Event, NewsArticle
from cms_plugins import CMSNewsAndEventsPlugin

from arkestra_utilities.settings import NEWS_AND_EVENTS_LAYOUT, MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH, IN_BODY_HEADING_LEVEL, MULTIPLE_ENTITY_MODE


def common_settings(request, slug):
    if slug:
        entity = get_object_or_404(Entity, slug=slug)
    else:
        entity = Entity.objects.base_entity()
    if not (entity.website and entity.website.published and entity.auto_news_page):
        raise Http404 

    request.auto_page_url = request.path
    # request.path = entity.get_website.get_absolute_url() # for the menu, so it knows where we are
    request.current_page = entity.get_website
    context = RequestContext(request)
    instance = NewsAndEventsPlugin()
    instance.limit_to = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.default_limit = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.order_by = "importance/date"
    instance.entity = entity
    instance.heading_level = IN_BODY_HEADING_LEVEL
    instance.display = "news-and-events"
    instance.format = "details image"
    instance.layout = NEWS_AND_EVENTS_LAYOUT
    instance.view = "current"
    instance.main_page_body_file = "arkestra/universal_plugin_lister.html"
    return instance, context, entity


def news_and_events(request, slug=None):
    instance, context, entity = common_settings(request, slug)    

    instance.type = "main_page"

    meta = {"description": "Recent news and forthcoming events",}
    title = unicode(entity) + _(u" news & events")
    if MULTIPLE_ENTITY_MODE:
        pagetitle = unicode(entity) + _(u" news & events")
    else:
        pagetitle = _("News & events")
    CMSNewsAndEventsPlugin().render(context, instance, None)

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        "intro_page_placeholder": entity.news_page_intro,
        'everything': instance,
        }
        )

    return render_to_response(
        "contacts_and_people/arkestra_page.html",
        context,
        )

def previous_events(request, slug):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "events"
    instance.limit_to = None

    meta = {"description": "Archive of previous events",}
    title = unicode(entity) + u" previous events"
    pagetitle = unicode(entity) + u" previous events"

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
        "contacts_and_people/arkestra_page.html",
        context,
        )
        
def all_forthcoming_events(request, slug):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "current"
    instance.display = "events"
    instance.limit_to = None

    CMSNewsAndEventsPlugin().render(context, instance, None)

    meta = {"description": "All forthcoming events",}
    title = unicode(entity) + u" forthcoming events"
    pagetitle = unicode(entity) + u" forthcoming events"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/arkestra_page.html",
        context,
        )

def news_archive(request, slug):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "news"
    instance.limit_to = None
    instance.order_by = "date"

    CMSNewsAndEventsPlugin().render(context, instance, None)

    meta = {"description": "Archive of news items",}
    title = unicode(entity) + u" - news archive"
    pagetitle = unicode(entity) + u" - news archive"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/arkestra_page.html",
        context,
        )


def newsarticle(request, slug):
    """
    Responsible for publishing news article
    """
    if request.user.is_staff:
        newsarticle = get_object_or_404(NewsArticle, slug=slug)
    else:
        newsarticle = get_object_or_404(NewsArticle, slug=slug, published=True, date__lte=datetime.datetime.now())
    return render_to_response(
        "news_and_events/newsarticle.html",
        {
        "newsarticle":newsarticle,
        "entity": newsarticle.get_hosted_by,
        "meta": {"description": newsarticle.summary,}
        },
        RequestContext(request),
    )

def event(request, slug):
    """
    Responsible for publishing an event
    """
    # print " -------- views.event --------"
    event = get_object_or_404(Event, slug=slug)
    
    return render_to_response(
        "news_and_events/event.html",
        {"event": event,
        "entity": event.get_hosted_by,
        "meta": {"description": event.summary,},
        },
        RequestContext(request),
        )