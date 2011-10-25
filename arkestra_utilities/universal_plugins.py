from django.db import models
from django.conf import settings

from cms.models.fields import PlaceholderField

from filer.fields.image import FilerImageField

from contacts_and_people.models import Entity, Person, default_entity_id
from contacts_and_people.templatetags.entity_tags import work_out_entity

PLUGIN_HEADING_LEVELS = settings.PLUGIN_HEADING_LEVELS
PLUGIN_HEADING_LEVEL_DEFAULT = settings.PLUGIN_HEADING_LEVEL_DEFAULT

class UniversalPluginModelManagerMixin(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class UniversalPluginModelMixin(models.Model):
    class Meta:
        abstract = True

    # core fields
    title = models.CharField(max_length=255,
        help_text="e.g. Outrage as man bites dog in unprovoked attack")
    short_title = models.CharField(max_length=255,  null=True, blank=True,
        help_text= u"e.g. Man bites dog (if left blank, will be copied from Title)")
    summary = models.TextField(verbose_name="Summary",
        null=False, blank=False, 
        help_text="e.g. Cardiff man arrested in latest wave of man-on-dog violence (maximum two lines)",)
    body = PlaceholderField('body', help_text="Not used or required for external items")    
    image = FilerImageField(null=True, blank=True)

    # universal plugin fields 
    hosted_by = models.ForeignKey(Entity, default=default_entity_id,
        related_name='%(class)s_hosted_events', null=True, blank=True,
        help_text=u"The entity responsible for publishing this item")
    publish_to = models.ManyToManyField(Entity, null=True, blank=True, related_name="%(class)s_publish_to",
        help_text=u"Use these sensibly - don't send minor items to the home page, for example")
    please_contact = models.ManyToManyField(Person, related_name='%(class)s_person', 
        help_text=u'The person to whom enquiries about this should be directed ', 
        null=True, blank=True)
    IMPORTANCES = (
        (0, u"Normal"),
        (1, u"More important"),
        (10, u"Most important"),
    )
    importance = models.PositiveIntegerField(null=True, blank=False,
        default=0, choices=IMPORTANCES,
        help_text=u"Important items will be featured in lists")

    def get_importance(self):
        if self.importance: # if they are not being gathered together, mark them as important
            return "important"
        else:
            return ""

    @property
    def links(self):
        return object_links(self)

    @property
    def external_url(self):
        # if the inheriting model doesn't have an external_url attribute, we'll give it a None one just in case this is needed
        return None
    
    @property
    def is_uninformative(self):
        if self.external_url or self.body.cmsplugin_set.all() or self.please_contact.all() or self.links:
            return False
        else:
            return True


class UniversalPluginOptions(models.Model):
    class Meta:
        abstract = True
    LAYOUTS = (
        ("sidebyside", u"Side-by-side"),
        ("stacked", u"Stacked"),
        )
    layout = models.CharField("Plugin layout", max_length=25, choices = LAYOUTS, default = "sidebyside")
    FORMATS = (
        ("title", u"Title only"),
        ("details image", u"Details"),
        )
    format = models.CharField("Item format", max_length=25,choices = FORMATS, default = "details image")    
    heading_level = models.PositiveSmallIntegerField(choices = PLUGIN_HEADING_LEVELS, default = PLUGIN_HEADING_LEVEL_DEFAULT)
    ORDERING = (
        ("date", u"Date alone"),
        ("importance/date", u"Importance & date"),
        )
    order_by = models.CharField(max_length = 25, choices=ORDERING, default="importance/date")
    LIST_FORMATS = (
        ("vertical", u"Vertical"),
        ("horizontal", u"Horizontal"),
        )
    list_format = models.CharField("List format", max_length = 25, choices=LIST_FORMATS, default="vertical")
    group_dates = models.BooleanField("Show date groups", default = True)
    limit_to = models.PositiveSmallIntegerField("Maximum number of items", default = 5, null = True, blank = True, 
        help_text = u"Leave blank for no limit")

    def sub_heading_level(self): # requires that we change 0 to None in the database
        if self.heading_level == None: # this means the user has chosen "No heading"
            return 6 # we need to give sub_heading_level a value
        else:
            return self.heading_level + 1 # so if headings are h3, sub-headings are h4


class UniversalPluginForm(object):
    def clean(self):
        if "horizontal" in self.cleaned_data["list_format"]:
            self.cleaned_data["order_by"] = "importance/date"
            self.cleaned_data["format"] = "details image"
            self.cleaned_data["layout"] = "stacked"
            self.cleaned_data["group_dates"] = False
            if self.cleaned_data["limit_to"] >3:
                self.cleaned_data["limit_to"] = 3
            if self.cleaned_data["limit_to"] < 2:
                self.cleaned_data["limit_to"] = 2
        if self.cleaned_data["limit_to"] == 0: # that's a silly number, and interferes with the way we calculate later
            self.cleaned_data["limit_to"] = None
        return self.cleaned_data


class UniversalPlugin(object):
    text_enabled = True
    def __init__(self, model = None, admin_site = None):
        self.render_template = "arkestra/universal_plugin_lister.html"
        self.admin_preview = False
        self.text_enabled = True
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
        if instance.type == "main_page" or instance.type == "sub_page" or instance.type == "menu":     
            for this_list in self.lists:
                this_list["links_to_other_items"](instance, this_list)
                 
    def set_limits_and_indexes(self, instance):
        for this_list in self.lists:
        
            # cut the list down to size if necessary
            if this_list["items"] and len(this_list["items"]) > instance.limit_to:
                this_list["items"] = this_list["items"][:instance.limit_to]

            # gather non-top items into a list to be indexed
            this_list["index_items"] = [item for item in this_list["items"] if not getattr(item, 'sticky', False)]
            # extract a list of dates for the index
            this_list["no_of_get_whens"] = len(set(item.get_when() for item in this_list["items"]))
            # more than one date in the list: show an index
            if instance.type == "sub_page" and this_list["no_of_get_whens"] > 1:
                this_list["index"] = True
            # we only show date groups when warranted    
            this_list["show_when"] = instance.group_dates and not ("horizontal" in instance.list_format or this_list["no_of_get_whens"] < 2)

    def set_image_format(self, instance):
        """
        Sets:
            image_size
        """
        if "image" in instance.format:
            instance.image_size = (75,75)

    def determine_layout_settings(self, instance):
        """
        Sets:
            list_format
        """
        # set columns for horizontal lists
        if "horizontal" in instance.list_format:
            instance.list_format = "row columns" + str(instance.limit_to) + " " + instance.list_format

            for this_list in self.lists:
                this_list["items"] = list(this_list["items"])
                if this_list["items"]:
                    for item in this_list["items"]:
                        item.column_class = "column"
                    if this_list["items"]:
                        this_list["items"][0].column_class = this_list["items"][0].column_class + " firstcolumn"
                        if len(this_list["items"]) > 1:
                            this_list["items"][-1].column_class = this_list["items"][-1].column_class + " lastcolumn"
    
        elif "vertical" in instance.format:
            instance.list_format = "row columns1"

    def set_layout_classes(self, instance):
        """
        Lays out the plugin's divs
        """
        instance.row_class="row"
        # if divs will be side-by-side
        if instance.layout == "sidebyside":
            if len(self.lists) > 1:
                instance.row_class=instance.row_class+" columns" + str(len(self.lists))
                self.lists[0]["div_class"] = "column firstcolumn"
                self.lists[-1]["div_class"] = "column lastcolumn"
            # if just one, and it needs an index     
            else:
                for this_list in self.lists:
                    if this_list.get("index"):
                        instance.row_class=instance.row_class+" columns3"
                        instance.index_div_class = "column lastcolumn"
                        this_list["div_class"] = "column firstcolumn doublecolumn"
                    # and if it doesn't need an index    
                    else: 
                        instance.row_class=instance.row_class+" columns1"

    def render(self, context, instance, placeholder):
        self.set_defaults(instance)

        instance.entity = getattr(instance, "entity", None) or work_out_entity(context, None)
        instance.type = getattr(instance, "type", "plugin")
        render_template = getattr(instance, "render_template", "")
        self.get_items(instance)
        self.add_link_to_main_page(instance)
        self.add_links_to_other_items(instance)
        self.set_limits_and_indexes(instance)
        self.set_image_format(instance)
        self.determine_layout_settings(instance)
        self.set_layout_classes(instance)
        instance.lists = self.lists
        context.update({ 
            'everything': instance,
            'placeholder': placeholder,
            })
        return context
