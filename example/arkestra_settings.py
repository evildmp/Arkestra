# Before we do anything else, get some default settings built into Arkestra.
# They are not just Arkestra settings, but settings for other applications
# that Arkestra requires to be just so.
 

# These are the only settings you really need.
# If you need to modify other aspects of Arkestra's behaviour, see the
# settings that are available in arkestra_utilities.settings; copy them 
# here and modify them here (not there)

# ------------------------ Arkestra settings

# must match the id of your base or default entity
ARKESTRA_BASE_ENTITY = 1 

# MULTIPLE_ENTITY_MODE is for projects hosting the site of more than one entity
# This does not necessarily entail a site for complex organisation,
# or for a number of different organisations - being able to redirect 
# news and events items to particular entities for example requires
# MULTIPLE_ENTITY_MODE to be True 

MULTIPLE_ENTITY_MODE = True


# how will video be encoded? by a thread? well, that's OK just for proof of concept
# but not really viable for anything else. We can use celery instead - but you have 
# to set it up - see the Django Celery section in settings

USE_CELERY_FOR_VIDEO_ENCODING = False
                                  

# ------------------------ Semantic editor

import os
from settings import STATIC_URL
SEMANTICEDITOR_MEDIA_URL = os.path.join(STATIC_URL, "semanticeditor/")


# ------------------------ Link system
                                           
# what filetypes can the user provide links to?
PERMITTED_FILETYPES = {
    "pdf": "Portable Document Format", 
    "txt": "Plain text", 
    "doc": "MS Word (avoid using if possible)",
    "rtf": "Rich Text Format",
    "csv": "Comma-separated values",
    }
    

# -------- Headings ----------------------

# global value for the heading level for page titles (e.g. entity names in entity pages)
PAGE_TITLE_HEADING_LEVEL = 1 

# The default (typically, the next down from the PAGE_TITLE_HEADING_LEVEL)
IN_BODY_HEADING_LEVEL = 2
PLUGIN_HEADING_LEVEL_DEFAULT = 2