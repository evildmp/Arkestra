from BeautifulSoup import BeautifulSoup
import re
from cms.plugins.text.models import Text

def get_placeholder_width(context, plugin):
    """
    Gets the width placeholder in which a plugin finds itself
    """
    # plugin previews don't return a width, so let's just say 100...
    # maybe if we get the width into a context processor, it will always be available
    # this really needs sorting out
    width = context.get('width', 100) or 400
    placeholder_width = float(width)
    print "placeholder width:", placeholder_width
    # check for left-hand menu and adjust width accordingly
    # if plugin.page.flags['no_local_menu'] == False:
    #    print "reducing width for Cardiff left-hand menu"
    #    placeholder_width = int(placeholder_width/1.269)
    #    print "placeholder width:", placeholder_width
    return placeholder_width

def get_plugin_ancestry(plugin):
    """
    Builds a list of plugins, from the instance downwards, but excluding the root plugin
    """
    plugins = []
    while plugin.parent:
        plugins.append(plugin)
        plugin = plugin.parent 
    return reversed(plugins)

def calculate_container_width(plugins, width, auto = False):
    """
    These values are given as variables here because we never quite know how values such as 2/0/5 will be calculated - this way, we need not worry what the values will be
    """
    one = 1.0
    half = 1.0/2
    one_third = 1.0/3
    one_quarter = 1.0/4
    one_fifth = 1.0/5
    one_sixth = 1.0/6
    two_thirds = 2.0/3
    three_quarters = 3.0/4
    two_fifths = 2.0/5
    three_fifths = 3.0/5

    column_widths = {
        one: 1.0,
        half:48.5,
        one_third:31.4,
        one_quarter:22.85,
        one_fifth:17.72,
        one_sixth:14.23,
        two_thirds:65.7,
        three_quarters:74.5,
        two_fifths:38.5,
        three_fifths:58.9, }

    # this truth table gives us clues about how to decide on width reductions. The three conditions that make up the key are:
    #   auto, space [the space-on-left/right classes that we use], floated
    # the reduce_by value is a percentage
    reduce_by = {
        (False, False, False): 100.0,
        (False, False, True): 100.0,
        (False, True, False): 67.0,
        (False, True, True): 100.0,
        (True, False, False): 100.0,
        (True, False, True): 50.0,
        (True, True, False): 67.0,
        (True, True, True): 50.0,
        }

    has_borders = False
    space = False
    floated = False

    for plugin in plugins:
        print "start width", width
        print "plugin", type(plugin) 
        body = Text.objects.get(id=plugin.parent_id).body # get the body field of the Text object this item is inserted into
        soup = BeautifulSoup(''.join(body)) # soup it up
        target = soup.find(id="plugin_obj_"+str(plugin.id))  # find the element with that id in the HTML
        grandparent_class = target.parent.parent.get("class", "") # find the image's span's containing div
        print "  grandparent_class:", grandparent_class
        if "space-on" in grandparent_class:
            space = True
        print "  space:", space

        if "images-left" in grandparent_class or "images-right" in grandparent_class:
            floated = True
        
        reduce_key = (auto, space, floated)
        
        print "  reduce key:", reduce_key, "reduceby:", reduce_by[reduce_key]
        
        width = width * reduce_by[reduce_key] / 100
        print "  reduced width: ", width
        print
        
        elements = reversed(target.findParents()) # get the tree of elements and reverse it
        print "  -- examining elements --"        
        for element in elements:
            element_class = element.get("class", "") # and its HTML class
            print  "    element name and class:", element.name, element_class
            # width reduction for borders
            if "image-borders" in element_class:
                has_borders = True
            # width reduction for outlines
            if "outline" in element_class or "tint" in element_class:
                print "  reducing by 32 for outline/tint"
                width = width - 32
            # prove we know when we have found a row 
            if re.search(r"\brow\b", element_class):
                print "    this is a row:", element_class
                if "columns" in element_class:
                    print "    width:", width
            # if this is a column whose parent is a row        
            if re.search(r"\column\b", element_class) and "columns" in element.parent.get("class", ""):
                # columns is the number of columns, or 1 if not specified
                columns = float(element.parent.get("class", "").split("columns")[1][0] or 1)
                print "    this is a column:", element_class
                # if double or triplewidth
                if "triplecolumn" in element_class:
                    columnwidth = 3.0
                elif "doublecolumn" in element_class:
                    columnwidth = 2.0
                else:
                    columnwidth = 1
                print "    this column width:", columnwidth, "/", columns
                # now use the value of columnwidth/columns as a key to the column_widths dict
                width = width * column_widths[columnwidth/columns]/100

    if has_borders:
        print "-16 for borders"
        width = width - 16
        
    return width
