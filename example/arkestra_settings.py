import os
from settings import STATIC_URL

# ------------------------ Arkestra settings

ARKESTRA_BASE_ENTITY = 1 # get this wrong, and you'll be sorry
MULTIPLE_ENTITY_MODE = False # True if you want to be able direct news/events and other items to particular entities - False if they'll all share all of thems
MENU_MODIFIERS  = {"ArkestraPages": ("contacts", "news",)}

# heading levels

h_page_title = PAGE_TITLE_HEADING_LEVEL = 1 # global value for the heading level for page titles (e.g. entity names in entity pages)
H_MAIN_BODY = 2

# a couple of things to explore later
# try tuple( [(i[0],u"") for i in t if i[0]<=cutoff] + [i for i in t if i[0] > cutoff] ) to generate headings
# tuple(i for i in HEADINGS if i[0] == 0 or i[0] > 2)  gives the result  ((0, u'No heading'), (3, u'Heading 3'), (4, u'Heading 4'), (5, u'Heading 5'))

HEADINGS = (
    (0, u"No heading"),
#        (1, u"Heading 1"),
    (2, u"Heading 2"),
    (3, u"Heading 3"),
    (4, u"Heading 4"),
    (5, u"Heading 5"),
    )

CASCADE_NEWS_AND_EVENTS = True # news & events items of children are automatically on parents' pages
NEWS_AND_EVENT_LIMIT_TO = 6
# NEWS_AND_EVENTS_LAYOUT = "sidebyside" # preferred layout for news and events; sidebyside or stacked 
SHOW_VENUE_IN_EVENTS_LISTS = True
SHOW_EVENT_TYPES = False
COLLECT_TOP_EVENTS = False # in long lists, gather top events all together

# ------------------------ Semantic editor

SEMANTICEDITOR_MEDIA_URL = os.path.join(STATIC_URL, "semanticeditor/")

# ensure that the highest_page_body_heading_level is made available below

WYM_CONTAINERS = ",\n".join([
    "{'name': 'P', 'title': 'Paragraph', 'css': 'wym_containers_p'}",
#    "{'name': 'H1', 'title': 'Heading_1', 'css': 'wym_containers_h1'}",
    "{'name': 'H2', 'title': 'Heading_2', 'css': 'wym_containers_h2'}",
    "{'name': 'H3', 'title': 'Heading_3', 'css': 'wym_containers_h3'}",
    "{'name': 'H4', 'title': 'Heading_4', 'css': 'wym_containers_h4'}",
    "{'name': 'H5', 'title': 'Heading_5', 'css': 'wym_containers_h5'}",
    "{'name': 'H6', 'title': 'Heading_6', 'css': 'wym_containers_h6'}",
#    "{'name': 'PRE', 'title': 'Preformatted', 'css': 'wym_containers_pre'}",
   "{'name': 'BLOCKQUOTE', 'title': 'Blockquote', 'css': 'wym_containers_blockquote'}",
   "{'name': 'TH', 'title': 'Table_Header', 'css': 'wym_containers_th'}",
])

WYM_TOOLS = ",\n".join([
    "{'name': 'Bold', 'title': 'Strong', 'css': 'wym_tools_strong'}",
    "{'name': 'Italic', 'title': 'Emphasis', 'css': 'wym_tools_emphasis'}",
    "{'name': 'InsertUnorderedList', 'title': 'Unordered_List', 'css': 'wym_tools_unordered_list'}",
    "{'name': 'InsertOrderedList', 'title': 'Ordered_List', 'css': 'wym_tools_ordered_list'}",
    "{'name': 'Indent', 'title': 'Indent', 'css': 'wym_tools_indent'}",
    "{'name': 'Outdent', 'title': 'Outdent', 'css': 'wym_tools_outdent'}",
    # "{'name': 'Superscript', 'title': 'Superscript', 'css': 'wym_tools_superscript'}",
    # "{'name': 'Subscript', 'title': 'Subscript', 'css': 'wym_tools_subscript'}",
    "{'name': 'Undo', 'title': 'Undo', 'css': 'wym_tools_undo'}",
    "{'name': 'Redo', 'title': 'Redo', 'css': 'wym_tools_redo'}",
    # "{'name': 'Paste', 'title': 'Paste_From_Word', 'css': 'wym_tools_paste'}",
    "{'name': 'ToggleHtml', 'title': 'HTML', 'css': 'wym_tools_html'}",
    #"{'name': 'CreateLink', 'title': 'Link', 'css': 'wym_tools_link'}",
    #"{'name': 'Unlink', 'title': 'Unlink', 'css': 'wym_tools_unlink'}",
    #"{'name': 'InsertImage', 'title': 'Image', 'css': 'wym_tools_image'}",
    "{'name': 'InsertTable', 'title': 'Table', 'css': 'wym_tools_table'}",
    #"{'name': 'Preview', 'title': 'Preview', 'css': 'wym_tools_preview'}",
])

# ------------------------ Links system

LINK_SCHEMA = {
    'newsarticle': {
        'search_fields': ('title',),
        'metadata_field': 'subtitle',
        'heading': 'News articles',
    },
    'person': {
        'search_fields': ('given_name','surname',),
        'heading': 'People',
    },
    'event': {
        'search_fields': ('title',),
        'metadata_field': 'subtitle',
        'heading': 'Events',
    },
    'external_link': {
        'search_fields': ('title', 'url'),
        'metadata_field': 'description',
        'heading': 'External resources',
    },
    'vacancy': {
        'search_fields': ('title',),
        'metadata_field': 'summary',
        'heading': 'Vacancies',
    },
    'page': {
        'search_fields': ('title_set__title',),
        'text_field': 'get_title',
    },
}
