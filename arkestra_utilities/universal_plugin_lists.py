class UniversalPlugin(object):
    def __init__(self, model = None, admin_site = None):
        self.lists = []
        super(UniversalPlugin, self).__init__(model, admin_site)

    def set_defaults(self, instance):
        # set defaults
        instance.view = getattr(instance, "view", "current")
        return

    def add_link_to_main_page(self, instance):
        if instance.type == "plugin" or instance.type == "sub_page":
            if (any(d['items'] for d in self.lists)) and getattr(instance.entity, self.auto_page_attribute, False):
                instance.link_to_main_page = instance.entity.get_related_info_page_url(self.auto_page_slug)
                instance.main_page_name = getattr(instance.entity, self.auto_page_menu_title, "")

    def print_settings(self):
        print "---- plugin settings ----"
        print "self.display", self.display
        print "self.view", self.view
        print "self.order_by", self.order_by
        print "self.group_dates", self.group_dates
        print "self.format", self.format
        print "self.list_format", self.list_format
        print "self.limit_to", self.limit_to
        print "self.layout", self.layout

    def add_links_to_other_items(self, instance):
        if instance.type == "main_page" or instance.type == "sub_page":       
            for this_list in self.lists:
                this_list["links_to_other_items"](instance, this_list)
                
    def news_style_other_links(self, instance, this_list):
        if this_list["items"] and instance.view == "current":
            all_items_count = len(this_list["items"])
            if instance.limit_to and all_items_count > instance.limit_to:
                this_list["other_items"] = [{
                    "link":instance.entity.get_related_info_page_url("news-archive"), 
                    "title":"news archive",
                    "count": all_items_count,}]
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
 
    def set_limits_and_indexes(self, instance):
        for this_list in self.lists:
        
            if this_list["items"] and len(this_list["items"]) > instance.limit_to:
                this_list["items"] = this_list["items"][:instance.limit_to]

            this_list["index_items"] = [item for item in this_list["items"] if not getattr(item, 'sticky', False)] # put non-top items in it
            this_list["no_of_get_whens"] = len(set(item.get_when() for item in this_list["index_items"]))
            if instance.type == "sub_page" and this_list["no_of_get_whens"] > 1: # more than 1 get_when()?
                this_list["index"] = True   # show an index
            this_list["show_when"] = instance.group_dates and not ("horizontal" in instance.list_format or this_list["no_of_get_whens"] < 2)

    def determine_layout_settings(self, instance):
        """
        Sets:
            image_size
            list_format
        
    
        """
        if "image" in instance.format:
            instance.image_size = (75,75)

        # set columns for horizontal lists
        if "horizontal" in instance.list_format:
            instance.list_format = "row columns" + str(instance.limit_to) + " " + instance.list_format

            for this_list in self.lists:
                if this_list["items"]:
                    for item in this_list["items"]:
                        item.column_class = "column"
                    this_list["items"][0].column_class = this_list["items"][0].column_class + " firstcolumn"
                    this_list["items"][-1].column_class = this_list["items"][-1].column_class + " lastcolumn"
    
        elif "vertical" in instance.format:
            instance.list_format = "row columns1"

    def set_layout_classes(self, instance):
        """
        Lays out the plugin's news and events divs
        """
        instance.row_class="row"
        # if news and events will be side-by-side
        if instance.layout == "sidebyside":
            if len(self.lists) > 1:
                instance.row_class=instance.row_class+" columns" + str(len(self.lists))
                self.lists[0]["div_class"] = "column firstcolumn"
                self.lists[-1]["div_class"] = "column lastcolumn"
            # if just news or events, and it needs an index     
            else:
                for this_list in self.lists:
                    if this_list.get("index"):
                        instance.row_class=instance.row_class+" columns3"
                        instance.index_div_class = "column lastcolumn"
                        this_list["div_class"] = "column firstcolumn doublecolumn"
                    # and if it doesn't need an index    
                    else: 
                        instance.row_class=instance.row_class+" columns1"

