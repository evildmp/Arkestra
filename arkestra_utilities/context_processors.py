from django.conf import settings

def arkestra_templates(request):
    print "------arkestra_templates context processor-------"
    """
    Adds useful Arkestra information to the context.
    """
    return {
        'PAGE_TITLE_HEADING_LEVEL': settings.PAGE_TITLE_HEADING_LEVEL,
        'IN_BODY_HEADING_LEVEL': settings.IN_BODY_HEADING_LEVEL,
        "SHOW_EVENT_TYPES": settings.SHOW_EVENT_TYPES,
        "MULTIPLE_ENTITY_MODE": settings.MULTIPLE_ENTITY_MODE,
        }
