################
The links system
################

The links system is one of the most complex parts of Arkestra.

**************************
The ExternalLinks database
**************************

What happens when saving an ExternalLink in Admin
=================================================

ExternalLinkForm.clean() checks that the link is in order.

If the URL (which must be unique) already exists in the database, an error is raised; if the title already exists, a warning is raised (a duplicate title could be confusing but is not fatal).


`links.utils.get_or_create_external_link()`
-------------------------------------------

When an object that can have an External URL is saved, the ModelAdmin.clean() of that object must call `links.admin.get_or_create_external_link()`, passing it various items of information:

* self.cleaned_data.get("input_url", None), # a manually entered url
* self.cleaned_data.get("external_url", None), # a url chosen with autocomplete
* self.cleaned_data.get("title"), # link title
* self.cleaned_data.get("summary"), # link description

`links.admin.get_or_create_external_link()` checks that information against the database:

*   is the URL scheme of input_url or external_url permitted by `links.utils.check_urls()`?
*   has input_url been provided?
	*   get_or_create an `ExternalLink` based on it
	
**************************
The links schema system
**************************

Any model can be registered with the links system, making it easy to search for - using the admin autocomplete search - and link to published instances of the model.

The registry system works in a similar way to django.contrib.admin.

A `link_schema.py` module is required - see the one in `contacts_and_people` for an example.

Any object we're going to link to needs a particular set of attributes. These can be built in to the model, or if they're not, we need to write a wrapper around the model to provide them.

A list of the needed attributes is in `links.schema_registry.ATTRIBUTES`.

The very simplest case
======================

The model has all the needed attributes already; even the admin has the `search_fields` declared::

    # import the model
    from news_and_events.models import Event
    
    # import the admin class
    from news_and_events.admin import EventAdmin        
    
    # register it
    schema.register(
        models.Event, 
        search_fields=admin.EventAdmin.search_fields
        )

This works because `FormDefinition` does indeed happen to have a (required) `title` attribute, though we won't always be so lucky.

Now when we're using any class that inherits from `links.models.LinkMethodsMixin`, we'll be able to choose the type `FormDefinition`, and search through its instances for one to make a link to.

Nearly as simple
======================

Perhaps the attributes are there, but we need to do a little more work to get hold of them::

    schema.register(
        models.Event, 
        search_fields=admin.EventAdmin.search_fields,
	    # wrapper attributes
	    title='name', 
	    description='some_foreign_key.title', 
	    heading='"Event"'
	    )

Each named argument after search_fields represents a attribute the wrapper will have.

We can use a dotted path to traverse through
object, starting from the linked object.

`description='some_foreign_key.title'`
    use the object's `some_foreign_key.title` for the description. Any
    attribute - a callable or property - will do.

`heading='"Event"'`
    use a static string for the heading under which objects of this type will
    be grouped in lists of links. Both `"'foo'"` and `'"bar"'` work.


Let's do some extra calculation
============================================

This works by providing a callable that takes one argument: the linked object
It can be a lamda function or a external function::

    def some_very_complicated_function(obj):
    	r = []
    	for x in obj.something.all():
    		if x.y:
    			r.append(u"foo: %s" % x.bar)
    		else:
    			r.append(u"stuff: %s" % x.bar)
    	return "<br />".join(r)
    
    schema.register(
        models.Event, 
        search_fields=admin.EventAdmin.search_fields,
    	title=lambda obj: u"%s (%s)" % (unicode(obj), obj.active_count),
    	description=some_very_complicated_function
    	)

Create our own `LinkWrapper` subclass
============================================

We can also create a `LinkWrapper` and provide it with the required attributes. Some of these might do some complex work for us, but here's a simple one first::

    # import the model
    from form_designer.models import FormDefinition    

    # declare a wrapper with a search field
    class FormDefinitionLinkWrapper(LinkWrapper):
        search_fields = ['title',]
            
    # register the wrapper
    schema.register_wrapper(FormDefinition, FormDefinitionLinkWrapper)




 