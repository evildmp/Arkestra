import operator
from datetime import datetime, timedelta

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from arkestra_utilities.generic_lister import ArkestraGenericLister, ArkestraGenericList 
from arkestra_utilities.settings import PLUGIN_HEADING_LEVEL_DEFAULT, AGE_AT_WHICH_ITEMS_EXPIRE, NEWS_AND_EVENTS_LAYOUT, MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH

from .models import NewsArticle, Event
import menu

from django_easyfilters import FilterSet


class NewsList(ArkestraGenericList):
    model = NewsArticle
    heading_text = _(u"News")
    
    def set_all_listable_items(self):
        # all listable items
        super(NewsList, self).set_all_listable_items()
        self.all_listable_items = self.all_listable_items.filter(
            date__lte = datetime.now(),            
            )

    def remove_expired(self):
        # remove expired
        if AGE_AT_WHICH_ITEMS_EXPIRE: 
            expiry_date = datetime.now() - \
               timedelta(days=AGE_AT_WHICH_ITEMS_EXPIRE)
            self.items = self.items.filter(date__gte=expiry_date)

    def other_items(self):
        other_items = []
        if "archive" in self.other_item_kinds:
            other_items.append({
                "link": self.entity.get_auto_page_url("news-archive"), 
                "title": "News archive",
                "count": self.items_for_context.count(),})
        if "main" in self.other_item_kinds:
            other_items.append({
                "link": self.entity.get_auto_page_url(menu.menu_dict["url_attribute"]),
                "title": "%s %s" % (
                    self.entity.short_name,
                    getattr(self.entity, menu.menu_dict["title_attribute"]).lower()
                    ),
                "cls": "main"
            })
        return other_items

    def re_order_by_importance(self):
        # re-order by importance as well as date
        if self.order_by == "importance/date":
            ordinary_items = []

            # split the within-date items for this entity into two sets
            sticky_items = self.items.order_by('-importance').filter(
                Q(hosted_by=self.entity) | Q(is_sticky_everywhere = True),
                sticky_until__gte=datetime.today(),  
                )
            non_sticky_items = self.items.exclude(
                Q(hosted_by=self.entity) | Q(is_sticky_everywhere = True),
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
                    Q(hosted_by=self.entity) | Q(is_sticky_everywhere = True),
                    importance__gte = 1)
                    )

                # if this date set contains any unimportant items, then 
                # there are no more to promote
                demotable_items = possible_top_items.exclude(
                    Q(hosted_by=self.entity) | Q(is_sticky_everywhere = True),
                    importance__gte = 1
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
                    reverse = True
                    )
            self.items = top_items + ordinary_items


class NewsFilterSet(FilterSet):
    fields = ['date', 'importance']

class NewsListArchive(NewsList):
    other_item_kinds = ("main")
    filter_set = NewsFilterSet
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

    def additional_list_processing(self):
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET) 
            
            
class NewsListCurrent(NewsList):
    other_item_kinds = ("archive")
    
    def additional_list_processing(self):
        self.remove_expired()
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()    


class NewsListPlugin(NewsList):
    def additional_list_processing(self):
        self.remove_expired()
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()    


class NewsListForPerson(NewsList):
    
    def set_items_for_context(self):
        self.items_for_context = self.all_listable_items.filter(please_contact=self.person)

    def additional_list_processing(self):
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()   


class EventsList(ArkestraGenericList):
    model = Event
    heading_text = _(u"Events")
    item_collections = (
        "actual_events", 
        "forthcoming_events", 
        "previous_events"
        )
    item_template = "news_and_events/event_list_item.html"
    
    def create_item_collections(self):
                
        if any(kind in self.item_collections for kind in ("actual_events", "forthcoming_events", "previous_events")):

            self.actual_events = self.items_for_context.filter(
                # an actual event is one that:
                # (either has no parent or whose parent is a series) and 
                # is not a series itself   
                Q(parent = None) | Q(parent__series = True), 
                series = False,
                ).order_by('date', 'start_time')
              
            # (a single-day event starting after today) or (not a single-day event
            # and ends after today)
            q_object = Q(single_day_event = True, date__gte = self.now) | \
                Q(single_day_event = False, end_date__gte = self.now)
        
            if "forthcoming_events" in self.item_collections:   
                self.forthcoming_events = self.actual_events.filter(q_object)
            
            if "previous_events" in self.item_collections:   
                self.previous_events = self.actual_events.exclude(q_object).reverse()

            self.items = getattr(self, self.item_collections[0])

    def other_items(self):
        other_items = []
        if "forthcoming_events" in self.other_item_kinds:
            other_items.append({
                "link": self.entity.get_auto_page_url("forthcoming-events"), 
                "title": "All forthcoming events",
                "count": self.forthcoming_events.count(),})
        if "previous_events" in self.other_item_kinds:
            other_items.append({
                "link": self.entity.get_auto_page_url("previous-events"), 
                "title": "Archived events",
                "count": self.previous_events.count(),})
        if "main" in self.other_item_kinds:
            other_items.append({
                "link": self.entity.get_auto_page_url(menu.menu_dict["url_attribute"]),
                "title": "%s %s" % (
                    self.entity.short_name,
                    getattr(self.entity, menu.menu_dict["title_attribute"]).lower()
                    ),
                "cls": "main"
            })
        return other_items


class EventsFilterSet(FilterSet):
    fields = ['date', 'type']


class EventsListArchive(EventsList):
    item_collections = ("previous_events", "forthcoming_events")
    other_item_kinds = ("forthcoming_events", "main")
    filter_set = EventsFilterSet
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
    
    def additional_list_processing(self):
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET) 


class EventsListForthcoming(EventsList):
    item_collections = ("forthcoming_events", "previous_events")
    other_item_kinds = ("previous_events", "main")
    
    def additional_list_processing(self):
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET) 


class EventsListCurrent(EventsList):
    item_collections = ("forthcoming_events", "previous_events")
    other_item_kinds = ("previous_events", "forthcoming_events")

    def additional_list_processing(self):
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()   
        
        
class EventsListPlugin(EventsList):
    item_collections = ("forthcoming_events",)
    
    def additional_list_processing(self):
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()   


class EventsListForPlace(EventsList):
    item_collections = ("forthcoming_events",)
    
    def additional_list_processing(self):
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()   

    def set_items_for_context(self):
        self.items_for_context = self.all_listable_items.filter(building=self.place)


class EventsListForPerson(EventsList):
    item_collections = ("forthcoming_events",)
    
    def additional_list_processing(self):
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()   

    def set_items_for_context(self):
        self.items_for_context = self.all_listable_items.filter(featuring=self.person)


class NewsAndEventsCurrentLister(ArkestraGenericLister):
    listkinds=[
        ("news", NewsListCurrent),
        ("events", EventsListCurrent),
            ]
    display="news events"
    order_by="importance/date"
    layout=NEWS_AND_EVENTS_LAYOUT
    limit_to=MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH


class NewsAndEventsMenuLister(ArkestraGenericLister):
    listkinds=[
        ("news", NewsListCurrent),
        ("events", EventsListCurrent),
            ]
    display="news and events"
    limit_to=MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    

class NewsAndEventsPluginLister(ArkestraGenericLister):
    listkinds = [
        ("news", NewsListPlugin),
        ("events", EventsListPlugin),
            ]


    def other_items(self):
        return [{
            "link": self.entity.get_auto_page_url("news-and-events"), 
            "title": "More %s" % self.display,
            "cls": "main"
            }]


class NewsAndEventsPersonLister(ArkestraGenericLister):
    layout=NEWS_AND_EVENTS_LAYOUT
    listkinds = [
        ("news", NewsListForPerson),
        ("events", EventsListForPerson),
            ]
    display="news events"


class NewsArchiveLister(ArkestraGenericLister):
    listkinds=[("news", NewsListArchive)]
    display="news"
    

class EventsArchiveLister(ArkestraGenericLister):
    listkinds=[("events", EventsListArchive)]
    display="events"
    
    
class EventsForthcomingLister(ArkestraGenericLister):
    listkinds=[("events", EventsListForthcoming)]
    display="events"
 
 
class EventsPlaceLister(ArkestraGenericLister):
    listkinds=[("events", EventsListForPlace)]
    display="events"
