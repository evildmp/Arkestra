#app = news_and_events
from news_and_events.models import NewsArticle, NewsSource, Event, EventType
from links.models import ExternalLink
from links.admin import ExternalLinkForm, validate_and_get_messages
from django.contrib import admin, messages
from django import forms
from datetime import datetime

# for the WYMeditor fields
from arkestra_utilities.widgets.wym_editor import WYMEditor

# for tabbed interface
from arkestra_utilities import admin_tabs_extension

# for autocomplete search
from widgetry import fk_lookup
from django.db.models import ForeignKey
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse

# for the generic object links
from links.admin import ObjectLinkInline

from cms.admin.placeholderadmin import PlaceholderAdmin

class NewsAndEventsForm(forms.ModelForm):
    # a shared form for news and events
    """
    subtitle = forms.CharField( # enabling this makes the help_text disappear
        widget=forms.Textarea(
          attrs={'cols':100, 'rows':2,},
        ),      
    )
    """    
    input_url = forms.CharField(max_length=255, required = False)
    
    def clean(self):
        NewsAndEventsForm.warnings = []
        NewsAndEventsForm.info = []
        # create the short_title automatically if necessary
        if not self.cleaned_data["short_title"] and self.cleaned_data.get("title"):
            if len(self.cleaned_data["title"]) > 70:
                raise forms.ValidationError("Please provide a short (less than 70 characters) version of the Title for the Short title field.")     
            else:
                self.cleaned_data["short_title"] = self.cleaned_data["title"]

        # if this item has an external url, we need to do all kinds of things with it    
        self.info, self.warnings, self.cleaned_data["external_url"]= validate_and_get_messages(
        self.cleaned_data.get("input_url", None), # a manually entered url
        self.cleaned_data.get("external_url", None), # a url chosen with autocomplete
        self.cleaned_data.get("title"), # link title
        self.cleaned_data.get("subtitle"), # link description
        self.info, 
        self.warnings,
        )          
        if not self.cleaned_data["hosted_by"] and not self.cleaned_data["external_url"]:
            raise forms.ValidationError("A Host is required except for items on external websites - please provide either a Host or an External URL")      
        #must have content or url in order to be published
        if not (self.cleaned_data["external_url"] or self.cleaned_data["content"] or self.cleaned_data["body"]):          
            self.warnings.append("This will not be published until either an external URL or Plugin has been added. Perhaps you ought to do that now.")

# Note for Stefan:

# the NewsAndEventsAdmin admin class should use admin_tabs_extension.ModelAdminWithTabs, but it seems to be incompatible with readonly_fields
# it will also need to inherit PlaceholderAdmin too

# The error is: 'Tab' object has no attribute 'readonly_fields'
# Traceback:
# File "/usr/local/lib/python2.6/dist-packages/django/core/handlers/base.py" in get_response
#   100.                     response = callback(request, *callback_args, **callback_kwargs)
# File "/usr/local/lib/python2.6/dist-packages/django/contrib/admin/options.py" in wrapper
#   239.                 return self.admin_site.admin_view(view)(*args, **kwargs)
# File "/usr/local/lib/python2.6/dist-packages/django/utils/decorators.py" in _wrapped_view
#   76.                     response = view_func(request, *args, **kwargs)
# File "/usr/local/lib/python2.6/dist-packages/django/views/decorators/cache.py" in _wrapped_view_func
#   69.         response = view_func(request, *args, **kwargs)
# File "/usr/local/lib/python2.6/dist-packages/django/contrib/admin/sites.py" in inner
#   190.             return view(request, *args, **kwargs)
# File "/usr/local/lib/python2.6/dist-packages/django/db/transaction.py" in _commit_on_success
#   299.                     res = func(*args, **kw)
# File "/var/www/html/modules/arkestra_utilities/admin_tabs_extension/tabs.py" in change_view
#   316.         media = self.media + adminForm.media
# File "/var/www/html/modules/arkestra_utilities/admin_tabs_extension/tabs.py" in _media
#   81.             media = media + tab.media
# File "/var/www/html/modules/arkestra_utilities/admin_tabs_extension/tabs.py" in _media
#   124.         return super(Tab, self)._media()
# File "/usr/local/lib/python2.6/dist-packages/django/contrib/admin/helpers.py" in _media
#   62.         for fs in self:
# File "/usr/local/lib/python2.6/dist-packages/django/contrib/admin/helpers.py" in __iter__
#   41.                 readonly_fields=self.readonly_fields,
# 
# Exception Type: AttributeError at /admin/news_and_events/newsarticle/307/
# Exception Value: 'Tab' object has no attribute 'readonly_fields'

# class NewsAndEventsAdmin(admin_tabs_extension.ModelAdminWithTabs, PlaceholderAdmin): # turned off because 'Tab' object has no attribute 'readonly_fields'
class NewsAndEventsAdmin(PlaceholderAdmin):
    class Meta:
        abstract = True
    inlines = (ObjectLinkInline,)
    exclude = ('content',)
    # for the change list pages
    search_fields = ['title',]
    list_display = ('short_title', 'date', 'hosted_by',)
    list_editable = ('hosted_by',)
    filter_horizontal = (
        # 'enquiries',
        'publish_to', 
        )
    prepopulated_fields = {
        'slug': ('title',)
            }
    # autocomplete fields
    related_search_fields = ['hosted_by', 'external_url',]
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(NewsAndEventsAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    def save_model(self, request, obj, form, change):
        print "respnse-change", self.form.info
        for message in self.form.warnings:
            messages.warning(request, message)
        for message in self.form.info:
            messages.info(request, message)
        return super(NewsAndEventsAdmin, self).save_model(request, obj, form, change)

    class Media:
        js = (
            '/media/cms/js/lib/jquery.js', # we already load jquery for the tabs
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra/js/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra/js/jquery/themes/base/ui.all.css',)
        }

class NewsArticleForm(NewsAndEventsForm):
    class Meta:
        model = NewsArticle
        
    def clean(self):
        super(NewsArticleForm, self).clean()
        
        if self.cleaned_data["external_news_source"] and not self.cleaned_data["url"]:
            raise forms.ValidationError("You can't claim that this is for an external news source unless you include a URL.")     

        # sticky_until value must be greater than (later) than date
        date = datetime.date(self.cleaned_data['date'])
        self.cleaned_data['sticky_until'] = self.cleaned_data.get('sticky_until', date) 
        # if importance = 0, it's not sticky

        self.cleaned_data['sticky_until'] = self.cleaned_data['sticky_until'] or datetime.date(self.cleaned_data['date'])
        if self.cleaned_data['importance'] == 0:
            self.cleaned_data['sticky_until'] = None 
        elif self.cleaned_data['sticky_until'] < datetime.date(self.cleaned_data['date']):
            self.cleaned_data['sticky_until'] = datetime.date(self.cleaned_data['date'])
        return self.cleaned_data

class NewsArticleAdmin(NewsAndEventsAdmin):
    # some general settings
    form = NewsArticleForm
    list_filter = ('date',)
    read_only_fields = ('sticky_until')
    # the tabs

    # fieldsets = (
    #     (None, 
    #         {
    #             'fields': ('body',),
    #             'classes': ('plugin-holder', 'plugin-holder-nopage'),
    #             },
    #         ),
    #     )
        
    fieldset_basic = (
        ('Basic', {
            'fields': (('title', 'image',), 'short_title', 'subtitle','hosted_by',),
        }),)
    fieldset_placeholder = (
        ('Placeholder', {
            'fields': ('body',),
          'classes': ('plugin-holder', 'plugin-holder-nopage'),
        }),)
    fieldset_date = (
        ('Date & significance', {
            'fields': ('date', 'importance', ('sticky_until', 'is_sticky_everywhere',), ),
        }),)
    fieldset_where_to_publish = (    
        ('Where to publish', {
            'fields': ('publish_to',),
        }),)
    fieldset_people = (
        ('People', {
            'fields': ('enquiries',),
        }),)
    fieldset_advanced = (
        ('Advanced Options', {
            'fields': ('external_news_source', 'slug',),
        }),)
    tabs = (
        ('Basic', {'fieldsets': fieldset_basic,}),
        ('Date & significance', {'fieldsets': fieldset_date,}),
        ('Where to Publish', {'fieldsets': fieldset_where_to_publish,}),
        ('People', {'fieldsets': fieldset_people,}),
        ('Links', {'inlines': ('ObjectLinkInline',),}),
        ('Advanced Options', {'fieldsets': fieldset_advanced,}),        
        )
    prepopulated_fields = {
        'slug': ('title',)
            }

class EventForm(NewsAndEventsForm):
    class Meta:
        model = Event
    def clean(self):
        super(EventForm, self).clean()
        # 1. obtain missing information from parent
        parent = self.cleaned_data['parent']
        if parent:
            print "admin.clean thinks this has a parent:", parent
            # the many-to-many fields can be inherited
            m2m_fields = ['publish_to',  ] #organisers ,'enquiries', 'registration_enquiries',
            for field_name in m2m_fields:
                print "checking parent field_content"
                self.cleaned_data[field_name] = self.cleaned_data[field_name] or list(getattr(parent,field_name).all())
            # other fields
            attribute_list = ['building', 'precise_location', 'hosted_by', 'access_note'] 
            for field_name in attribute_list:
                print "checking which attributes to inherit:", field_name
                self.cleaned_data[field_name] = self.cleaned_data[field_name] or getattr(parent,field_name)
            # if parent is single day event, and this one has no date set, inherit the parent's
            if not self.cleaned_data["start_date"]:
                if parent.single_day_event:
                    self.cleaned_data["start_date"] = self.cleaned_data["end_date"] = parent.start_date
                    self.cleaned_data["single_day_event"] = True
                    self.info.append("You didn't say, but I am guessing that this is a single-day event on " + str(self.cleaned_data["start_date"]) + ".")
                else:
                    raise forms.ValidationError("I'm terribly sorry, I can't work out when this event is supposed to start. You'll have to enter that information yourself.")
        
        # 3. check dates
        if self.cleaned_data["start_date"]:
            if self.cleaned_data["series"]:
                raise forms.ValidationError("An event with a start date can't also be a series of events. Please correct this.")      
            elif self.cleaned_data["end_date"] == self.cleaned_data["start_date"]:
                self.cleaned_data["single_day_event"] = True
            elif not self.cleaned_data["end_date"]:
                self.cleaned_data["single_day_event"] = True
                self.info.append("You didn't enter an end date, so I have assumed this is a single-day event")        
            elif not self.cleaned_data["single_day_event"]:
                if self.cleaned_data["end_date"] < self.cleaned_data["start_date"]:
                    raise forms.ValidationError('This event appears to end before it starts, which is very silly. Please correct the dates.')
                if not self.cleaned_data["start_time"] and self.cleaned_data["end_time"]:
                    self.cleaned_data["end_time"] = None
                    self.warning.append("You didn't enter a start time, so I deleted the end time. I hope that's OK.")
            
            if self.cleaned_data["single_day_event"]:  
                self.cleaned_data["end_date"] = self.cleaned_data["start_date"]
                if not self.cleaned_data["start_time"]:
                    self.info.append("You have a lovely smile.")
                    self.cleaned_data["end_time"] = None
                elif self.cleaned_data["end_time"] and self.cleaned_data["end_time"] < self.cleaned_data["start_time"]:
                    raise forms.ValidationError('This event appears to end before it starts, which is very silly. Please correct the times.')
                                  
            self.cleaned_data['jumps_queue_on'] = self.cleaned_data['jumps_queue_on'] or self.cleaned_data['start_date']
            if self.cleaned_data['importance'] == 0:
                self.cleaned_data['jumps_queue_on'] = None 
            elif self.cleaned_data['jumps_queue_on'] > self.cleaned_data['start_date']:
                self.cleaned_data['jumps_queue_on'] = self.cleaned_data['start_date']

        # an event without a start date can be assumed to be a series of events
        else:
            self.cleaned_data["series"] = True
            self.info.append("You didn't enter a start date, so I will assume this is a series of events")
            self.cleaned_data['start_date'] = self.cleaned_data['end_date'] = self.cleaned_data['start_time'] = self.cleaned_data['end_time'] = None
            self.cleaned_data['single_day_event'] = False
            self.cleaned_data['jumps_queue_on'] = None 
            self.cleaned_data['importance'] = 0
        print "info", self.info
        return self.cleaned_data

    '''
    def clean_enquiries(self):
        data = self.cleaned_data['enquiries']
        parent = self.cleaned_data['parent']
        print "cleaning enquiries: %s (%s) parent: %s (%s)" % (data,type(data), parent, type(parent))
        if not data and parent:
            print "  getting defaultdata from parent"
            data = list(parent.enquiries.all())
        return data
    '''

class EventAdmin(NewsAndEventsAdmin):
    # some general settings
    form = EventForm
    filter_horizontal = (
        # 'enquiries',
        'publish_to', 
        # 'registration_enquiries',
        #'organisers', 
        'featuring', 
        )
    change_list_template = "admin/news_and_events/event/change_list.html"
    list_display = ('short_title','parent',  'inherit_name',  'start_date', 'series', 'slug',)
    list_editable = ('parent', 'inherit_name',  'start_date',  'series', 'slug',)
    search_fields = ['title',]
    list_filter = ('start_date',)
    save_as = True
    # autocomplete fields
    related_search_fields = ['hosted_by','parent','building',]
    # the tabs
    fieldset_basic = (
        ('', {
            'fields': ('type', ('title',  'short_title',),  'image', 'subtitle', 'hosted_by', ),
        }),
    )
    fieldset_where_to_publish = (    
        ('', {
            'fields': ('publish_to',)
        }),)
    fieldset_where_and_when = (    
        ('Where', {
            'fields': (('building', 'precise_location',), 'access_note'),
        }),
        ('When', {
            'fields': ('series', 'single_day_event', ('start_date', 'start_time',), ('end_date', 'end_time',),),
        }),
         ('Significance', {
            'fields': (('jumps_queue_on', 'importance',), ('jumps_queue_everywhere',),),
        }),
       
        )
    fieldset_relationships = (
        ('Relationships with other Events', {
            'fields': ('always_display_series', 'parent', 'child_list_heading', 'do_not_advertise_children', 'no_direct_access_to_children',), 
        }),)        
    fieldset_people = (    
        ('People', {
            'fields': (
            'featuring', #'enquiries', 'registration_enquiries', #'organisers', 
            ),
        }),)    
    fieldset_advanced = (    
        ('', {
            'fields': ('url', 'slug',),
        }),)
    tabs = (
        ('Basic', {'fieldsets': fieldset_basic,}),
        ('Where to publish', {'fieldsets': fieldset_where_to_publish,}),
        ('Where & when', {'fieldsets': fieldset_where_and_when,}),
        ('Relationships', {'fieldsets': fieldset_relationships,}),
        ('People', {'fieldsets': fieldset_people,}),
        ('Links', {'inlines': ('ObjectLinkInline',),}),
        ('Advanced Options', {'fieldsets': fieldset_advanced,}),
        )
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
                'root_events': Event.objects.filter(level=0),
                'has_add_permission': request.user.has_perm('news_and_events.add_event'),
                'has_change_permission': request.user.has_perm('news_and_events.change_event'),
                'has_delete_permission': request.user.has_perm('news_and_events.delete_event'),
        })
        return super(EventAdmin, self).changelist_view(request, extra_context)
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(EventAdmin, self).get_urls()
        # helper for url pattern generation
        info = "%sadmin_%s_%s" % (self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name)
        #pat = lambda regex, fn: url(regex, self.admin_site.admin_view(fn), name='%s_%s' % (info, fn.__name__))
        url_patterns = patterns('',
            url(r'^([0-9]+)/move-page/$', self.admin_site.admin_view(self.move_event), name='%s_%s' % (info, 'move_page') ),
            #pat(r'^([0-9]+)/move-page/$', self.move_entity),
        )
        url_patterns.extend(urls)
        return url_patterns
    def move_event(self, request, event_id, extra_context=None):
        target = request.POST.get('target', None)
        position = request.POST.get('position', None)
        if target is None or position is None:
            return HttpResponseRedirect('../../')            
        try:
            event = self.model.objects.get(pk=event_id)
            target = self.model.objects.get(pk=target)
        except self.model.DoesNotExist:
            return HttpResponse("error")
        # does he haves permissions to do this...?
        if not request.user.has_perm('news_and_events.change_event'):
            return HttpResponse("Denied")
        # move page
        event.move_to(target, position)
        event.save()
        return HttpResponse("ok")

class EventTypeAdmin(admin.ModelAdmin):
    pass

class NewsSourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Event,EventAdmin)
admin.site.register(NewsSource,NewsSourceAdmin)
admin.site.register(EventType,EventTypeAdmin)
admin.site.register(NewsArticle,NewsArticleAdmin)
#admin.site.register(NewsArticle,PlaceholderAdmin)