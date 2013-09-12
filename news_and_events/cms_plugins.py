from django import forms
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from arkestra_utilities.generic_models import ArkestraGenericPlugin
from arkestra_utilities.generic_models import ArkestraGenericPluginForm
from arkestra_utilities.admin_mixins import AutocompleteMixin

from contacts_and_people.templatetags.entity_tags import work_out_entity

from models import NewsAndEventsPlugin, NewsArticle, Event
from mixins import NewsAndEventsPluginMixin
from lister import NewsAndEventsPluginLister

from menu import menu_dict

class NewsAndEventsPluginForm(ArkestraGenericPluginForm, forms.ModelForm):
    class Meta:
        model = NewsAndEventsPlugin


class CMSNewsAndEventsPlugin(NewsAndEventsPluginMixin, ArkestraGenericPlugin, AutocompleteMixin, CMSPluginBase):

    text_enabled = True
    admin_preview = False
    # default render_template - change it in your ArkestraGenericPlugin if
    # required
    render_template = "arkestra/generic_lister.html"

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


    def render(self, context, instance, placeholder):
        self.entity = getattr(instance, "entity", None) or \
            work_out_entity(context, None)

        self.lister = NewsAndEventsPluginLister(
            entity=self.entity,
            display=instance.display,
            order_by=instance.order_by,
            layout=instance.layout,
            limit_to=instance.limit_to,
            item_format=instance.format,
            list_format=instance.list_format,
            # request=instance.request
            )

        context.update({
            'lister': self.lister,
            'placeholder': placeholder,
            })
        return context


plugin_pool.register_plugin(CMSNewsAndEventsPlugin)