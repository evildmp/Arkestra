from models import Vacancy, Studentship

class VacancyStudentshipPluginMixin(object):
    def other_links(self, instance, this_list):
        raise Exception
        # if this_list["items"] and instance.view == "current":
        #     all_items_count = len(this_list["items"])
        #     if instance.limit_to and all_items_count > instance.limit_to:
        #         this_list["other_items"] = [{
        #             "link":instance.entity.get_related_info_page_url("news-archive"), 
        #             "title":"news archive",
        #             "count": all_items_count,}]
        return this_list
            
    def events_style_other_links(self, instance, this_list):
        kind = this_list["heading_text"].lower()    
        this_list["other_items"] = []
        if instance.view == "current":
            if instance.previous_items or instance.forthcoming_items:
                if instance.limit_to and len(instance.items) > instance.limit_to:
                    if instance.forthcoming_items.count() > instance.limit_to:
                        this_list["other_items"].append({
                            "link":instance.entity.get_related_info_page_url("all-open-%s" %kind), 
                            "title":"All open %s" %kind,  
                            "count": instance.forthcoming_items.count(),}
                            )
            if instance.previous_items:
                this_list["other_items"].append({
                    "link":instance.entity.get_related_info_page_url("archived-%s" %kind), 
                    "title":"Archived %s" %kind,
                    "count": instance.previous_items.count(),}
                    )    
                
        elif instance.view == "archive":
                
            if instance.forthcoming_items:
                this_list["other_items"] = [{
                    "link":instance.entity.get_related_info_page_url("current-%s" %kind), 
                    "title":"All open %s" %kind,  
                    "count": instance.forthcoming_items.count(),}]                
        return this_list

    def get_items(self, instance):
        self.lists = []
        if "vacancies" in instance.display:
            this_list = {"model": Vacancy,}
            this_list["items"] = Vacancy.objects.get_items(instance)
            # this_list["other_items"] = []
            this_list["links_to_other_items"] = self.events_style_other_links
            this_list["heading_text"] = instance.vacancies_heading_text
            this_list["item_template"] = "arkestra/universal_plugin_list_item.html"
            self.lists.append(this_list)
            print "**", this_list

        if "studentships" in instance.display:
            this_list = {"model": Studentship,}
            this_list["items"] = Studentship.objects.get_items(instance)
            # this_list["other_items"] = []
            this_list["links_to_other_items"] = self.events_style_other_links
            this_list["heading_text"] = instance.studentships_heading_text
            this_list["item_template"] = "arkestra/universal_plugin_list_item.html"
            self.lists.append(this_list)
