from django.conf import settings

# *Don't* be tempted to change anything in this file.
# If you do need to change a setting, copy it to your project's settings
# file, and change it there; it'll override the setiing here.

# -------- Fundamental entity settings ----------------------

# ARKESTRA_BASE_ENTITY
# This is the only item you need to put safely in your project's settings file
#
# 1. copy this to arkestra_settings in your project folder
# 2. make sure it's correct
# 3. very rarely, you might have to change it to keep it correct

ARKESTRA_BASE_ENTITY = getattr(settings, "ARKESTRA_BASE_ENTITY", None)

# MULTIPLE_ENTITY_MODE is for projects hosting the site of more than one entity
# This does not necessarily entail a site for complex organisation,
# or for a number of different organisations - being able to redirect 
# news and events items to particular entities for example requires
# MULTIPLE_ENTITY_MODE to be True 

MULTIPLE_ENTITY_MODE = getattr(settings, "MULTIPLE_ENTITY_MODE", True)

DEFAULT_CONTACTS_PAGE_TITLE = getattr(settings, "DEFAULT_CONTACTS_PAGE_TITLE", "Contacts & people")
DEFAULT_NEWS_PAGE_TITLE = getattr(settings, "DEFAULT_NEWS_PAGE_TITLE", "News & events")
DEFAULT_VACANCIES_PAGE_TITLE = getattr(settings, "DEFAULT_VACANCIES_PAGE_TITLE", "Vacancies & studentships")
DEFAULT_PUBLICATIONS_PAGE_TITLE = getattr(settings, "DEFAULT_PUBLICATIONS_PAGE_TITLE", "Publications")

# -------- News & Events ----------------------

# How many items should be displayed on main news & events pages, 
# such as /news-and-events
MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH = getattr(settings, "MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH", 6)

# the age in days at which items can be considered to have expired and should be archived
AGE_AT_WHICH_ITEMS_EXPIRE = getattr(settings, "AGE_AT_WHICH_ITEMS_EXPIRE", 180)

# in All forthcoming events lists, gather top events  together
COLLECT_TOP_ALL_FORTHCOMING_EVENTS = getattr(settings, "COLLECT_TOP_ALL_FORTHCOMING_EVENTS", True)

# show event type (e.g. "Seminar")
SHOW_EVENT_TYPES = getattr(settings, "SHOW_EVENT_TYPES", False)

STANDARD_FEED_ENTRY_COUNT = getattr(settings,'STANDARD_FEED_ENTRY_COUNT', 5)

NEWS_AND_EVENTS_LAYOUT = getattr(settings, "NEWS_AND_EVENTS_LAYOUT", "sidebyside")

# -------- Date formats ----------------------

DATE_FORMAT = getattr(settings, "DATE_FORMAT", 
    {
    "date_groups": "F Y",
    "not_this_year": "jS F Y",
    "not_this_month": "jS F",    
    "this_month": "jS",
    }
    )

# admin

ENABLE_CONTACTS_AND_PEOPLE_AUTH_ADMIN_INTEGRATION = getattr(settings, "ENABLE_CONTACTS_AND_PEOPLE_AUTH_ADMIN_INTEGRATION", False)

# -------- Headings ----------------------

# global value for the heading level for page titles (e.g. entity names in entity pages)
PAGE_TITLE_HEADING_LEVEL = getattr(settings, "PAGE_TITLE_HEADING_LEVEL", 1)

# The default (typically, the next down from the PAGE_TITLE_HEADING_LEVEL)
IN_BODY_HEADING_LEVEL = getattr(settings, "IN_BODY_HEADING_LEVEL", 2)
PLUGIN_HEADING_LEVEL_DEFAULT = getattr(settings, "PLUGIN_HEADING_LEVEL_DEFAULT", 2)

# The heading levels available to plugins
PLUGIN_HEADING_LEVELS = getattr(settings, "PLUGIN_HEADING_LEVELS", (
    (0, u"No heading"),
    # (1, u"Heading 1"), # assuming that your templates reserve <h1> for page titles, don't allow for plugins
    (2, u"Heading 2"),
    (3, u"Heading 3"),
    (4, u"Heading 4"),
    (5, u"Heading 5"),
    )
    )
                                    
# image processing

IMAGESET_ITEM_PADDING = getattr(settings, "IMAGESET_ITEM_PADDING", 10) # should be relative to templates!

PERMITTED_FILETYPES = getattr(settings, "PERMITTED_FILETYPES", ["pdf",])


# links

LINK_SCHEMA = getattr(settings, 'LINK_SCHEMA', {})

# The video processing system

USE_CELERY_FOR_VIDEO_ENCODING = getattr(settings, "USE_CELERY_FOR_VIDEO_ENCODING", False)

# -------- Django CMS ----------------------

CMS_SEO_FIELDS = getattr(settings, "CMS_SEO_FIELDS", True)
CMS_MENU_TITLE_OVERWRITE = getattr(settings, "CMS_MENU_TITLE_OVERWRITE", True)

# -------- Menus ----------------------

# Built in menu modifiers are in contacts_and_people.menu


from news_and_events.menu import menu_dict as news_and_events_menu
from contacts_and_people.menu import menu_dict as contacts_and_people_menu
from vacancies_and_studentships.menu import menu_dict as vacancies_and_studentships_menu


ARKESTRA_MENUS = getattr(settings, "ARKESTRA_MENUS", [
    news_and_events_menu,
    contacts_and_people_menu,
    vacancies_and_studentships_menu,
    ]
    )

# Do you want all menu branches to expand? 

EXPAND_ALL_MENU_BRANCHES = getattr(settings, "EXPAND_ALL_MENU_BRANCHES", False)

# -------- Semantic editor ----------------------

# ensure that the highest_page_body_heading_level is made available below

WYM_CONTAINERS = getattr(settings, "WYM_CONTAINERS", 
    ",\n".join([
        "{'name': 'P', 'title': 'Paragraph', 'css': 'wym_containers_p'}",
    #    "{'name': 'H1', 'title': 'Heading_1', 'css': 'wym_containers_h1'}", # I assume you reserve <h1> for your page templates
        "{'name': 'H2', 'title': 'Heading_2', 'css': 'wym_containers_h2'}",
        "{'name': 'H3', 'title': 'Heading_3', 'css': 'wym_containers_h3'}",
        "{'name': 'H4', 'title': 'Heading_4', 'css': 'wym_containers_h4'}",
        "{'name': 'H5', 'title': 'Heading_5', 'css': 'wym_containers_h5'}",
        "{'name': 'H6', 'title': 'Heading_6', 'css': 'wym_containers_h6'}",
    #    "{'name': 'PRE', 'title': 'Preformatted', 'css': 'wym_containers_pre'}",
       "{'name': 'BLOCKQUOTE', 'title': 'Blockquote', 'css': 'wym_containers_blockquote'}",
       # "{'name': 'TH', 'title': 'Table_Header', 'css': 'wym_containers_th'}", # not ready for this yet
    ])
    )


WYM_TOOLS = getattr(settings, "WYM_TOOLS", 
    ",\n".join([
        "{'name': 'Italic', 'title': 'Emphasis', 'css': 'wym_tools_emphasis'}", # and not italic
        "{'name': 'Bold', 'title': 'Strong', 'css': 'wym_tools_strong'}", # not 'bold'
        "{'name': 'InsertUnorderedList', 'title': 'Unordered_List', 'css': 'wym_tools_unordered_list'}",
        "{'name': 'InsertOrderedList', 'title': 'Ordered_List', 'css': 'wym_tools_ordered_list'}",
        "{'name': 'Indent', 'title': 'Indent', 'css': 'wym_tools_indent'}", # should be 'nest'
        "{'name': 'Outdent', 'title': 'Outdent', 'css': 'wym_tools_outdent'}", # should be 'unnest'
        # "{'name': 'Superscript', 'title': 'Superscript', 'css': 'wym_tools_superscript'}",
        # "{'name': 'Subscript', 'title': 'Subscript', 'css': 'wym_tools_subscript'}",
        "{'name': 'Undo', 'title': 'Undo', 'css': 'wym_tools_undo'}",
        "{'name': 'Redo', 'title': 'Redo', 'css': 'wym_tools_redo'}",
        # "{'name': 'Paste', 'title': 'Paste_From_Word', 'css': 'wym_tools_paste'}",
        "{'name': 'ToggleHtml', 'title': 'HTML', 'css': 'wym_tools_html'}",
        #"{'name': 'CreateLink', 'title': 'Link', 'css': 'wym_tools_link'}",
        #"{'name': 'Unlink', 'title': 'Unlink', 'css': 'wym_tools_unlink'}",
        #"{'name': 'InsertImage', 'title': 'Image', 'css': 'wym_tools_image'}",
        # "{'name': 'InsertTable', 'title': 'Table', 'css': 'wym_tools_table'}", # not ready for this yet
        #"{'name': 'Preview', 'title': 'Preview', 'css': 'wym_tools_preview'}",
    ])
    )
    
WYM_CLASSES = ""
WYM_STYLES = ""
# -------- Django ----------------------

LOGIN_REDIRECT_URL = getattr(settings, "LOGIN_REDIRECT_URL", "/admin/") #what happens after login - why is this required? 
