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

* title:			the full title of the item
* short_title:		a short version, for lists
* summary: 	    a brief summary, used in lists and on the item's main page
* body: 			a PlaceholderField    
* image:

* hosted_by:		the Entity that hosts or publishes the item
* publish_to:		the other Entities to whose pages it should be published
* please_contact: 	a Person
* importance:		
          
and @properties:

* get_importance(self):	marks items as important, to help gather them together or highlight them in lists as required
* links
* external_url
* is_uninformative():	the item bears little information of its own
* get_hosted_by:
* get_template:	the template of the webpage of the entity of this item
* get_entity:
* get_website:
    
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

To `urls.py` add a url pattern::

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

The best thing to do is to have a look at the actual `news_and_events/newsarticle.html`.

Same salient points: 

* {% extends newsarticle.get_template %} - see ArkestraGenericModel.get_template, above
* page furniture, such as the metadata, will be handled by the template it extends 


***********
managers.py
***********

It's useful to give your model a manager. You don't *need* to, but it helps keep things tidy, and we'll use one in this example. In particular, if you want to make use of the ArkestraGenericPlugin, that makes use of a `get_items()` method on your manager.

Inherit the generic model manager::

	from arkestra_utilities.managers import ArkestraGenericModelManager

At present this only contains::

	    def get_by_natural_key(self, slug):
	        return self.get(slug=slug)

but in the future it might acquire more.

Define your manager and give it a `get_items()` method::

	class NewsArticleManager(ArkestraGenericModelManager):
	    def get_items(self, instance):
			# just for now, we will return all the objects of this model
	        return self.model.objects.all()

`get_items()` can be very complex - see the news_and_events.EventManager for a particularly complex example.

The `instance` argument for the manager is actually an instance of the plugin model class, which functions as a reasonably convenient API.

Go back to your model and add an attribute so it knows about the manager::

    objects = NewsArticleManager()


*******************
models.py (again)
*******************

Now let's create a plugin that we can use to list a number of the items in the model we have created.

We have already imported arkestra_utilities.ArkestraGenericPluginOptions. This provides::

* entity: the entity whose items we'll publish (can usually be left blan; Arkestra will work out what to do)
* layout: if there are multiple lists (e.g. news and events), will they be stacked or side-by-side?
* format: title only? details? image?
* heading_level: above the list there'll be a heading
* order_by: date alone, or rank by importance too?
* list format: horizontal or vertical
* group dates: group lists into sublists (of months, usually)
* limit_to: how many items - leave blank for no limit

::
	class NewsAndEventsPlugin(CMSPlugin, ArkestraGenericPluginOptions):

Note that this plugin can handle both news and events

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
