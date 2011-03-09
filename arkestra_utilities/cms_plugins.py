from cms.plugins.twitter.cms_plugins import TwitterSearchPlugin
from arkestra_utilities.models import ArkestraTwitterSearch
from cms.plugin_pool import plugin_pool
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class ArkestraTwitterSearchPlugin(TwitterSearchPlugin):
    text_enabled = True
    render_template = "arkestra_utilities/twitter_search.html"
    model = ArkestraTwitterSearch
    name = _("Arkestra Twitter Search")

    class PluginMedia:
        js = ('%splugins/twitter/js/jquery.tweet.js' % settings.CMS_MEDIA_URL,)
    
plugin_pool.register_plugin(ArkestraTwitterSearchPlugin)