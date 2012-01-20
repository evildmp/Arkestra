from BeautifulSoup import BeautifulSoup
from cms.plugins.text.models import Text
from arkestra_utilities.modifier_pool import adjuster_pool

def get_placeholder_width(context, plugin):
    """
    Gets the width placeholder in which a plugin finds itself
        
	{% with
	    adjust_width=current_page.flags.no_page_title   # adjust_width depends on some context variable
	    width_adjuster="absolute"                       # the adjustment will be to an absolute value
	    width_adjustment=200                            # the value in pixels
	    
	    image_border_reduction=8
	    
	    background_classes="background"
	    background_adjuster="px"
	    background_adjustment=32
	    %}    
    	{% placeholder body %}
    {% endwith %}

    """
    # try to get placeholder_width context variable; if not, then width;
    # if not, use 100 (100 is for admin)

    placeholder_width = context.get("placeholder_width")
    placeholder_width = placeholder_width or context.get("width")
    placeholder_width = float(placeholder_width or 100.0)

    # run all registered placeholder_width modifiers
    for cls in adjuster_pool.adjusters["placeholder_width"]:
        inst = cls()
        placeholder_width = inst.modify(context, placeholder_width)
        
    return placeholder_width

def get_plugin_ancestry(plugin):
    """
    Builds a list of plugins, from the instance downwards, but excluding the root plugin
    """
    plugins = []
    # print "plugin", type(plugin)
    while plugin.parent:
        plugins.append(plugin)
        plugin = plugin.parent 
    return reversed(plugins)

def calculate_container_width(context, instance, width, auto=False):
    markers = {}

    # we could in theory have nested text/layout plugins, but in practice
    # probably never will - it's not necessary, given the inner row/column
    # capabilities of the semantic editor - so this list of plugins will usually just contain the plugin we're working on 
    plugins = get_plugin_ancestry(instance)
    
    for plugin in plugins:
        # get the body field (i.e. output HTML) of the Text object this item is inserted into
        body = Text.objects.get(id=plugin.parent_id).body 
        # soup it up
        soup = BeautifulSoup(''.join(body)) 
        # find the element with that id in the HTML
        target = soup.find(id="plugin_obj_"+str(plugin.id)) 
                    
        # run plugin_width modifiers
        for cls in adjuster_pool.adjusters["plugin_width"]:
            inst = cls()
            width = inst.modify(context, target, width, auto)

        elements = reversed(target.findParents()) # get the tree of elements and reverse it
        # we start with the root (i.e. document)

        for element in elements:
            # run image_width modifiers
            # check for attributes that have a cumulative adjusting affect - we need to act each time we find one
            for cls in adjuster_pool.adjusters["image_width"]:
                inst = cls()
                width = inst.modify(context, element, width)

            # run mark_and_modify modifiers, to mark only
            # check for attributes that have an effect only once - act after the loop
            for cls in adjuster_pool.adjusters["mark_and_modify"]:
                inst = cls()
                markers = inst.mark(context, element, markers)
            
    # run mark_and_modify modifiers, to modify
    for cls in adjuster_pool.adjusters["mark_and_modify"]:
        inst = cls()
        width = inst.modify(context, markers, width)
        
    return width
