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
LISTER_MAIN_PAGE_LIST_LENGTH = getattr(settings, "LISTER_MAIN_PAGE_LIST_LENGTH", 6)

# the age in days at which items can be considered to have expired and should be
# archived
AGE_AT_WHICH_ITEMS_EXPIRE = getattr(settings, "AGE_AT_WHICH_ITEMS_EXPIRE", 180)

# in All forthcoming events lists, gather top events  together
COLLECT_TOP_ALL_FORTHCOMING_EVENTS = getattr(settings, "COLLECT_TOP_ALL_FORTHCOMING_EVENTS", True)

# show event type (e.g. "Seminar")
SHOW_EVENT_TYPES = getattr(settings, "SHOW_EVENT_TYPES", False)

STANDARD_FEED_ENTRY_COUNT = getattr(settings,'STANDARD_FEED_ENTRY_COUNT', 5)

NEWS_AND_EVENTS_LAYOUT = getattr(settings, "NEWS_AND_EVENTS_LAYOUT", "sidebyside")

# -------- Date formats ----------------------

DATE_FORMAT = getattr(settings, "ARKESTRA_DATE_FORMATS", "jS F Y")

ARKESTRA_DATE_FORMATS = getattr(settings, "ARKESTRA_DATE_FORMATS",
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

# a dictionary to show how many items per row depending on the number of items
LIGHTBOX_COLUMNS = getattr(
    settings,
    "LIGHTBOX_COLUMNS",
    {1:1, 2:2, 3:3, 4:4, 5:5, 6:3, 7:4, 8:4, 9:3, 10:5, 11:4, 12:4, 13:5, 14:5, 15:5, 16:4, 17:6, 18:6, 19:5, 20:5, 21:6, 22:6, 23:6, 24:6, 25:5 }
    )

PERMITTED_FILETYPES = getattr(settings, "PERMITTED_FILETYPES", ["pdf",])


# links

LINK_SCHEMA = getattr(settings, 'LINK_SCHEMA', {})

# The video processing system

USE_CELERY_FOR_VIDEO_ENCODING = getattr(settings, "USE_CELERY_FOR_VIDEO_ENCODING", False)

VIDEO_HOSTING_SERVICES = getattr(settings, "VIDEO_HOSTING_SERVICES", {
    "vimeo": {"name": "Vimeo", "template": "embedded_video/vimeo.html"},
    "youtube": {"name": "YouTube", "template": "embedded_video/youtube.html"},
    }
    )

# -------- Django CMS ----------------------

CMS_SEO_FIELDS = getattr(settings, "CMS_SEO_FIELDS", True)
CMS_MENU_TITLE_OVERWRITE = getattr(settings, "CMS_MENU_TITLE_OVERWRITE", True)

# -------- Menus ----------------------

# Built in menu modifiers are in contacts_and_people.menu


from news_and_events.menu import menu_dict as news_and_events_menu
from contacts_and_people import menu as contacts_and_people_menu
from vacancies_and_studentships.menu import menu_dict as vacancies_and_studentships_menu


ARKESTRA_MENUS = getattr(
    settings,
    "ARKESTRA_MENUS",
    [
        news_and_events_menu,
        vacancies_and_studentships_menu,
        contacts_and_people_menu.menu_dict,
    ]
)

# Do you want all menu branches to expand?
EXPAND_ALL_MENU_BRANCHES = getattr(settings, "EXPAND_ALL_MENU_BRANCHES", False)


PERSON_TABS = getattr(
    settings, "PERSON_TABS", contacts_and_people_menu.PersonTabs
    )

# -------- Django ----------------------

LOGIN_REDIRECT_URL = getattr(
    settings,
    "LOGIN_REDIRECT_URL",
    "/admin/"
    )
    #  what happens after login - why is this required?
