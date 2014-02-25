import operator
from datetime import datetime, timedelta

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from arkestra_utilities.generic_lister import (
    ArkestraGenericLister, ArkestraGenericList, ArkestraGenericFilterSet
    )

from arkestra_utilities.settings import (
    NEWS_AND_EVENTS_LAYOUT, LISTER_MAIN_PAGE_LIST_LENGTH,
    AGE_AT_WHICH_ITEMS_EXPIRE, MULTIPLE_ENTITY_MODE
    )

from .models import NewsArticle, Event
import menu


class NewsList(ArkestraGenericList):
    model = NewsArticle
    heading_text = _(u"News")

    def remove_expired(self):
        # remove expired
        if AGE_AT_WHICH_ITEMS_EXPIRE:
            expiry_date = datetime.now() - \
                timedelta(days=AGE_AT_WHICH_ITEMS_EXPIRE)
            self.items = self.items.filter(date__gte=expiry_date)

    def other_items(self):
        # supply a list of links to available other items
        other_items = []

        if "archive" in self.other_item_kinds:
            other_items.append({
                "link": self.entity.get_auto_page_url("news-archive"),
                "title": "News archive",
                "count": self.archived_items.count(),
                })

        if "main" in self.other_item_kinds:
            auto_page_title = menu.menu_dict["title_attribute"]

            if not MULTIPLE_ENTITY_MODE:
                title = getattr(self.entity, auto_page_title)
            else:
                title = "%s %s" % (
                    self.entity.short_name,
                    getattr(self.entity, auto_page_title).lower()
                    )

            other_items.append({
                "link": self.entity.get_auto_page_url("news-and-events"),
                "title": title,
                "css_class": "main"
            })

        return other_items

    def re_order_by_importance(self):
        # re-order by importance as well as date
        if self.order_by == "importance/date":
            ordinary_items = []

            # split the within-date items for this entity into two sets
            sticky_items = self.items.order_by('-importance').filter(
                Q(hosted_by=self.entity) | Q(is_sticky_everywhere=True),
                sticky_until__gte=datetime.today(),
                )
            non_sticky_items = self.items.exclude(
                Q(hosted_by=self.entity) | Q(is_sticky_everywhere=True),
                sticky_until__gte=datetime.today(),
                )

            top_items = list(sticky_items)

            # now go through the non-top items, and find any that can be
            # promoted
            # get the set of dates where possible promotable items can be found
            dates = non_sticky_items.dates('date', 'day').reverse()

            for date in dates:

                # get all non-top items from this date
                possible_top_items = non_sticky_items.filter(
                    date__year=date.year,
                    date__month=date.month,
                    date__day=date.day
                    )

                # promotable items have importance > 0
                # add the promotable ones to the top items list
                top_items.extend(possible_top_items.filter(
                    Q(hosted_by=self.entity) | Q(is_sticky_everywhere=True),
                    importance__gte=1)
                    )

                # if this date set contains any unimportant items, then
                # there are no more to promote
                demotable_items = possible_top_items.exclude(
                    Q(hosted_by=self.entity) | Q(is_sticky_everywhere=True),
                    importance__gte=1
                    )
                if demotable_items.count() > 0:
                    # put those unimportant items into ordinary items
                    ordinary_items.extend(demotable_items)
                    # and stop looking for any more
                    break

            # and add everything left in non-sticky items before this date
            if dates:
                remaining_items = non_sticky_items.filter(date__lte=date)
                ordinary_items.extend(remaining_items)
                for item in top_items:
                    item.sticky = True
                    if self.item_format == "title":
                        item.importance = None
                ordinary_items.sort(
                    key=operator.attrgetter('date'),
                    reverse=True
                    )
            self.items = top_items + ordinary_items

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.archived_items = self.items
        self.remove_expired()
        self.re_order_by_importance()
        self.truncate_items()
        self.set_show_when()


class NewsListCurrent(NewsList):
    other_item_kinds = ("archive")


class NewsListPlugin(NewsList):
    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.remove_expired()
        self.re_order_by_importance()  # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()


class NewsListForPerson(NewsList):

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_person(self)
        self.re_order_by_importance()  # expensive; shame it has to be here
        self.set_show_when()


class NewsArkestraGenericFilterSet(ArkestraGenericFilterSet):
    fields = ['date']


class NewsListArchive(NewsList):
    other_item_kinds = ("main")
    filter_set = NewsArkestraGenericFilterSet
    search_fields = [
        {
            "field_name": "text",
            "field_label": "Search title/summary",
            "placeholder": "Search",
            "search_keys": [
                "title__icontains",
                "summary__icontains",
                ],
            },
        ]

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)


class EventsList(ArkestraGenericList):
    model = Event
    heading_text = _(u"Events")
    item_collections = (
        "actual_events",
        "forthcoming_events",
        "previous_events"
        )
    item_template = "news_and_events/event_list_item.html"

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.create_item_collections()
        self.truncate_items()
        self.set_show_when()

    def create_item_collections(self):
        if any(
            kind in self.item_collections
            for kind in (
                "actual_events",
                "forthcoming_events",
                "previous_events"
                )):

            self.actual_events = self.items.filter(
                # an actual event is one that:
                # (either has no parent or whose parent is a series) and
                # is not a series itself
                Q(parent=None) | Q(parent__series=True),
                series=False,
                ).order_by('date', 'start_time')

            # (event starting after today) or (not a single-day
            # event and ends after today)
            forthcoming = Q(date__gte=self.now) | \
                Q(single_day_event=False, end_date__gte=self.now)

            if "forthcoming_events" in self.item_collections:
                self.forthcoming_events = self.actual_events.filter(forthcoming)

            if "previous_events" in self.item_collections:
                self.previous_events = self.actual_events.exclude(
                    forthcoming
                    ).reverse()

            self.items = getattr(self, self.item_collections[0])

    def set_items_for_person(self):
        self.items = self.items.filter(please_contact=self.person) | \
            self.items.filter(featuring=self.person)

    def set_items_for_place(self):
        self.items = self.items.filter(building=self.place)

    def other_items(self):
        other_items = []

        if "forthcoming_events" in self.other_item_kinds:
            other_items.append({
                "link": self.entity.get_auto_page_url("events-forthcoming"),
                "title": "All forthcoming events",
                "count": self.forthcoming_events.count(),
                })

        if "previous_events" in self.other_item_kinds:
            other_items.append({
                "link": self.entity.get_auto_page_url("events-archive"),
                "title": "Previous events",
                "count": self.previous_events.count(),
                })

        if "main" in self.other_item_kinds:
            auto_page_title = menu.menu_dict["title_attribute"]

            if not MULTIPLE_ENTITY_MODE:
                title = getattr(self.entity, auto_page_title)
            else:
                title = "%s %s" % (
                    self.entity.short_name,
                    getattr(self.entity, auto_page_title).lower()
                    )

            other_items.append({
                "link": self.entity.get_auto_page_url("news-and-events"),
                "title": title,
                "css_class": "main"
            })

        return other_items


class EventsListCurrent(EventsList):
    item_collections = ("forthcoming_events", "previous_events")
    other_item_kinds = ("previous_events", "forthcoming_events")


class EventsListPlugin(EventsList):
    item_collections = ("forthcoming_events",)


class EventsListForPlace(EventsList):
    item_collections = ("forthcoming_events",)

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_place()
        self.create_item_collections()
        self.truncate_items()
        self.set_show_when()


class EventsListForPerson(EventsList):
    item_collections = ("forthcoming_events",)

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_person()
        self.create_item_collections()
        self.truncate_items()
        self.set_show_when()


class EventsArkestraGenericFilterSet(ArkestraGenericFilterSet):
    fields = ['date', 'type']


class EventsFilterList(EventsList):
    filter_set = EventsArkestraGenericFilterSet
    search_fields = [
        {
            "field_name": "text",
            "field_label": "Title/summary",
            "placeholder": "Search",
            "search_keys": [
                "title__icontains",
                "summary__icontains",
                ],
            },
        ]

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.create_item_collections()
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)


class EventsListForthcoming(EventsFilterList):
    item_collections = ("forthcoming_events", "previous_events")
    other_item_kinds = ("previous_events", "main")


class EventsListArchive(EventsFilterList):
    item_collections = ("previous_events", "forthcoming_events")
    other_item_kinds = ("forthcoming_events", "main")


class NewsAndEventsCurrentLister(ArkestraGenericLister):
    listkinds = [
        ("news", NewsListCurrent),
        ("events", EventsListCurrent),
        ]
    display = "news events"
    order_by = "importance/date"
    layout = NEWS_AND_EVENTS_LAYOUT
    limit_to = LISTER_MAIN_PAGE_LIST_LENGTH


class NewsAndEventsMenuLister(ArkestraGenericLister):
    listkinds = [
        ("news", NewsListCurrent),
        ("events", EventsListCurrent),
        ]
    display = "news and events"
    limit_to = LISTER_MAIN_PAGE_LIST_LENGTH


class NewsAndEventsPluginLister(ArkestraGenericLister):
    listkinds = [
        ("news", NewsListPlugin),
        ("events", EventsListPlugin),
        ]

    def other_items(self):
        link = self.entity.get_auto_page_url(menu.menu_dict["url_attribute"])
        return [{
            "link": link,
            "title": "More %s" % self.display,
            "css_class": "main"
            }]


class NewsAndEventsPersonLister(ArkestraGenericLister):
    layout = NEWS_AND_EVENTS_LAYOUT
    listkinds = [
        ("news", NewsListForPerson),
        ("events", EventsListForPerson),
        ]
    display = "news events"


class NewsArchiveLister(ArkestraGenericLister):
    listkinds = [("news", NewsListArchive)]
    display = "news"


class EventsArchiveLister(ArkestraGenericLister):
    listkinds = [("events", EventsListArchive)]
    display = "events"


class EventsForthcomingLister(ArkestraGenericLister):
    listkinds = [("events", EventsListForthcoming)]
    display = "events"


class EventsPlaceLister(ArkestraGenericLister):
    listkinds = [("events", EventsListForPlace)]
    display = "events"
