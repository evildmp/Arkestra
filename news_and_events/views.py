import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from arkestra_utilities.views import ArkestraGenericView

from models import Event, NewsArticle
from .lister import NewsAndEventsCurrentLister, NewsArchiveLister, \
    EventsArchiveLister, EventsForthcomingLister

from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE


class NewsAndEventsView(ArkestraGenericView):
    auto_page_attribute = "auto_news_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = NewsAndEventsCurrentLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_lister.html"
        self.meta = {"description": "Recent news and forthcoming events"}
        self.title = unicode(self.entity) + u" news & events"
        if MULTIPLE_ENTITY_MODE:
            self.pagetitle = unicode(self.entity) + u" news & events"
        else:
            self.pagetitle = "News & events"

        return self.response(request)


class NewsArchiveView(ArkestraGenericView):
    auto_page_attribute = "auto_news_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = NewsArchiveLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable archive of news items"}
        self.title = u"News archive for %s" % unicode(self.entity)
        self.pagetitle = u"News archive for %s" % unicode(self.entity)

        return self.response(request)


class EventsArchiveView(ArkestraGenericView):
    auto_page_attribute = "auto_news_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = EventsArchiveLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable archive of events"}
        self.title = u"Events archive for %s" % unicode(self.entity)
        self.pagetitle = u"Events archive for %s" % unicode(self.entity)

        return self.response(request)


class EventsForthcomingView(ArkestraGenericView):
    auto_page_attribute = "auto_news_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = EventsForthcomingLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable list of forthcoming events"}
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
        newsarticle = get_object_or_404(
            NewsArticle,
            slug=slug,
            published=True,
            date__lte=datetime.datetime.now()
            )
    return render_to_response(
        "news_and_events/newsarticle.html", {
            "newsarticle": newsarticle,
            "entity": newsarticle.get_hosted_by,
            "meta": {"description": newsarticle.summary}
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
        "news_and_events/event.html", {
            "event": event,
            "entity": event.get_hosted_by,
            "meta": {"description": event.summary}
        },
        RequestContext(request),
        )
