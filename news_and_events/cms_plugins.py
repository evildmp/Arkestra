from django import forms
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from arkestra_utilities.generic_models import ArkestraGenericPlugin
from arkestra_utilities.generic_models import ArkestraGenericPluginForm
from arkestra_utilities.mixins import AutocompleteMixin

from contacts_and_people.templatetags.entity_tags import work_out_entity

from models import NewsAndEventsPlugin, NewsArticle, Event
from mixins import NewsAndEventsPluginMixin

from menu import menu_dict

class NewsAndEventsPluginForm(ArkestraGenericPluginForm, forms.ModelForm):
    class Meta:
        model = NewsAndEventsPlugin


class CMSNewsAndEventsPlugin(ArkestraGenericPlugin, NewsAndEventsPluginMixin, AutocompleteMixin, CMSPluginBase):
    model = NewsAndEventsPlugin
    name = _("News & events")
    form = NewsAndEventsPluginForm
    menu_cues = menu_dict
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