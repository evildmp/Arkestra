from django import forms
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from arkestra_utilities.universal_plugins import UniversalPlugin
from arkestra_utilities.universal_plugins import UniversalPluginForm
from arkestra_utilities.mixins import AutocompleteMixin

from contacts_and_people.templatetags.entity_tags import work_out_entity

from models import NewsAndEventsPlugin, NewsArticle, Event
from mixins import NewsAndEventsPluginMixin

class NewsAndEventsPluginForm(UniversalPluginForm, forms.ModelForm):
    class Meta:
        model = NewsAndEventsPlugin


class CMSNewsAndEventsPlugin(UniversalPlugin, NewsAndEventsPluginMixin, AutocompleteMixin, CMSPluginBase):
    """
    How to use and abuse this plugin:
    
    first create an instance of the plugin model:
    
        instance = NewsAndEventsPlugin()
    
    set the attributes as required:
    
        instance.display = "events"
        instance.type = "for_place"
        instance.place = self
        instance.view = "current"
        instance.format = "details image"
        
    render it to get back the items you want in instance.lists, if you have the context:
    
        CMSNewsAndEventsPlugin().render(context, instance, None)

    alternatively (this is used in the menus, for example):
    
        plugin = CMSNewsAndEventsPlugin()   
        plugin.get_items(instance)
        plugin.add_links_to_other_items(instance)    
        ... and any operations tests as required
        
    and the NewsAndEventsPlugin() needs to have the lists attribute of CMSNewsAndEventsPlugin()

    """
    model = NewsAndEventsPlugin
    name = _("News & events")
    form = NewsAndEventsPluginForm
    auto_page_attribute = "auto_news_page"
    auto_page_slug = "news-and-events"
    auto_page_menu_title = "news_page_menu_title"
    fieldsets = (
        (None, {
        'fields': (('display', 'layout', 'list_format',),  ( 'format', 'order_by', 'group_dates',), 'limit_to')
    }),
        ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('entity', 'heading_level', ('news_heading_text', 'events_heading_text'), ('show_previous_events', ),)
    }),
    )

    # autocomplete fields
    related_search_fields = ['entity',]
    
    def icon_src(self, instance):
        return "/static/plugin_icons/news_and_events.png"

plugin_pool.register_plugin(CMSNewsAndEventsPlugin)