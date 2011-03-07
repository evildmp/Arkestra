from django.conf import settings

def arkestra_templates(request):
    print "------arkestra_templates context processor-------"
    """
    Adds useful Arkestra information to the context.
    """
    return {
        'page_title_heading_level': settings.PAGE_TITLE_HEADING_LEVEL,
        'h_main_body': settings.H_MAIN_BODY,
        }
