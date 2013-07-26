import operator
from datetime import datetime, timedelta

from arkestra_utilities.generic_lister import ArkestraGenericLister

from django.db.models import Q

from arkestra_utilities.settings import PLUGIN_HEADING_LEVEL_DEFAULT, MULTIPLE_ENTITY_MODE, AGE_AT_WHICH_ITEMS_EXPIRE

from .models import NewsArticle, Event
from .menu import menu_dict

from django_easyfilters import FilterSet

class ItemFilterSet(FilterSet):
    fields = ['date']
        
class ArkestraGenericList(object):
    model = None       
    item_template = "arkestra/universal_plugin_list_item_new.html"
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
    
    def __init__(
        self,
        view="current",
        limit_to=None,
        entity=None,
        order_by="", 
        format="details image",
        type="plugin",
        group_dates=True,
        list_format="vertical",
        request=None,
        ):   

        self.view = view
        self.limit_to = limit_to  
        self.entity = entity
        self.type=type
        self.order_by=order_by
        self.group_dates = group_dates
        self.list_format = list_format
        self.request = request
        
        self.set_all_listable_items()
        self.filter_by_entity() 
        self.items = self.items_for_entity
        
        if self.view == "archive":
            self.apply_filters()
            self.itemfilter = ItemFilterSet(self.items, self.request.GET) 

        else:       
            self.remove_expired()
            self.re_order_by_importance() # expensive; shame it has to be here
            self.truncate_items()
            self.index_items()
            self.set_show_when()    

    # methods that always get called by __init__()
    
    def set_all_listable_items(self):
        # all listable items
        self.all_listable_items = self.model.objects.filter(
            published=True,
            date__lte = datetime.now(),            
            in_lists=True,
            )

    def filter_by_entity(self):
        # filter by entity
        if MULTIPLE_ENTITY_MODE and self.entity:
            self.items_for_entity = self.all_listable_items.filter(
                Q(hosted_by=self.entity) | Q(publish_to=self.entity)
                ).distinct()
            # print self.items_for_entity.count()
            # print self.items_for_entity.query
        else:
            self.items_for_entity = self.all_listable_items
                        
    # further processing

    def apply_filters(self):
        for search_field in self.search_fields:
            field_name = search_field["field_name"]
            if field_name in self.request.GET:
                query = self.request.GET[field_name]
                search_field["value"] = query
            
                q_object = Q()
                for search_key in search_field["search_keys"]:
                    lookup = {search_key: query}
                q_object |= Q(**lookup)
                self.items = self.items.distinct().filter(q_object) 

        self.hidden_search_fields = []
        for key in ItemFilterSet.fields:
            if key not in [search_field["field_name"] for search_field in self.search_fields]:
                for query_value in self.request.GET.getlist(key):
                    # the field_name and query_value populate some <input> elements
                    self.hidden_search_fields.append(
                        {
                            "field_name": key,
                            "value": query_value,                            
                        })
        
    # methods that merely manipulate the contents of the list - all work on 
    # self.items

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

    # methods that inspect the list and return something useful
    def set_show_when(self):
        # we only show date groups when warranted    
        self.show_when = self.group_dates and not ("horizontal" in self.list_format or self.no_of_get_whens < 2)

    def other_items(self):    
        if self.items and self.view == "current":   
            all_items_count = self.items_for_entity.count()
            if self.limit_to and all_items_count > self.limit_to:
                return [{
                    "link": self.entity.get_related_info_page_url("class-news-archive"), 
                    "title": "%s news archive" % self.entity,
                    "count": all_items_count,}]

    def index_items(self):
        # gather non-top items into a list to be indexed
        self.index_items = [item for item in self.items if not getattr(item, 'sticky', False)]
        # extract a list of dates for the index
        self.no_of_get_whens = len(set(getattr(item, "get_when", None) for item in self.items))
        # more than one date in the list: show an index
        if self.type == "sub_page" and self.no_of_get_whens > 1:
            self.index = True

class NewsList(ArkestraGenericList):
    model = NewsArticle

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
        
        
class NewsAndEventsLister(object):
     
    menu_cues = menu_dict
    listkinds = [
                ("news", NewsList),
                ("events", EventsList),
            ]
    
    def __init__(
        self,
        display="",
        view="current",
        list_format="vertical",
        layout="",
        limit_to=None,
        group_dates=True,
        format="details image",
        type="plugin",
        order_by="",
        heading_level=PLUGIN_HEADING_LEVEL_DEFAULT,
        lists=None,
        entity=None,
        request=None  
        ):
        
        self.display = display
        self.view = view
        self.list_format = list_format
        self.layout = layout
        self.limit_to = limit_to
        self.group_dates = group_dates
        self.format = format
        self.type = type
        self.order_by = order_by
        self.heading_level = heading_level
        self.lists = lists or []
        self.entity = entity
        self.request = request
        
    def get_items(self):   
        
        self.lists = []

        for kind, listclass in self.listkinds:
        
            if kind in self.display:
                this_list = listclass(
                    view=self.view,
                    limit_to=self.limit_to,
                    entity=self.entity,
                    order_by=self.order_by,
                    type=self.type,
                    format=self.format,
                    group_dates=self.group_dates,
                    list_format=self.list_format,
                    request=self.request
                    )
            
                self.lists.append(this_list)

    def add_link_to_main_page(self):  
        
        # only plugins and sub_pages need a link to the main page
        auto_page_attribute = self.menu_cues.get("auto_page_attribute", "")
    
        if auto_page_attribute and \
            (self.type == "plugin" or self.type == "sub_page") and \
            (any(lister.items for lister in self.lists)) and \
            getattr(self.entity, auto_page_attribute, False):  
            
            url_attribute = self.menu_cues["url_attribute"]
            title_attribute = self.menu_cues["title_attribute"]
            
            self.link_to_main_page = self.entity.get_related_info_page_url(url_attribute)
            self.main_page_name = getattr(self.entity, title_attribute)  
    
    def add_links_to_other_items(self):
        if self.type == "main_page" or self.type == "sub_page" or \
            self.type == "menu":     
            for this_list in self.lists:    
                this_list.other_links()
                         
                   
    

