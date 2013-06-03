import operator
from datetime import datetime, timedelta

from django.db.models import Q

from arkestra_utilities.settings import PLUGIN_HEADING_LEVEL_DEFAULT, MULTIPLE_ENTITY_MODE, AGE_AT_WHICH_ITEMS_EXPIRE

class ArkestraGenericList(object):
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
        
        # all listable items
        self.all_items = self.model.objects.filter(
            published=True,
            date__lte = datetime.now(),            
            in_lists=True,
            )
        
        # filter by entity
        if MULTIPLE_ENTITY_MODE and entity:
            self.items = self.all_items.filter(
                Q(hosted_by=entity) | Q(publish_to=entity)
                ).distinct()
        
        # remove expired
        if AGE_AT_WHICH_ITEMS_EXPIRE and view == "current" and \
            type in ["plugin", "main_page", "menu"]: 
            expiry_date = datetime.now() - \
               timedelta(days=AGE_AT_WHICH_ITEMS_EXPIRE)
            self.items = self.items.filter(date__gte=expiry_date)

        # re-order by importance as well as date
        if order_by == "importance/date":
            ordinary_items = []

            # split the within-date items for this entity into two sets
            sticky_items = self.items.order_by('-importance').filter(
                Q(hosted_by=entity) | Q(is_sticky_everywhere = True),
                sticky_until__gte=datetime.today(),  
                )
            non_sticky_items = self.items.exclude(
                Q(hosted_by=entity) | Q(is_sticky_everywhere = True),
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
                    Q(hosted_by=entity) | Q(is_sticky_everywhere = True),
                    importance__gte = 1)
                    )

                # if this date set contains any unimportant items, then 
                # there are no more to promote
                demotable_items = possible_top_items.exclude(
                    Q(hosted_by=entity) | Q(is_sticky_everywhere = True),
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
           
        
        # cut the list down to size if necessary
        if self.items and len(self.items) > self.limit_to:
            self.items = self.items[:self.limit_to]  
            
        # gather non-top items into a list to be indexed
        self.index_items = [item for item in self.items if not getattr(item, 'sticky', False)]
        # extract a list of dates for the index
        self.no_of_get_whens = len(set(getattr(item, "get_when", None) for item in self.items))
        # more than one date in the list: show an index
        if type == "sub_page" and self.no_of_get_whens > 1:
            self.index = True
        # we only show date groups when warranted    
        self.show_when = group_dates and not ("horizontal" in list_format or self.no_of_get_whens < 2)
        
        
class ArkestraGenericLister(object):

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
                    )
            
                if this_list.items: 
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
                         