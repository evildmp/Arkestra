from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import NewsAndEventsPlugin, NewsArticle, Event
from django.utils.translation import ugettext as _
from django import forms

from itertools import chain
from contacts_and_people.templatetags.entity_tags import work_out_entity
from functions import get_news_and_events

# for tabbed interface
from arkestra_utilities import admin_tabs_extension
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

class CMSNewsAndEventsPlugin(AutocompleteMixin, CMSPluginBase):
    model = NewsAndEventsPlugin
    name = _("News & events")
    text_enabled = True
    form = NewsAndEventsPluginForm
    render_template = "arkestra/universal_plugin_lister.html"
    admin_preview = False
    
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
        #print self.render_template
        print "======================= in render of CMSNewsAndEventsPlugin =================="
        instance.entity = getattr(instance, "entity", None) or work_out_entity(context, None)
        instance.type = getattr(instance, "type", "plugin")
        try:
            render_template = instance.render_template
        except AttributeError:
            pass
        get_news_and_events(instance)
        context.update({ 
            'everything': instance,
            'placeholder': placeholder,
            })
        print "returning context"
        return context

    def icon_src(self, instance):
        return "/static/plugin_icons/news_and_events.png"

plugin_pool.register_plugin(CMSNewsAndEventsPlugin)
