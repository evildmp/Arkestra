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
    
    def render(self, context, instance, placeholder):
        self.set_defaults(instance)

        instance.entity = getattr(instance, "entity", None) or work_out_entity(context, None)
        instance.type = getattr(instance, "type", "plugin")
        render_template = getattr(instance, "render_template", "")
        self.get_items(instance)
        self.add_link_to_main_page(instance)
        self.add_links_to_other_items(instance)
        # for item in self.lists:
        #     print "##", item["heading_text"], len(item["other_items"])
        self.set_limits_and_indexes(instance)
        self.determine_layout_settings(instance)
        self.set_layout_classes(instance)
        instance.lists = self.lists
        context.update({ 
            'everything': instance,
            'placeholder': placeholder,
            })
        return context

    def icon_src(self, instance):
        return "/static/plugin_icons/news_and_events.png"

plugin_pool.register_plugin(CMSNewsAndEventsPlugin)