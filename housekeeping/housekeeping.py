"""
This module will convert existing rich text fields to placeholders
"""

import django.http as http
from django.db.models import get_model
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.auth.decorators import login_required


@login_required
def options(request):

    #return http.HttpResponse("fixed")
    return shortcuts.render_to_response(
        "housekeeping/housekeeping.html",
        {},
        RequestContext(request),
        )
