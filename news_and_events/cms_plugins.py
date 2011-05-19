from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import NewsAndEventsPlugin, NewsArticle, Event
from django.utils.translation import ugettext as _
from django import forms
from itertools import chain
from contacts_and_people.templatetags.entity_tags import work_out_entity
from functions import get_news_and_events

# for autocomplete search
from widgetry import fk_lookup
from django.db.models import ForeignKey
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse

# for tabbed interface
from arkestra_utilities import admin_tabs_extension

class NewsAndEventsPluginForm(forms.ModelForm):
    class Meta:
        model = NewsAndEventsPlugin
    def clean(self):
        if "featured" in self.cleaned_data["format"]:
            self.cleaned_data["order_by"] = "importance/date"
        if self.cleaned_data["format"] == "featured horizontal":
            self.cleaned_data["layout"] = "stacked"
            if self.cleaned_data["limit_to"] >3:
                self.cleaned_data["limit_to"] = 3
            if self.cleaned_data["limit_to"] < 2:
                self.cleaned_data["limit_to"] = 2
        if self.cleaned_data["limit_to"] == 0: # that's a silly number, and interferes with the way we calculate later
            self.cleaned_data["limit_to"] = None
        return self.cleaned_data

class CMSNewsAndEventsPlugin(CMSPluginBase):
    model = NewsAndEventsPlugin
    name = _("News & events")
    text_enabled = True
    form = NewsAndEventsPluginForm
    render_template = "news_and_event_lists.html"
    admin_preview = False
    
    fieldsets = (
        (None, {
        'fields': (('display', 'layout',),  ( 'format', 'order_by',), 'limit_to')
    }),
        ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('entity', 'heading_level', ('news_heading_text', 'events_heading_text'), ('show_previous_events', ),)
    }),
    )

    
    """
    fieldset_basic = (
        (None, {
        'fields': (('display', 'layout',),  ( 'format', 'order_by',), 'limit_to')
    }),)
    fieldset_advanced = (
        ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('entity', 'heading_level', ('news_heading_text', 'events_heading_text'), ('show_previous_events', ),)
    }),
    )

    tabs = (
        ('Basic', {'fieldsets': fieldset_basic,}),
        ('Advanced Options', {'fieldsets': fieldset_advanced,}),        
        )
    """

    # autocomplete fields
    related_search_fields = ['entity',]
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(CMSNewsAndEventsPlugin, self).formfield_for_dbfield(db_field, **kwargs)
    class Media:
        js = (
            '/media/cms/js/lib/jquery.js', # we already load jquery for the tabs
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra/static/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/static/jquery/themes/base/ui.all.css',)
        }

    def render(self, context, instance, placeholder):
        #print self.render_template
        print "-- in render of CMSNewsAndEventsPlugin --"
        instance.entity = getattr(instance, "entity", None) or work_out_entity(context, None)
        instance.type = getattr(instance, "type", "plugin")
        instance.show_images = getattr(instance, "show_images", True)
        print "instance.show_images", instance.show_images
        try:
            render_template = instance.render_template
        except AttributeError:
            pass
        get_news_and_events(instance)
        context.update({ 
            'news_and_events': instance,
            'placeholder': placeholder,
            })
        print "returning context"
        return context

    def icon_src(self, instance):
        return "/static/plugin_icons/news_and_events.png"
            
plugin_pool.register_plugin(CMSNewsAndEventsPlugin)