import operator
from datetime import datetime, timedelta

from arkestra_utilities.generic_lister import ArkestraGenericList, ArkestraGenericLister

from django.db.models import Q

from arkestra_utilities.settings import PLUGIN_HEADING_LEVEL_DEFAULT, MULTIPLE_ENTITY_MODE, AGE_AT_WHICH_ITEMS_EXPIRE

from .models import NewsArticle, Event
from .menu import menu_dict

        
class NewsList(ArkestraGenericList):
    model = NewsArticle       
    item_template = "arkestra/universal_plugin_list_item.html"
    
    def __init__(
        self,
        view,
        limit_to,
        entity,
        order_by, 
        type,
        format,
        group_dates,
        list_format,
        ):   

        self.view = view
        self.limit_to = limit_to  
        self.entity = entity
        self.type=type
        self.order_by=order_by
        self.group_dates = group_dates
        self.list_format = list_format

        # as soon as a List class is instantiated we need to find what's in it 
        self.all_listable_items()
        self.filter_by_entity()        
        self.remove_expired()
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        
        # self.index_items()
        # self.set_show_when()    

    # methods that actually generate the contents of the list
    
    def all_listable_items(self):
        # all listable items
        self.all_items = self.model.objects.filter(
            published=True,
            date__lte = datetime.now(),            
            in_lists=True,
            )

    def filter_by_entity(self):
        # filter by entity
        if MULTIPLE_ENTITY_MODE and self.entity:
            self.items = self.all_items.filter(
                Q(hosted_by=self.entity) | Q(publish_to=self.entity)
                ).distinct() 
                
    def remove_expired(self):
        # remove expired
        if AGE_AT_WHICH_ITEMS_EXPIRE and self.view == "current" and \
            self.type in ["plugin", "main_page", "menu"]: 
            expiry_date = datetime.now() - \
               timedelta(days=AGE_AT_WHICH_ITEMS_EXPIRE)
            self.items = self.items.filter(date__gte=expiry_date)

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
                    if format == "title":
                        item.importance = None
                ordinary_items.sort(
                    key=operator.attrgetter('date'), 
                    reverse = True
                    )
            self.items = top_items + ordinary_items

    def truncate_items(self):        
        # cut the list down to size if necessary
        if self.items and len(self.items) > self.limit_to:
            self.items = self.items[:self.limit_to]  

    # methods that add meta-information to the List
    
    def index_items(self):
        # gather non-top items into a list to be indexed
        self.index_items = [item for item in self.items if not getattr(item, 'sticky', False)]
        # extract a list of dates for the index
        self.no_of_get_whens = len(set(getattr(item, "get_when", None) for item in self.items))
        # more than one date in the list: show an index
        if self.type == "sub_page" and self.no_of_get_whens > 1:
            self.index = True

    def set_show_when(self):
        # we only show date groups when warranted    
        self.show_when = self.group_dates and not ("horizontal" in self.list_format or self.no_of_get_whens < 2)

    # methods that can be called only when required, e.g. in a template

    def other_items(self):
        if self.items and self.view == "current":
            all_items_count = len(self.all_items)
            if self.limit_to and all_items_count > self.limit_to:
                self.other_items = [{
                    "link": self.entity.get_related_info_page_url("news-archive"), 
                    "title": "News archive",
                    "count": all_items_count,}]
    

class EventsList(ArkestraGenericList):
    model = Event

    def other_links(self):
        if self.view == "current":
                
            if getattr(self, "previous_events", None) or \
                getattr(self, "forthcoming_events", None):
                if self.limit_to and len(self.events) > self.limit_to:
                    if self.forthcoming_events.count() > self.limit_to:
                        self.other_items.append({
                            "link": self.entity.get_related_info_page_url("forthcoming-events"), 
                            "title": "All forthcoming events", 
                            "count": self.forthcoming_events.count(),}
                            )
            if getattr(self, "previous_events", None):
                self.other_items.append({
                    "link": self.entity.get_related_info_page_url("previous-events"), 
                    "title": "Previous events",
                    "count": self.previous_events.count(),}
                    )    
                
        elif self.view == "archive":
                
            if getattr(self, "forthcoming_events", None):
                self.other_items = [{
                    "link": self.entity.get_related_info_page_url("forthcoming-events"), 
                    "title": "All forthcoming events", 
                    "count": self.forthcoming_events.count(),}]                
        
        
class NewsAndEventsLister(ArkestraGenericLister):
     
    menu_cues = menu_dict
    listkinds = [
                ("news", NewsList),
                # ("events", EventsList),
            ]
    

                   


