import datetime
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from django.views.generic.base import View

from contacts_and_people.models import Entity

from models import NewsAndEventsPlugin, Event, NewsArticle
from lister import NewsAndEventsCurrentLister, NewsArchiveLister, EventsArchiveLister, EventsForthcomingLister

from cms_plugins import CMSNewsAndEventsPlugin

from arkestra_utilities.settings import NEWS_AND_EVENTS_LAYOUT, MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH, IN_BODY_HEADING_LEVEL, MULTIPLE_ENTITY_MODE


class ArkestraGenericView(View):
    def get(self, request, *args, **kwargs):
        self.get_entity()
        
    def get_entity(self):
        slug = self.kwargs['slug']
        if slug:
            entity = get_object_or_404(Entity, slug=slug)
        else:
            entity = Entity.objects.base_entity()
        if not (entity.website and entity.website.published and entity.auto_news_page):
            raise Http404 
        self.entity = entity         
    
    def response(self, request):
        request.auto_page_url = request.path
        # request.path = entity.get_website.get_absolute_url() 
        # for the menu, so it knows where we are
        request.current_page = self.entity.get_website
        context = RequestContext(request)
        context.update({
            "entity": self.entity,
            "title": self.title,
            "meta": self.meta,
            "pagetitle": self.pagetitle,
            "main_page_body_file": self.main_page_body_file,
            "intro_page_placeholder": self.entity.news_page_intro,
            'lister': self.lister,
            }
            )
        
        return render_to_response(
            "arkestra_utilities/entity_auto_page.html",
            context,
            )
    

class NewsAndEventsView(ArkestraGenericView):
    def get(self, request, *args, **kwargs):
        super(NewsAndEventsView, self).get(request, *args, **kwargs)
        
        self.lister = NewsAndEventsCurrentLister(
            entity=self.entity,
            request=self.request
            )
        
        self.lister.get_items()
        
        self.main_page_body_file = "arkestra/generic_lister.html"
        self.meta = {"description": "Recent news and forthcoming events",}
        self.title = unicode(self.entity) + u" news & events"
        if MULTIPLE_ENTITY_MODE:
            self.pagetitle = unicode(self.entity) + u" news & events"
        else:
            self.pagetitle = "News & events"
        
        return self.response(request)

class NewsArchiveView(ArkestraGenericView):
    def get(self, request, *args, **kwargs):
        self.get_entity()
        
        self.lister = NewsArchiveLister(
            entity=self.entity,
            request=self.request
            )
        
        self.lister.get_items()
        
        self.main_page_body_file = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable archive of news items",}
        self.title = u"News archive for %s" % unicode(self.entity)
        self.pagetitle = u"News archive for %s" % unicode(self.entity)
        
        return self.response(request)
        
class EventsArchiveView(ArkestraGenericView):
    def get(self, request, *args, **kwargs):
        self.get_entity()
        
        self.lister = EventsArchiveLister(
            entity=self.entity,
            request=self.request
            )
        
        self.lister.get_items()

        self.main_page_body_file = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable archive of events",}
        self.title = u"Events archive for %s" % unicode(self.entity)
        self.pagetitle = u"Events archive for %s" % unicode(self.entity)
        
        return self.response(request)


class EventsForthcomingView(ArkestraGenericView):
    def get(self, request, *args, **kwargs):
        self.get_entity()
        
        self.lister = EventsForthcomingLister(
            entity=self.entity,
            request=self.request
            )
        
        self.lister.get_items()

        self.main_page_body_file = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable list of forthcoming events",}
        self.title = u"Forthcoming events for %s" % unicode(self.entity)
        self.pagetitle = u"Forthcoming events for %s" % unicode(self.entity)
        
        return self.response(request)


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
