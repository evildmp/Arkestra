import django.http as http
from django.db.models import get_model
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

from convert_to_placeholders import convert 
from tidy_links import tidy_links 

@login_required
def tasks(request, task = None, action = "dryrun"):
    report = {}

    if task == "convert-placeholders":
        report = convert(action)
    elif task == "tidy-links":
        report = tidy_links(action)
    else:
        # nothing matched, so just do the menu
        return shortcuts.render_to_response(
        "housekeeping/housekeeping.html", {
                "base_template": settings.CMS_TEMPLATES[0][0],
                },
            RequestContext(request),
            )
        
    return shortcuts.render_to_response(
        report["template"], {
            "task": task,
            "action": action,
            "report": report,
            "base_template": settings.CMS_TEMPLATES[0][0],
            },
        RequestContext(request),
        )
                                           