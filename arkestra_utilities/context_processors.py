from arkestra_utilities.settings import PAGE_TITLE_HEADING_LEVEL, IN_BODY_HEADING_LEVEL, IN_BODY_HEADING_LEVEL, MULTIPLE_ENTITY_MODE

def arkestra_templates(request):
    """
    Adds useful Arkestra information to the context.
    """
    return {
        'PAGE_TITLE_HEADING_LEVEL': PAGE_TITLE_HEADING_LEVEL,
        'IN_BODY_HEADING_LEVEL': IN_BODY_HEADING_LEVEL,
        "SHOW_EVENT_TYPES": IN_BODY_HEADING_LEVEL,
        "MULTIPLE_ENTITY_MODE": MULTIPLE_ENTITY_MODE,
        }
