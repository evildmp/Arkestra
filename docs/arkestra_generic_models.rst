#######################
Arkestra generic models
#######################

Arkestra provides a flexible way to query your database for information and have it published - automatically, in the right time, in the right place.

Say you decide that your record company should publish information about new recordings.

Let's create a model, called "Recording", and assume that it belongs to an application called "recordings". 

You can give it whatever fields you like, but the ArkestraGenericModel gives you some by default (if you don't need them all, simply don't use them).


******************
The model
******************

Create your class, subclassing ArkestraGenericModel:

from arkestra_utilities.generic_models import ArkestraGenericModel

class Recording(ArkestraGenericModel):

This will inherit:

    title			the full title of the item
    short_title		a short version, for lists
    summary 	    a brief summary, used in lists and on the item's main page
    body 			a PlaceholderField    
    image

    hosted_by		the Entity that hosts or publishes the item
    publish_to		the other Entities to whose pages it should be published
    please_contact 	a Person
    importance		

    def get_importance(self):
        if self.importance: # if they are not being gathered together, mark them as important
            return "important"
        else:
            return ""

    @property
    def links(self):
        return self.object_links_set.all()

    @property
    def external_url(self):
        # if the inheriting model doesn't have an external_url attribute, we'll give it a None one just in case this is needed
        return None
    
    @property
    is_uninformative()	the item bears little information of its own
    
Add whatever fields you need of your own - for example:

    release_date
    artist
    formats
    catalogue_number
    
* generate a menu item
* add a url
* add a view    
    

*******************
What a plugin needs
*******************

class MyPluginEditor(CMSPlugin, ArkestraGenericPluginOptions):

This is in effect the model for the plugin, and will inherit:

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

form and admin
==============

from arkestra_utilities.generic_models import ArkestraGenericPlugin, ArkestraGenericPluginForm
from arkestra_utilities.mixins import AutocompleteMixin
 
class PublicationsPluginForm(ArkestraGenericPluginForm, forms.ModelForm):
    pass


class CMSPublicationsPlugin(UniversalPlugin, AutocompleteMixin, CMSPluginBase):
    model = PublicationsPlugin
    name = _("Publications")
    form = PublicationsPluginForm
    auto_page_attribute = "auto_publications_page"
    auto_page_slug = "publications"
    auto_page_menu_title = "publications_page_menu_title"
    # fieldsets = (
    #     (None, {
    #     'fields': (('display', 'layout', 'list_format',),  ( 'format', 'order_by', 'group_dates',), 'limit_to')
    # }),
    #     ('Advanced options', {
    #     'classes': ('collapse',),
    #     'fields': ('entity', 'heading_level', ('news_heading_text', 'events_heading_text'), ('show_previous_events', ),)
    # }),
    # )

    # autocomplete fields
    related_search_fields = ['entity',]

    def get_items(self, instance):
        self.lists = []

        this_list = {"model": Publication,}
        this_list["items"] = Pub.objects.get_items(instance)
        this_list["links_to_other_items"] = self.news_style_other_links
        this_list["heading_text"] = instance.news_heading_text
        this_list["item_template"] = "arkestra/universal_plugin_list_item.html"
        # the following should *also* check this_list["links_to_other_items"] - 
        # but then get_items() will need to call self.add_links_to_other_items() itself
        # this will then mean that news and events pages show two columns if one has links to other items
        if this_list["items"]: 
            self.lists.append(this_list)


    def icon_src(self, instance):
        return "/static/plugin_icons/publications_plugin.png"




****
Menu
****

Every Entity in the system that has Recordings should have a menu item where they're listed.

For now we will just hardcode a little routine into our menu, contacts_and_people.menu, at the comment "# insert nodes for this Entity":

self.create_new_node(
    title = "Recordings",
    url = node.entity.get_related_info_page_url("recordings"), # i.e. /url_of_entity/recordings
    parent = node, 
    ) 				

We'll make this more sophisticated later.

***
URL
***

We need a URL pattern to match that, so you'll need:

    # named entities' recordings
    (r"^recordings/(?P<slug>[-\w]+)/$", "recordings.views.recordings"),

    # base entity's vacancies and studentships
    (r'^recordings/$', "recordings.views.recordings"),    

*****
Views
*****

Your URL is looking for a view:

  


class MyPluginPublisher(ArkestraGenericPlugin, AutocompleteMixin, CMSPluginBase):

This is in effect the admin for the plugin. Its render() method is what publishes the output. It will inherit:

    How to use and abuse this plugin:
    
    first create an instance of the plugin model:
    
        instance = NewsAndEventsPlugin()
    
    set the attributes as required:
    
        instance.display = "events"
        instance.type = "for_place"
        instance.place = self
        instance.view = "current"
        instance.format = "details image"
        
    render it to get back the items you want in instance.lists, if you have the context:
    
        CMSNewsAndEventsPlugin().render(context, instance, None)

    alternatively (this is used in the menus, for example):
    
        plugin = CMSNewsAndEventsPlugin()   
        plugin.get_items(instance)
        plugin.add_links_to_other_items(instance)    
        ... and any operations tests as required
        
    and the NewsAndEventsPlugin() needs to have the lists attribute of CMSNewsAndEventsPlugin()
