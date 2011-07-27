from models import NewsArticle, Event

class NewsAndEventsPluginMixin(object):
    def news_style_other_links(self, instance, this_list):
        this_list["other_items"] = []
        if this_list["items"] and instance.view == "current":
            all_items_count = len(this_list["items"])
            if instance.limit_to and all_items_count > instance.limit_to:
                this_list["other_items"] = [{
                    "link":instance.entity.get_related_info_page_url("news-archive"), 
                    "title":"news archive",
                    "count": all_items_count,}]
            print "###", this_list["other_items"]
            return this_list
            
    def events_style_other_links(self, instance, this_list):
        this_list["other_items"] = []
        if instance.view == "current":
                
            if instance.previous_events or instance.forthcoming_events:
                if instance.limit_to and len(instance.events) > instance.limit_to:
                    if instance.forthcoming_events.count() > instance.limit_to:
                        this_list["other_items"].append({
                            "link":instance.entity.get_related_info_page_url("forthcoming-events"), 
                            "title":"all forthcoming events", 
                            "count": instance.forthcoming_events.count(),}
                            )
            if instance.previous_events:
                this_list["other_items"].append({
                    "link":instance.entity.get_related_info_page_url("previous-events"), 
                    "title":"previous events",
                    "count": instance.previous_events.count(),}
                    )    
                
        elif instance.view == "archive":
                
            if instance.forthcoming_events:
                this_list["other_items"] = [{
                    "link":instance.entity.get_related_info_page_url("forthcoming-events"), 
                    "title":"all forthcoming events", 
                    "count": instance.forthcoming_events.count(),}]                
        return this_list

    def get_items(self, instance):
        self.lists = []

        if "news" in instance.display:
            this_list = {"model": NewsArticle,}
            this_list["items"] = NewsArticle.objects.get_items(instance)
            this_list["links_to_other_items"] = self.news_style_other_links
            this_list["heading_text"] = instance.news_heading_text
            print "##", this_list
            self.lists.append(this_list)

        if "events" in instance.display:
            this_list = {"model": Event,}
            this_list["items"] = Event.objects.get_items(instance)
            this_list["links_to_other_items"] = self.events_style_other_links
            this_list["heading_text"] = instance.events_heading_text
            self.lists.append(this_list)