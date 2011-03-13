from django.conf import settings

def arkestra_templates(request):
    print "------arkestra_templates context processor-------"
    """
    Adds useful Arkestra information to the context.
    """
    return {
        'page_title_heading_level': settings.PAGE_TITLE_HEADING_LEVEL,
        'h_main_body': settings.H_MAIN_BODY,
        # 'show_venue_in_events_lists': settings.SHOW_VENUE_IN_EVENTS_LISTS, # is this even needed anywhere?  should we show venues by default?
        "show_event_types": settings.SHOW_EVENT_TYPES,
        "multiple_entity_mode": settings.MULTIPLE_ENTITY_MODE,
        }
