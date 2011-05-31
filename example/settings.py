import os
import os.path

BASE_PATH = os.path.normpath(os.path.dirname(__file__))

# FIXTURE_DIRS = [os.path.join(PROJECT_DIR, 'fixtures')]

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# ------------------------ misc settings

SITE_ID = 1
INTERNAL_IPS = ('127.0.0.1',)

FILE_UPLOAD_PERMISSIONS = 0644
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400

# ------------------------  admin settings
SERVER_EMAIL = '' # <-- EDIT

ADMINS = () # <-- EDIT

MANAGERS = ADMINS

DATABASES = {} # <-- EDIT

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.

TIME_ZONE = 'Europe/London' 
DATE_FORMAT = "jS F Y"
TIME_FORMAT = "H\.i"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
LANGUAGE_CODE = "en"
USE_I18N = True
gettext = lambda s: s

LANGUAGES = (
('en', gettext('English')),
('cy', gettext('Cymraeg')),
)

CMS_LANGUAGE_CONF = {
    'de':['fr'],
    'en':['fr'],
}
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = BASE_PATH+'/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
g)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'legacy_finders.LegacyAppDirectoriesFinder',    
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lngG56gjhrcuytvutgdjhjd6dkjk3=drp3*%$£k(*' # <-- EDIT

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
#    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.csrf',

    "django.core.context_processors.request",

    "cms.context_processors.media",
    "arkestra_utilities.context_processors.arkestra_templates",
)

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
    )

THUMBNAIL_SUBDIR = "output"
THUMBNAIL_DEBUG = False # if True, will cause template syntax errors for missing images

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',

    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.media.PlaceholderMediaMiddleware', 
)

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_PATH+'/templates/',
)

INSTALLED_APPS = (

     # Django CMS applications

    'cms',
    'menus',
    'appmedia',
    'cms.plugins.text',
    'cms.plugins.snippet',
    'cmsplugin_filer_image',

    # Arkestra applications
    
    'contacts_and_people',
    'news_and_events',
    'links',
    'arkestra_utilities',
    # 'housekeeping', # poor thing, it's in a bit of a mess at the moment
    'arkestra_utilities.admin_tabs_extension',
    'arkestra_utilities.widgets.combobox', # so that static-files picks it up
    # 'vacancies_and_studentships', # not needed for most sistes

    # other applications
    
    'semanticeditor',
    'mptt',
    'easy_thumbnails',
    'typogrify',
    'filer',    
    'widgetry',
    'south',
    # 'features',

    # core Django applications

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.admindocs',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
)

# ------------------------ authentication

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
#    'auth.ldapauth.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PROFILE_MODULE = 'contacts_and_people.Person'

LOGIN_REDIRECT_URL = "/admin/"

ENABLE_CONTACTS_AND_PEOPLE_AUTH_ADMIN_INTEGRATION=True

# Override the server-derived value of SCRIPT_NAME 
# See http://code.djangoproject.com/wiki/BackwardsIncompatibleChanges#lighttpdfastcgiandothers
FORCE_SCRIPT_NAME = ''
# ------------------------ Django CMS

CMS_DEFAULT_TEMPLATE = "arkestra.html"

CMS_TEMPLATES = (
    ('arkestra.html', gettext('Arkestra')),
)

CMS_APPLICATIONS_URLS = (
    ('sampleapp.urls', 'Sample application'),
    ('sampleapp.urlstwo', 'Second sample application'),
)

CMS_PLACEHOLDER_CONF = {                        
    'body': {
        "plugins": (
            'SemanticTextPlugin', 
            'CMSVacanciesPlugin', 
            'CMSNewsAndEventsPlugin', 
            'SnippetPlugin', 
            'LinksPlugin', 
            'CMSPublicationsPlugin', 
            'ImagePlugin', 
            'EntityAutoPageLinkPluginPublisher', 
            'EntityMembersPluginPublisher', 
            'FilerImagePlugin', 
            'EntityDirectoryPluginPublisher', 
            'CarouselPluginPublisher',
            'FocusOnPluginPublisher',
            ),
        "extra_context": {"theme":"16_5", "width":"800",},
        "name": gettext("body"),
    },
}

CMS_NAVIGATION_EXTENDERS = (('example.categories.navigation.get_nodes', 'Categories'),)
CMS_SOFTROOT = True
CMS_MODERATOR = False
CMS_PERMISSION = True
CMS_REDIRECTS = True
CMS_SEO_FIELDS = True
CMS_MENU_TITLE_OVERWRITE = True
CMS_HIDE_UNTRANSLATED = False
CMS_FLAT_URLS = False
CMS_MEDIA_URL = STATIC_URL + 'cms/'

CMS_PAGE_FLAGS = (
    ('no_local_menu', 'Hide local menu') ,
    ('no_page_title', "Don't display page title") ,
    )
    
from arkestra_settings import *
