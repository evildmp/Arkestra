from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import NewsAndEventsPlugin, NewsArticle, Event
from django.utils.translation import ugettext as _
from django import forms
from arkestra_utilities.universal_plugin_lists import UniversalPlugin

from contacts_and_people.templatetags.entity_tags import work_out_entity
from functions import get_news_and_events

# for tabbed interface
from arkestra_utilities.admin import AutocompleteMixin


class NewsAndEventsPluginForm(forms.ModelForm):
    class Meta:
        model = NewsAndEventsPlugin
    
    def clean(self):
        if "horizontal" in self.cleaned_data["list_format"]:
            self.cleaned_data["order_by"] = "importance/date"
            self.cleaned_data["format"] = "details image"
            self.cleaned_data["layout"] = "stacked"
            self.cleaned_data["group_dates"] = False
            if self.cleaned_data["limit_to"] >3:
                self.cleaned_data["limit_to"] = 3
            if self.cleaned_data["limit_to"] < 2:
                self.cleaned_data["limit_to"] = 2
        if self.cleaned_data["limit_to"] == 0: # that's a silly number, and interferes with the way we calculate later
            self.cleaned_data["limit_to"] = None
        return self.cleaned_data


class CMSNewsAndEventsPlugin(UniversalPlugin, AutocompleteMixin, CMSPluginBase):
    model = NewsAndEventsPlugin
    name = _("News & events")
    text_enabled = True
    form = NewsAndEventsPluginForm
    render_template = "arkestra/universal_plugin_lister.html"
    admin_preview = False
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

        if "news" in instance.display:
            this_list = {"model": NewsArticle,}
            this_list["items"] = NewsArticle.objects.get_items(instance)
            this_list["links_to_other_items"] = self.news_style_other_links
            this_list["heading_text"] = instance.news_heading_text
            self.lists.append(this_list)

        if "events" in instance.display:
            this_list = {"model": Event,}
            this_list["items"] = Event.objects.get_items(instance)
            this_list["links_to_other_items"] = self.events_style_other_links
            this_list["heading_text"] = instance.events_heading_text
            self.lists.append(this_list)

        self.add_link_to_main_page(instance)
        self.add_links_to_other_items(instance)
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
