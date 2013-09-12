from datetime import datetime

from django.db.models import Q

from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE, PLUGIN_HEADING_LEVEL_DEFAULT

class ArkestraGenericLister(object):

    # menu_cues = menu.menu_dict

    display = ""
    list_format = "vertical"
    layout = ""
    limit_to = None
    group_dates = True
    item_format = "details image"
    order_by = "date"
    heading_level = PLUGIN_HEADING_LEVEL_DEFAULT
    lists = None
    entity = None
    place = None
    person = None
    request = None


    def __init__(self, **kwargs):
        vars(self).update(kwargs)

        self.lists = []

        for kind, listclass in self.listkinds:
            if kind in self.display:
                list_ = listclass(
                    limit_to=self.limit_to,
                    entity=self.entity,
                    place=self.place,
                    person=self.person,
                    order_by=self.order_by,
                    item_format=self.item_format,
                    group_dates=self.group_dates,
                    list_format=self.list_format,
                    request=self.request
                    )

                if list_.items or list_.other_items:
                    self.lists.append(list_)

        self.determine_layout_settings()
        self.set_layout_classes()

    def other_items(self):
        pass

    def determine_layout_settings(self):
        """
        Sets:
            list_format
        """
        # set columns for horizontal lists
        if "horizontal" in self.list_format:
            self.list_format = "row columns%s %s" % (
                self.limit_to,
                self.list_format
                )

            # loop over the list of items
            for list_ in self.lists:
                # list_.items is itself a Python list
                # give each a "column" CSS class
                for item in list_.items:
                    item.column_class = "column"
                # give the first (if it exists) a "firstcolumn" CSS class
                if list_.items:
                    list_.items[0].column_class += " firstcolumn"
                    list_.items[-1].column_class += " lastcolumn"
                # # give the last (if it exists) a "lastcolumn" CSS class
                #     if len(list_.items) > 1:
                #         list_.items[-1].column_class += " lastcolumn"

        elif "vertical" in self.list_format:
            self.list_format = "vertical"

    def set_layout_classes(self):
        """
        Lays out the plugin's divs
        """
        self.row_class="row"
        # if divs will be side-by-side
        if self.layout == "sidebyside" and len(self.lists) > 1:
            self.row_class=self.row_class+" columns" + str(len(self.lists))
            self.lists[0].div_class = "column firstcolumn"
            self.lists[-1].div_class = "column lastcolumn"


class ArkestraGenericList(object):

    # defaults for list instances
    limit_to = None
    entity = None
    order_by = ""
    item_format = "details image"
    type = "plugin"
    group_dates = True
    list_format = "vertical"
    request = None

    item_collections = []
    other_item_kinds = []
    model = None
    item_template = "arkestra/generic_list_item.html"

    def __init__(self, **kwargs):
        vars(self).update(kwargs)
        self.now = datetime.now()

        # methods that are always called by __init__()
        self.set_items_for_context()        # sets items_for_context
        self.create_item_collections()  # sets multiple attributes & self.items
        self.additional_list_processing()

    # subclasses should provide their own versions of these methods if required

    def additional_list_processing(self):
        # call additional methods as required
        pass

    # methods that always get called by additional_list_processing()

    def set_items_for_context(self):
        # usually, the context for lists is the Entity we're publishing the
        # lists for, but this could be Place or Person for Events, for example
        # takes:    self.all_listable_items.objects
        # sets:     self.items_for_context
        if MULTIPLE_ENTITY_MODE and self.entity:
            self.items_for_context = self.model.objects.listable_objects().filter(
                Q(hosted_by=self.entity) | Q(publish_to=self.entity)
                ).distinct()
        else:
            self.items_for_context = self.all_listable_items

    def create_item_collections(self):
        # usually, we can simply pass along the items we have, but sometimes
        # we will need to obtain lists of particular sets of the items - for
        # example, we need various collections to generate Events menus
        # self.other_item_kinds lists these
        # takes:    self.items_for_context
        # sets:     self.items (the main set, always)
        #           self.forthcoming_events (for example, optional)
        #
        self.items = self.items_for_context

    # the following methods are optional; if required, they will be called by
    # self.additional_list_processing()

    # methods for lists that filter and search

    def filter_on_search_terms(self):
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
        for key in self.filter_set.fields:
            if key not in [search_field["field_name"] for search_field in self.search_fields]:
                for query_value in self.request.GET.getlist(key):
                    # the field_name and query_value populate some <input> elements
                    self.hidden_search_fields.append(
                        {
                            "field_name": key,
                            "value": query_value,
                        })

    # other operations on the list of items
    # all take and set self.items

    def remove_expired(self):
        # in some lists, items that are too old should be removed
        pass

    def re_order_by_importance(self):
        # in some lists, items should be re-ordered
        # acts on self.order_by
        pass

    def truncate_items(self):
        # in some lists, we only ask for a certain number of items
        # acts on self.limit_to
        if self.items and len(self.items) > self.limit_to:
            self.items = self.items[:self.limit_to]

    # methods that inspect self.items and set something useful

    def set_show_when(self):
        # in some lists, we regroup by date
        # we only show date groups when warranted
        no_of_get_whens = len(set(getattr(item, "get_when", None) for item in self.items))
        self.show_when = self.group_dates and not ("horizontal" in self.list_format or no_of_get_whens < 2)

    def other_items(self):
        # build a list of links to relevant other items
        # self.other_item_kinds lists these
        # see NewsList.other_items() for an example
        return []
