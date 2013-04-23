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
* ``get_website``
    
And you can add whatever fields of your own that are required and ignore the ones that are not.
    
          
********                                                            
admin.py
********

Import some handy mixins::

	from arkestra_utilities.admin_mixins import SupplyRequestMixin, AutocompleteMixin, InputURLMixin, fieldsets
      
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

``instance`` is the class that defines the behaviour of the plugin in this particular instance. If the plugin is configurable, the instance is the model instance as set up in the Admin; if not, it's just an instance of the same model class created for the purpose, but not stored in the database. If we haven't even created sucha model class ourselves, it will be an instance of ``cms.models.pluginmodel.CMSPlugin``.

ArkestraGenericPlugin provides a number of methods, mostly called by ``render()``:

``render(self, context, instance, placeholder)``
    * works out the entity
    * assumes the ``type`` of the instance is ``plugin`` if not stated otherwise (e.g. a menu generator, a main page generator)
    * changes the render_template from ``arkestra/universal_plugin_lister.html`` if required
    * calls ``set_defaults()`` to set some sensible defaults which may or may not be overridden
    * calls ``get_items()`` to get items in a list of lists, called ``lists``.
    * calls ``add_link_to_main_page()`` to see if we need a link to a main page (e.g. the main news and events page)
    * calls ``add_links_to_other_items()`` to see if we should provide links to archives etc
    * calls ``set_limits_and_indexes()`` to work out whether we need indexes, or how to truncate lists of items
    * calls ``determine_layout_settings()`` to set rows/columns and classes for items in the lists
    * calls ``set_layout_classes()`` to work out the overall structure (rows/columns) of the plugin output
    Everything it needs to set for the overall information about what's going on in the plugin is set as an attribute of ``instance``, which is then passed to the template as ``everything``. ``lists`` is made an attribute of ``instance``.
    
``get_items()`` isn't provided by ArkestraGenericPlugin, except as a dummy that sets an empty ``lists`` - it needs to be provided by whatever subclasses it::

	self.lists = []


This is because ArkestraGenericPlugin won't have any idea how to get items - it doesn't know about content.

::

    class CMSNewsAndEventsPlugin(ArkestraGenericPlugin, CMSPluginBase):
    	# set text_enabled, admin_preview, render_template if the ArkestraGenericPlugin default are not suitable

        # provide an icon for the admin interface
		def icon_src(self, instance):
            return "/static/plugin_icons/news_and_events.png"

    plugin_pool.register_plugin(CMSNewsAndEventsPlugin)

You should now be able to insert the plugin into a placeholder, and examine its output - but there won't be anything in there yet, because ``get_items()`` returns ``[]``.

So let's add a method to our plugin::

    def get_items(self, instance):
        # call the base get_items() to set up our self.lists
		super(CMSPublicationsPlugin, self).get_items(instance)

        # create a dict to store information about the news articles
		news_articles = {}

        # put the actual items in it
		news_articles["items"] = NewsArticle.objects.all()

        # will the plugin publish links to other items (more news, news archive)?
		news_articles["links_to_other_items"] = self.news_style_other_links
		
        # will the plugin publish links to other items (more news, news archive)?
		news_articles["heading_text"] = instance.news_heading_text
            
		# what template will each item in this list use?
		news_articles["item_template"] = "arkestra/universal_plugin_list_item.html"


        self.lists.append(news_articles)

And if we haven't changed ``render_template``, it will use ``arkestra/universal_plugin_lister.html``.  Use ``arkestra/universal_plugin_lister.html`` as a guide to writing your template.
 

add_link_to_main_page()
=======================
                     
To be completed

*******
urls.py
*******

We can use the architecture we have been working with to create an automatic page, for each entity, for this - or these - generic models.

We need a URL pattern for this::

    # named entities' news
    (r"^news/(?P<slug>[-\w]+)/$", "news.views.news"),

    # base entity's news
    (r'^news/$', "news.views.news"),    



********
views.py
********





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
