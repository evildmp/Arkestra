#######################
Arkestra templating
#######################

*******************************
Placeholder & image sizing cues
*******************************

Your main site template(s) should include some cues for the image sizing system.

Obviously, these should reflect the site's CSS.

The built-in `arkestra_utilities/templates/arkestra.html` sets some defaults, so if your own template extends that (certainly recommended while you are getting started) you will find that the values below are already set.

They are set using `{% with %}`/`{% endwith %}` around the `{% block body_content %}`. If you want to override any of them in your own template, use `{% with %}`/`{% endwith %}` just *inside* in your template's `{% block body_content %}`, the way `institute.html` does in the example project. 

::

    placeholder_width=960 # the main body, default for all placeholders 
    generic_main_width=523 # width of the main part of a news item, event, etc
    sidebar_image_size="294x196" # images in news, events, etc sidebars
    sidebar_map_size="296x100" # map thumbnail image in events etc sidebars
    entity_map_size="445x100" # map thumbnail image for entites
    person_map_size="445x100" # map thumbnail image for persons
    entity_image_size="445x384" # main entity image
    person_image_size="384x384" # person's main image
    place_image_size="627x418"  # a place's main image
    lightbox_max_dimension=600  # what's the biggest a lightbox can be?
    plugin_thumbnail_size="75x75"  
                                                                     
**************************
{% block main_page_body %}
**************************

Some views, such as for an entity's Contacts & People page or News & Events page, expect your templates to be lined up in the right way. For example:

* the view for a Contacts & People page will load `contacts_and_people/templates/contacts_and_people/arkestra_page.html`
* this extend the template that it gets from the entity's cms.Page: `{% extends entity.get_template %}`
* the site template in its `{% block main_page_body %}` will thus include the file that view has specified, containing the special stuff for that view: `{% include main_page_body_file %}`

So, anything in your template that should *not* end up in pages like Contacts & People should be *inside* `{% block main_page_body %}`, so that it is replaced.

Anything outside that block will appear on those pages too.
