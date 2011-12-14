#######################
Arkestra generic models
#######################

Arkestra provides a flexible way to query your database for information and have it published - automatically, in the right time, in the right place.

This is a full description of how the news_and_events application does this.

*********
models.py
*********

Import the classes you'll need::

	from arkestra_utilities.generic_models import ArkestraGenericPluginOptions, ArkestraGenericModel
	from arkestra_utilities.mixins import URLModelMixin

Inherit the ones you need into your new model class::

	class NewsArticle(ArkestraGenericModel, URLModelMixin):

You don't need to inherit URLModelMixin, but it can be useful. URLModelMixin provides fields:

* slug
* external_url
                                                                                            
and methods:

* __unicode__() 
* get_absolute_url() 

URLModelMixin is handy if your instances of your model will each have their own page on the site. 

ArkestraGenericModel provides:

``title``
    the full title of the item

``short_title``
    a short version, for lists

``summary``
    a brief summary, used in lists and on the item's main page

``body``
    a PlaceholderField    

``image``
    for the item's page, and to offer a little thumbnail image for lists

``hosted_by``
    the Entity that hosts or publishes the item

``publish_to``
    the other Entities to whose pages it should be published

``please_contact``
    a Person

``importance``
    so Arkestra can highlight it when appropriate

and @properties:


``get_importance``
    marks items as important, to help gather them together or highlight them in lists as required

``is_uninformative``
    the item bears little information of its own

``get_template``
    the template of the webpage of the entity of this item

* ``links``
* ``external_url``
* ``get_hosted_by``
* ``get_entity``
* ``get_website``
    
And you can add whatever fields of your own that are required and ignore the ones that are not.
    
          
********                                                            
admin.py
********

Import some handy mixins::

	from arkestra_utilities.mixins import SupplyRequestMixin, AutocompleteMixin, InputURLMixin, fieldsets
      
* SupplyRequestMixin supplies the context to the admin - you might have a need for it
* AutocompleteMixin
* InputURLMixin
* fieldsets: some handy predefined fieldsets

Define the admin form and class, and do the usual things with them::

	class NewsArticleForm(InputURLMixin):
	    class Meta:
	        model = NewsArticle


	class NewsArticledmin(SupplyRequestMixin, AutocompleteMixin, ModelAdminWithTabsAndCMSPlaceholder):
	    related_search_fields = ['hosted_by', 'external_url',] # autocomplete on these fields

	    def _media(self):
	        return super(AutocompleteMixin, self).media + super(ModelAdminWithTabsAndCMSPlaceholder, self).media
	    media = property(_media)


*******
urls.py
*******

To ``urls.py`` add a url pattern::

    (r"^news/(?P<slug>[-\w]+)/$", "news_and_events.views.newsarticle"),


********
views.py
********
                                                    
We need to provide the view the urlpattern points to::


	def newsarticle(request, slug):
	    """
	    Responsible for publishing news article
	    """
	    newsarticle = get_object_or_404(NewsArticle, slug=slug)
    
	    return render_to_response(
	        "news_and_events/newsarticle.html",
	        {
	        "newsarticle":newsarticle,
	        "entity": newsarticle.hosted_by,
	        "meta": {"description": newsarticle.summary,}
	        },
	        RequestContext(request),
	        )
                                        

********************************
news_and_events/newsarticle.html
********************************

The best thing to do is to have a look at the actual ``news_and_events/newsarticle.html``.

Same salient points: 

* {% extends newsarticle.get_template %} - see ArkestraGenericModel.get_template, above
* page furniture, such as the metadata, will be handled by the template it extends 


***********
managers.py
***********

It's useful to give your model a manager. You don't *need* to, but it helps keep things tidy, and we'll use one in this example. In particular, if you want to make use of the ArkestraGenericPlugin, that makes use of a ``get_items()`` method on your manager.

Inherit the generic model manager::

	from arkestra_utilities.managers import ArkestraGenericModelManager

At present this only contains::

	    def get_by_natural_key(self, slug):
	        return self.get(slug=slug)

but in the future it might acquire more.

Define your manager and give it a ``get_items()`` method::

	class NewsArticleManager(ArkestraGenericModelManager):
	    def get_items(self, instance):
			# just for now, we will return all the objects of this model
	        return self.model.objects.all()

``get_items()`` can be very complex - see the news_and_events.EventManager for a particularly complex example.

The ``instance`` argument for the manager is actually an instance of the plugin model class, which functions as a reasonably convenient API.

Go back to your model and add an attribute so it knows about the manager::

    objects = NewsArticleManager()


**************
cms_plugins.py
**************

The simplest kind of plugin isn't even configurable. You just insert it into your content, and let it do its work. We'll start with one of those::

    from arkestra_utilities.generic_models import ArkestraGenericPlugin

ArkestraGenericPlugin refers throughout to ``instance``. 

``instance`` is the class that defines the behaviour of the plugin in this particular instance. If the plugin is configurable, the instance is the model instance as set up in the Admin; if not, it's just an instance of the same model class created for the purpose, but not stored in the database.

ArkestraGenericPlugin provides a number of methods::

``__init__()``
    set the ``render_template`` to ``arkestra/universal_plugin_lister.html`` by default

``set_defaults()``
    if not already provided, ``instance.view`` is set to "current"    

``render(self, context, instance, placeholder)``
    * works out the entity
    * assumes the ``type`` of the instance is ``plugin`` if not stated otherwise (e.g. a menu generator, a main page generator)
    * changes the render_template from ``arkestra/universal_plugin_lister.html`` if required
    * calls set_defaults() (below)
    * calls get_items() to get items in a list of lists, called ``lists``.
    * calls add_link_to_main_page() to see if we need a link to a main page (e.g. the main news and events page)
    * calls add_links_to_other_items() to see if we should provide links to archives etc
    * calls set_limits_and_indexes() to work out whether we need indexes, or how to truncate lists of items
    * calls set_image_format() to set an image size for thumbnail images
    * calls determine_layout_settings() to set rows/columns and classes for items in the lists
    * calls set_layout_classes() to work out the overall structure (rows/columns) of the plugin output
    Everything it needs to set for the overall information about what's going on in the plugin is set as an attribute of ``instance``, which is then passed to the template as ``everything``. ``lists`` is made an attribute of ``instance``.
    

``set_limits_and_indexes``
    


    def add_link_to_main_page(self, instance):
        if instance.type == "plugin" or instance.type == "sub_page":
            if (any(d['items'] for d in self.lists)) and \
                getattr(instance.entity, self.menu_cues["auto_page_attribute"], False): 
                instance.link_to_main_page = instance.entity.get_related_info_page_url(self.menu_cues["url_attribute"])
                instance.main_page_name = getattr(instance.entity, self.menu_cues["title_attribute"])

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



    class CMSNewsAndEventsPlugin(ArkestraGenericPlugin, NewsAndEventsPluginMixin, AutocompleteMixin, CMSPluginBase):
        name = _("News & events")
        def icon_src(self, instance):
            return "/static/plugin_icons/news_and_events.png"

    plugin_pool.register_plugin(CMSNewsAndEventsPlugin)


*******************
models.py (again)
*******************

Now let's create a plugin that we can use to list a number of the items in the model we have created.

We have already imported arkestra_utilities.ArkestraGenericPluginOptions. This provides::

* entity: the entity whose items we'll publish (can usually be left blank; Arkestra will work out what to do)
* layout: if there are multiple lists (e.g. news and events), will they be stacked or side-by-side?
* format: title only? details? image?
* heading_level: above the list there'll be a heading
* order_by: date alone, or rank by importance too?
* list format: horizontal or vertical
* group dates: group lists into sublists (of months, usually)
* limit_to: how many items - leave blank for no limit

::

	class NewsAndEventsPlugin(CMSPlugin, ArkestraGenericPluginOptions):

Note that this plugin can handle both news and events.

And let's add::

    display = models.CharField("Show", max_length=25,choices = DISPLAY, default = "news events")
    show_previous_events = models.BooleanField()
    news_heading_text = models.CharField(max_length=25, default="News")
    events_heading_text = models.CharField(max_length=25, default="Events")









class NewsAndEventsPlugin(CMSPlugin, ArkestraGenericPluginOptions):

This is in effect the model for the plugin, and will inherit:


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
