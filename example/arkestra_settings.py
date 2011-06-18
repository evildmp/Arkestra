# These are the only settings you really need.
# If you need to modify other aspects of Arkestra's behaviour, see the
# settings that are available in arkestra_utilities.settings; copy them 
# here and modify them here (not there)

# ------------------------ Arkestra settings

# must match the id of your base or default entity
ARKESTRA_BASE_ENTITY = 1 

# ------------------------ Semantic editor

import os
from settings import STATIC_URL
SEMANTICEDITOR_MEDIA_URL = os.path.join(STATIC_URL, "semanticeditor/")