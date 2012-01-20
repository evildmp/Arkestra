from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from cms.models.fields import PlaceholderField

from filer.fields.image import FilerImageField

from links.models import ObjectLink

from contacts_and_people.models import Entity, Person, default_entity_id, default_entity
from contacts_and_people.templatetags.entity_tags import work_out_entity

PLUGIN_HEADING_LEVELS = settings.PLUGIN_HEADING_LEVELS
PLUGIN_HEADING_LEVEL_DEFAULT = settings.PLUGIN_HEADING_LEVEL_DEFAULT

class ArkestraGenericModel(models.Model):
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

    @property
    def has_expired(self):
       # the item is too old to appear in current lists, and should only be listed in archives
       return False
    
    @property
    def get_importance(self):
        if self.importance: # if they are not being gathered together, mark them as important
            return "important"
        else:
            return ""

    @property
    def get_hosted_by(self):
        return self.hosted_by or default_entity
        
    @property
    def get_template(self):
        return self.get_hosted_by.get_template()    
        
    @property
    def get_entity(self):
        """
        Real-world information, can be None
        """
        return self.hosted_by or Entity.objects.get(id=default_entity_id)
    
    @property
    def get_website(self):
        """
        for internal Arkestra purposes only
        """
        if self.get_entity:
            return self.get_entity.get_website
        else:
            return None
            
    @property
    def links(self):
        model = ContentType.objects.get_for_model(self)
        # print model, self.id
        links = ObjectLink.objects.filter(content_type__pk=model.id, object_id = self.id).order_by('destination_content_type')
        # print "links", links
        return links

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


class ArkestraGenericPluginOptions(models.Model):
    class Meta:
        abstract = True
    entity = models.ForeignKey(Entity, null=True, blank=True, 
        help_text="Leave blank for autoselect", 
        related_name="%(class)s_plugin")
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


class ArkestraGenericPluginForm(object):
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


class ArkestraGenericPlugin(object):
    text_enabled = True
    admin_preview = False
    # default render_template - change it in your ArkestraGenericPlugin if required
    render_template = "arkestra/universal_plugin_lister.html"

    # def __init__(self, model = None, admin_site = None):
    #     super(ArkestraGenericPlugin, self).__init__(model, admin_site)  

    def set_defaults(self, instance):
        # set defaults
        # ** important ** - these are set only when the render() function is called
        instance.display = getattr(instance, "display", "")
        instance.view = getattr(instance, "view", "current")
        instance.list_format = getattr(instance, "list_format", "vertical")
        instance.layout = getattr(instance, "layout", "")
        instance.limit_to = getattr(instance, "limit_to", None)
        instance.group_dates = getattr(instance, "group_dates", True)
        instance.format = getattr(instance, "format", "details image")
        instance.type = getattr(instance, "type", "plugin") # assume it's a plugin unless otherwise stated
        instance.order_by = getattr(instance, "order_by", "")
        instance.heading_level = getattr(instance, "heading_level", PLUGIN_HEADING_LEVEL_DEFAULT)
        instance.type = getattr(instance, "type", "plugin")
        
        # print "---- plugin settings ----"
        # print "self.display", instance.display
        # print "self.view", instance.view
        # print "self.group_dates", instance.group_dates
        # print "self.format", instance.format
        # print "self.list_format", instance.list_format
        # print "self.order_by", instance.order_by
        # print "self.limit_to", instance.limit_to
        # print "self.layout", instance.layout
        # print "self.heading_level", instance.heading_level
        return

    def add_link_to_main_page(self, instance):
        if instance.type == "plugin" or instance.type == "sub_page":
            if (any(d['items'] for d in self.lists)) and \
                getattr(instance.entity, getattr(self, "menu_cues", {}).get("auto_page_attribute", ""), False): 
                instance.link_to_main_page = instance.entity.get_related_info_page_url(self.menu_cues["url_attribute"])
                instance.main_page_name = getattr(instance.entity, self.menu_cues["title_attribute"])

    # def print_settings(self):
    #     print "---- plugin settings ----"
    #     print "self.display", self.display
    #     print "self.view", self.view
    #     print "self.order_by", self.order_by
    #     print "self.group_dates", self.group_dates
    #     print "self.format", self.format
    #     print "self.list_format", self.list_format
    #     print "self.limit_to", self.limit_to
    #     print "self.layout", self.layout

    def add_links_to_other_items(self, instance):
        if instance.type == "main_page" or instance.type == "sub_page" or instance.type == "menu":     
            for this_list in self.lists:
                # does this list have a function specified that will add the links we need to other items?
                if this_list.get("links_to_other_items"):
                    # call that function
                    this_list["links_to_other_items"](instance, this_list)
                 
    def set_limits_and_indexes(self, instance):
        
        for this_list in self.lists:
            # if a plugin or a main page or menu, eliminate expired items
            if instance.view == "current" and instance.type in ["plugin", "main_page", "menu"]:
                this_list["items"] = [item for item in this_list["items"] if not item.has_expired]
                
            # cut the list down to size if necessary
            if this_list["items"] and len(this_list["items"]) > instance.limit_to:
                this_list["items"] = this_list["items"][:instance.limit_to]
            # gather non-top items into a list to be indexed
            this_list["index_items"] = [item for item in this_list["items"] if not getattr(item, 'sticky', False)]
            # extract a list of dates for the index
            this_list["no_of_get_whens"] = len(set(getattr(item, "get_when", None) for item in this_list["items"]))
            # more than one date in the list: show an index
            if instance.type == "sub_page" and this_list["no_of_get_whens"] > 1:
                this_list["index"] = True
            # we only show date groups when warranted    
            this_list["show_when"] = instance.group_dates and not ("horizontal" in instance.list_format or this_list["no_of_get_whens"] < 2)


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
    
        elif "vertical" in instance.list_format:
            instance.list_format = "vertical"

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

    def get_items(self, instance):
        self.lists = []

    def render(self, context, instance, placeholder):
        instance.entity = getattr(instance, "entity", None) or work_out_entity(context, None)
        self.set_defaults(instance)
        self.get_items(instance)
        self.add_link_to_main_page(instance)
        self.add_links_to_other_items(instance)
        self.set_limits_and_indexes(instance)
        self.determine_layout_settings(instance)
        self.set_layout_classes(instance)
        instance.lists = self.lists
        context.update({ 
            'everything': instance,
            'placeholder': placeholder,
            })
        return context

    def icon_src(self, instance):
        return "/static/plugin_icons/generic.png"
