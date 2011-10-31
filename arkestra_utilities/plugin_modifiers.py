from modifier_pool import adjuster_pool, WidthAdjuster
import re

"""

There are various kinds of WidthAdjuster modifiers:

* placeholder_width

works out the width of the cms placeholder



* plugin_width

works out the overall width of the plugin (image, carousel, video, whatever) including its borders etc

* image_width

works out the exact size of the images required

* mark_and_modify



"""


class SimplePlaceholderWidthAdjuster(WidthAdjuster):
    kind="placeholder_width"
    
    def modify(self, context, placeholder_width):
        # check for conditions that adjust the placeholder width
        adjust_width = context.get("adjust_width", False)
        # can be "percent", "relative", "absolute", "divider"
        adjuster = context.get("width_adjuster", None) 
        adjustment = float(context.get("width_adjustment", 0))
    
        if adjust_width:
            # print "need to adjust"
            if adjuster == "divider":
                placeholder_width = placeholder_width/adjustment
            elif adjuster == "multiplier":
                placeholder_width = placeholder_width * adjustment
            elif adjuster == "percent":
                placeholder_width = placeholder_width * adjustment/100
            elif adjuster == "relative":
                placeholder_width = placeholder_width + adjustment
            elif adjuster == "absolute":
                placeholder_width = adjustment
            placeholder_width = int(placeholder_width)
            # print "adjusted placeholder width:", placeholder_width
        return placeholder_width


class AutoSpaceFloat(WidthAdjuster):
    """
    this truth table gives us clues about how to decide on width reductions.
    The three conditions that make up the key are: 
        auto
        space [the space-on-left/right classes that we use]
        floated
    the reduce_by value is a percentage
    """
    reduce_by = {
        (False, False, False):  100.0,  # given width, no left/right space, not floated
        (False, False, True):   100.0,  # given width, no left/right space, floated
        (False, True, False):    67.0,  # given width, left/right space, not floated
        (False, True, True):    100.0,  # given width, left/right space, floated
        (True, False, False):   100.0,  # auto width, no left/right space, not floated
        (True, False, True):     50.0,  # auto width, no left/right space, floated
        (True, True, False):     67.0,  # auto width, left/right space, not floated
        (True, True, True):      50.0,  # auto width, left/right space, floated
        }

    space = False
    floated = False
    kind="plugin_width"

    def modify(self, context, target, width, auto):
        # check for attributes that use the reduce_key
        grandparent = target.parent.parent
        if grandparent: 
            grandparent_class = grandparent.get("class", "")
            self.space = "space-on" in grandparent_class
            self.floated = "images-left" in grandparent_class or "images-right" in grandparent_class
        reduce_key = (auto, self.space, self.floated)
        width = width * self.reduce_by[reduce_key] / 100
        return width
        
class ReduceForBackground(WidthAdjuster):
    kind="image_width"
    """
    Do any of the elements containing this image have a background? If so, reduce the width.
    """
    def modify(self, context, element, width):
        element_class = element.get("class", "") # and its HTML class
        background_classes = context.get("background_classes", "outline tint")
        if any((word in element_class for word in background_classes.split())):
            width = width - context.get("background_reduction", 32)
        return width

class ColumnWidths(WidthAdjuster):
    kind="image_width"
    """
    These values are given as variables here because we never quite know how
    values such as 2.0/5 will be calculated - this way, we need not worry what
    the values will be
    """
    one            = 1.0
    half           = 1.0/2
    one_third      = 1.0/3
    one_quarter    = 1.0/4
    one_fifth      = 1.0/5
    one_sixth      = 1.0/6
    two_thirds     = 2.0/3
    three_quarters = 3.0/4
    two_fifths     = 2.0/5
    three_fifths   = 3.0/5

    """
    See the column widths styles in arkestra.css - they need to match these */
    """
    column_widths = {
        one: 1.0,
        half: 48.0,
        one_third: 30.6667,
        one_quarter: 22.0,
        one_fifth: 16.8,
        one_sixth: 13.3333,
        two_thirds: 65.4,
        three_quarters: 74.0,
        two_fifths: 37.73,
        three_fifths: 58.4,
    }
    
    def modify(self, context, element, width):
        # print "============ ColumnWidths "
        element_class = element.get("class", "") # and its HTML class
        # if this is a column whose parent is a row        
        if re.search(r"\column\b", element_class) and "columns" in element.parent.get("class", ""):
            # columns is the number of columns, or 1 if not specified
            columns = float(element.parent.get("class", "").split("columns")[1][0] or 1)
            # print "    this is a column:", element_class
            # if double or triplewidth
            if "triplecolumn" in element_class:
                columnwidth = 3.0
            elif "doublecolumn" in element_class:
                columnwidth = 2.0
            else:
                columnwidth = 1
            # now use the value of columnwidth/columns as a key to the column_widths dict
            width = width * self.column_widths[columnwidth/columns]/100
        return width

class ImageBorders(WidthAdjuster):
    kind="mark_and_modify"
    
    def mark(self, context, element, markers):
        image_border_class = context.get("image_border_class", "image-borders")
        no_image_border_class = context.get("no_image_border_class", "no-image-borders")
        element_class = element.get("class", "") # and its HTML class
        if image_border_class in element_class:
            # print "has borders"
            markers["has_borders"] = True
        if no_image_border_class in element_class:     
            markers["has_borders"] = False
        return markers
    
    def modify(self, context, markers, width):
        if markers.get("has_borders"):
            # print "-16 for borders"
            width = width - context.get("image_border_reduction", 16)
        return width

def register():
    adjuster_pool.register_adjuster(SimplePlaceholderWidthAdjuster)
    adjuster_pool.register_adjuster(AutoSpaceFloat)
    adjuster_pool.register_adjuster(ReduceForBackground)
    adjuster_pool.register_adjuster(ColumnWidths)
    adjuster_pool.register_adjuster(ImageBorders)
