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

# ------------------------ Semantic editor

import os
from settings import STATIC_URL
SEMANTICEDITOR_MEDIA_URL = os.path.join(STATIC_URL, "semanticeditor/")