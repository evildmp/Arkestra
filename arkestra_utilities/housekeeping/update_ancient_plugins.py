"""
This module will update ancient plugins
"""

import django.http as http
from django.db.models import get_model
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from news_and_events.models import NewsAndEventsPlugin

@login_required
def update_ancient_plugins(request, slug = "dryrun"):
    # this dictionary stores the information for the conversions
    if slug == "execute":
        execute = True
    
        for instance in NewsAndEventsPlugin.objects.all():    
            # the older news and events plugin used integers; this will convert and save them
            if instance.format == "0":
                instance.format = "title"
                instance.save()
            elif instance.format == "1":
                instance.format = "details"
                instance.save()
            if instance.display == "0":
                instance.display = "news_and_events"
                instance.save()
            elif instance.display == "1":
                instance.display = "news"
                instance.save()
            elif instance.display == "2":
                instance.display = "events"
                instance.save()                 
    else:
        execute = False
            
    return shortcuts.render_to_response(
        "housekeeping/update_ancient_plugins.html", {
            "execute": execute,
            },
        RequestContext(request),
        )
