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

ARKESTRA_BASE_ENTITY = 1

# MULTIPLE_ENTITY_MODE is for projects hosting the site of more than one entity
# This does not necessarily entail a site for complex organisation,
# or for a number of different organisations - being able to redirect 
# news and events items to particular entities for example requires
# MULTIPLE_ENTITY_MODE to be True 

MULTIPLE_ENTITY_MODE = True

# -------- News & Events ----------------------

# How many items should be displayed on main news & events pages, 
# such as /news-and-events
MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH = 6

# in All forthcoming events lists, gather top events  together
COLLECT_TOP_ALL_FORTHCOMING_EVENTS = True

# show event type (e.g. "Seminar")
SHOW_EVENT_TYPES = False

# -------- Headings ----------------------

# global value for the heading level for page titles (e.g. entity names in entity pages)
PAGE_TITLE_HEADING_LEVEL = 1 

# The default (typically, the next down from the PAGE_TITLE_HEADING_LEVEL)
IN_BODY_HEADING_LEVEL = 2
PLUGIN_HEADING_LEVEL_DEFAULT = 2

# The heading levels available to plugins
PLUGIN_HEADING_LEVELS = (
    (0, u"No heading"),
    # (1, u"Heading 1"), # assuming that your templates reserve <h1> for page titles, don't allow for plugins
    (2, u"Heading 2"),
    (3, u"Heading 3"),
    (4, u"Heading 4"),
    (5, u"Heading 5"),
    )

# -------- Django CMS ----------------------

CMS_SEO_FIELDS = True
CMS_MENU_TITLE_OVERWRITE = True

# -------- Menus ----------------------

# Built in menu modifiers are in contacts_and_people.menu

MENU_MODIFIERS  = {"ArkestraPages": ("contacts", "news", "vacancies")}

# Do you want all menu branches to expand? 

EXPAND_ALL_MENU_BRANCHES = True

# -------- Semantic editor ----------------------

# ensure that the highest_page_body_heading_level is made available below

WYM_CONTAINERS = ",\n".join([
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

WYM_TOOLS = ",\n".join([
    "{'name': 'Bold', 'title': 'Strong', 'css': 'wym_tools_strong'}", # not 'bold'
    "{'name': 'Italic', 'title': 'Emphasis', 'css': 'wym_tools_emphasis'}", # and not italic
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

# -------- Django ----------------------

LOGIN_REDIRECT_URL = "/admin/" #what happens after login - why is this required? 
