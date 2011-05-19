from BeautifulSoup import BeautifulSoup
from cms.plugins.text.models import Text
from arkestra_utilities.modifier_pool import adjuster_pool

def get_placeholder_width(context, plugin):
    
    """
    Gets the width placeholder in which a plugin finds itself
        
	{% with
	    adjust_width=current_page.flags.no_page_title 
	    width_adjuster="absolute" 
	    width_adjustment=200 %
	    
	    border_classes="image_borders"
	    border_adjuster="px"
	    border_adjustment=16
	    
	    background_classes="background"
	    background_adjuster="px"
	    background_adjustment=32
	    %}    
    	{% placeholder body %}
    {% endwith %}

    """
    # try to get placeholder_width context variable; if not, then width; if not, use 100 (100 is for admin)
    
    placeholder_width = float(context.get("placeholder_width", context.get("width", 100.0))) 
    print "placeholder width:", placeholder_width

    for cls in adjuster_pool.adjusters["placeholder_width"]:
        inst = cls()
        placeholder_width = inst.modify(context, placeholder_width)
        
    return placeholder_width

def get_plugin_ancestry(plugin):
    """
    Builds a list of plugins, from the instance downwards, but excluding the root plugin
    """
    plugins = []
    print "plugin", type(plugin)
    while plugin.parent:
        plugins.append(plugin)
        plugin = plugin.parent 
    return reversed(plugins)

def calculate_container_width(instance, width, auto = False):
    markers={}

    plugins = get_plugin_ancestry(instance) # we could in theory have nested text/layout plugins, but in practice probably never will - it's not necessary, given the inner row/column capabilities of the semantic editor - so this list of plugins will usually just contain the plugin we're working on 
    
    for plugin in plugins:
        print "start width", width
        print "plugin:", plugin, "id:", plugin.id, "type:", type(plugin) 
        # get the body field (i.e. output HTML) of the Text object this item is inserted into
        body = Text.objects.get(id=plugin.parent_id).body 
        print "parent id:",plugin.parent_id
        # soup it up
        soup = BeautifulSoup(''.join(body)) 
        # find the element with that id in the HTML
        target = soup.find(id="plugin_obj_"+str(plugin.id)) 
                    
        # check for attributes that use the reduce_key
        for cls in adjuster_pool.adjusters["plugin_width"]:
            inst = cls()
            width = inst.modify(target, width, auto)

        elements = reversed(target.findParents()) # get the tree of elements and reverse it
        # we start with the root (i.e. document)

        for element in elements:
            # check for attributes that have a cumulative adjusting affect - we need to act each time we find one
            for cls in adjuster_pool.adjusters["image_width"]:
                inst = cls()
                width = inst.modify(element, width)

            # check for attributes that have an effect only once - act after the loop
            for cls in adjuster_pool.adjusters["mark_and_modify"]:
                inst = cls()
                markers = inst.mark(element, markers)
            
    for cls in adjuster_pool.adjusters["mark_and_modify"]:
        inst = cls()
        width = inst.modify(markers, width)
        
    return width
