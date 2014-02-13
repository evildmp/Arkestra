import six

from datetime import datetime

from django.db.models import Q

from django_easyfilters import FilterSet

from arkestra_utilities.settings import (
    MULTIPLE_ENTITY_MODE, PLUGIN_HEADING_LEVEL_DEFAULT
    )
from generic_models import ArkestraGenericModel


class ArkestraGenericFilterSet(FilterSet):
    template_file = "django-easyfilters/arkestra_default.html"


class ArkestraGenericList(object):

    limit_to = None
    order_by = ""
    item_format = "details image"
    group_dates = True

    entity = None
    type = "plugin"
    list_format = "vertical"
    request = None

    item_collections = []
    other_item_kinds = []
    model = ArkestraGenericModel
    item_template = "arkestra/generic_list_item.html"

    def __init__(self, **kwargs):
        vars(self).update(kwargs)
        self.now = datetime.now()

    def build(self):
        self.items = self.model.objects.listable_objects()
        # self.set_items_for_entity()    # sets items_for_context
        # self.item1()  # sets multiple attributes & self.items
        # self.truncate_items()
        # self.set_show_when()

    def set_items_for_entity(self):
        # usually, the context for lists is the Entity we're publishing the
        # lists for, but this could be Place or Person for Events, for example
        # takes:    self.items
        # sets:     self.items
        if MULTIPLE_ENTITY_MODE and self.entity:
            self.items = self.items.filter(
                Q(hosted_by=self.entity) | Q(publish_to=self.entity)
                ).distinct()

    def set_items_for_person(self):
        self.items = self.items.filter(please_contact=self.person)

    def create_item_collections(self):
        # usually, we can simply pass along the items we have, but sometimes
        # we will need to obtain lists of particular sets of the items - for
        # example, we need various collections to generate Events menus
        # self.other_item_kinds lists these
        # takes:    self.items
        # sets:     self.items (the main set, always)
        #           self.forthcoming_events (for example, optional)
        #
        pass

    # the following methods are optional; if required, they will be called by
    # self.additional_list_processing()

    # methods for lists that filter and search

    def filter_on_search_terms(self):
        # check each search_field in the filter
        for search_field in self.search_fields:
            field_name = search_field["field_name"]

            # if the field_name's in the URL
            if field_name in self.request.GET:

                # a query dict could contain multiple identical keys
                # but we don't care, we'll only ever work with one
                # and we will discard any others
                query = self.request.GET[field_name]

                # record the URL's query string so we can put it back
                search_field["value"] = query

                q_object = Q()
                for search_key in search_field["search_keys"]:
                    lookup = {search_key: query}
                    q_object |= Q(**lookup)
                self.items = self.items.distinct().filter(q_object)

        # the hidden search fields are where we record query strings from
        # django-easy-filter choices
        self.hidden_search_fields = []

        for field in self.filter_set.fields:
            if isinstance(field, six.string_types):
                key = field
            else:
                key = field[0]
            if key not in [
                search_field["field_name"]
                    for search_field in self.search_fields]:
                for query_value in self.request.GET.getlist(key):
                    # the field_name and query_value populate some <input>
                    # elements
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
        if self.order_by == "importance/date":
            if self.items and len(self.items) > self.limit_to:
                self.items = self.items[:self.limit_to]

        elif self.items.count() > self.limit_to:
            self.items = self.items[:self.limit_to]

    # methods that inspect self.items and set something useful

    def set_show_when(self):
        # in some lists, we regroup by date
        # we only show date groups when warranted
        no_of_get_whens = len(set(
            getattr(item, "get_when", None)
            for item in self.items
            ))
        self.show_when = self.group_dates and not (
            "horizontal" in self.list_format or
            no_of_get_whens < 2
            )

    def other_items(self):
        # build a list of links to relevant other items
        # self.other_item_kinds lists these
        # see NewsList.other_items() for an example
        return []

    def is_showable(self):
        try:
            return self.items.exists()
        except AttributeError:
            if self.items:
                return True
        if self.other_items():
            return True


class ArkestraGenericFilterList(ArkestraGenericList):
    def build(self):
        self.items = self.model.objects.listable_objects()
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)


class ArkestraGenericLister(object):

    # attributes that must be passed on to the Lists
    limit_to = None
    order_by = "date"
    item_format = "details image"
    group_dates = True  # if set_show_when() is used

    # attributes that the Lists don't need
    entity = None
    layout = ""
    heading_level = PLUGIN_HEADING_LEVEL_DEFAULT
    list_format = "vertical"

    # may be required by in GenericList

    # also always required
    display = ""    # what sets of items - i.e. models - to display
    lists = None    # the lists created for each
    request = None

    def __init__(self, **kwargs):
        vars(self).update(kwargs)

        kwargs.setdefault("limit_to", self.limit_to)
        kwargs.setdefault("order_by", self.order_by)
        kwargs.setdefault("item_format", self.item_format)
        kwargs.setdefault("group_dates", self.group_dates)

        self.lists = []

        for kind, listclass in self.listkinds:
            if kind in self.display:

                # any attributes supplied as kwargs
                list_ = listclass(**kwargs)

                list_.build()
                if list_.is_showable():
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

                    # coercing to list() prevents a possible attempt to
                    # apply negative slicing to a queryset
                    # See https://github.com/evildmp/Arkestra/issues/111
                    list(list_.items)[-1].column_class += " lastcolumn"

        elif "vertical" in self.list_format:
            self.list_format = "vertical"

    def set_layout_classes(self):
        """
        Lays out the plugin's divs
        """
        self.row_class = "row"
        # if divs will be side-by-side
        if self.layout == "sidebyside" and len(self.lists) > 1:
            self.row_class = self.row_class+" columns" + str(len(self.lists))
            self.lists[0].div_class = "column firstcolumn"
            self.lists[-1].div_class = "column lastcolumn"
