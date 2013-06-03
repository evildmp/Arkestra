from arkestra_utilities.generic_lister import ArkestraGenericList, ArkestraGenericLister

from .models import NewsArticle, Event
from .menu import menu_dict

        
class NewsList(ArkestraGenericList):
    model = NewsArticle       
        
    def other_items(self):
        if self.items and self.view == "current":
            all_items_count = len(self.all_items)
            if self.limit_to and all_items_count > self.limit_to:
                self.other_items = [{
                    "link": self.entity.get_related_info_page_url("news-archive"), 
                    "title": "News archive",
                    "count": all_items_count,}]

        return self.other_items
                                  

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
    

                   


