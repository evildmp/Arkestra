import pickle
import hashlib


def generate_key(*args, **kwargs):
    return hashlib.sha224(pickle.dumps([args, kwargs])).hexdigest()

# define get_fallback_template()
# when we no longer need 2.3 support this can be simplified
try:
    # get_cms_setting exists in django CMS 2.4 and later
    from cms.utils.conf import get_cms_setting

except ImportError:
    # in django CMS 2.3 we use ordinary settings

    from django.conf import settings

    def get_fallback_template():
        return get_fallback_template()

    def get_cms_media_url():
        return settings.CMS_MEDIA_URL

else:
    def get_fallback_template():
        return get_cms_setting("TEMPLATES")[0][0]

    def get_cms_media_url():
        return get_cms_setting("MEDIA_URL")
