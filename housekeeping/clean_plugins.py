"""
This module will remove junk from plugins
"""

from cms.models import Placeholder
from cms.models.pluginmodel import CMSPlugin
from cms.plugins.text.models import Text

from BeautifulSoup import BeautifulSoup
import re

import django.http as http
from django.db.models import get_model
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

@login_required
def clean(request, slug = "dryrun"):
    # this dictionary stores the information for the conversions
    if slug == "execute":
        execute = True
    else:
        execute = False
    trashed_styles=[]
    trashed_nbsps=[]
    trashed_paragraphs=[]
    trashed_style_attributes=[]
    double_spaces=[]
    click_heres=[]
    
    for plugin in Text.objects.all():
        modified = False
                
        if "&#160;" in plugin.body:
            plugin.body = plugin.body.replace("&#160;", " ")
            trashed_nbsps.append(plugin)
            print plugin, "    nbsp"
            modified = True
        
        if u"\xa0" in plugin.body:
            plugin.body = plugin.body.replace(u"\xa0", " ")
            trashed_nbsps.append(plugin)
            print plugin, "    encoded nbsp"
            modified = True
        
        if "  " in plugin.body:
            # plugin.body = plugin.body.replace("  ", " ")
            plugin.body = ' '.join(plugin.body.split())
            double_spaces.append(plugin)
            modified = True
            print plugin, "    doublespace"

        if "<p></p>" in plugin.body or "<p> </p>" in plugin.body:
            plugin.body = plugin.body.replace("<p></p>", "")
            plugin.body = plugin.body.replace("<p> </p>", "")
            trashed_paragraphs.append(plugin)
            modified = True
            print plugin, "    empty p"


        if "click here".lower() in plugin.body.lower():
            click_heres.append(plugin)
            print plugin, "    click here"

        # soup = plugin.body
        soup = BeautifulSoup(''.join(plugin.body)) # soup it up
        style_elements = soup.findAll("style")  # find the element with that id in the HTML
        modified_soup = False
    
        if style_elements:
            [style_element.extract() for style_element in style_elements]
            print plugin, "    style element"
            trashed_styles.append(plugin)
            modified_soup = True

        for attribute in ["style", "width", "height", "align"]:
            
            illegal_attributes = soup.findAll(attrs={attribute: True})
            if illegal_attributes:
                for illegal_attribute in illegal_attributes:
                    print "-------------- illegal attribute --------------"
                    print plugin
                    print "was:", illegal_attribute
                    print "will delete attribute:", attribute, " which is:", illegal_attribute[attribute]
                    del illegal_attribute[attribute]
                    print "now:", illegal_attribute
                modified_soup = True
        if modified_soup:
            modified= True
            plugin.body = unicode(soup)                    

        
        if execute and modified:
            # print "Saving", plugin.cmsplugin_ptr_id, plugin
            plugin.save()
            
    return shortcuts.render_to_response(
        "housekeeping/statistics.html", {
            "execute": execute,
            "trashed_styles": trashed_styles,
            "trashed_nbsps": trashed_nbsps,
            "trashed_paragraphs": trashed_paragraphs,
            "double_spaces": double_spaces,
            "click_heres": click_heres,
            },
        RequestContext(request),
        )
