from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.db.models import ForeignKey
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse

from widgetry.tabs.placeholderadmin import ModelAdminWithTabsAndCMSPlaceholder

from arkestra_utilities.widgets.wym_editor import WYMEditor
from arkestra_utilities import admin_tabs_extension
from arkestra_utilities.mixins import SupplyRequestMixin, AutocompleteMixin, InputURLMixin, fieldsets

from links.admin import ExternalLinkForm, get_or_create_external_link
from links.admin import ObjectLinkInline

from models import NewsArticle, NewsSource, Event, EventType

class NewsAndEventsForm(InputURLMixin):
    # a shared form for news and events
    class Meta:
        widgets = {'summary': forms.Textarea(
              attrs={'cols':80, 'rows':2,},
            ),  
        }
    
    def clean(self):
        # create the short_title automatically if necessary
        if not self.cleaned_data["short_title"] and self.cleaned_data.get("title"):
            if len(self.cleaned_data["title"]) > 70:
                raise forms.ValidationError("Please provide a short (less than 70 characters) version of the Title for the Short title field.")     
            else:
                self.cleaned_data["short_title"] = self.cleaned_data["title"]
                
        # check ExternalLink-related issues
        self.cleaned_data["external_url"] = get_or_create_external_link(self.request,
            self.cleaned_data.get("input_url", None), # a manually entered url
            self.cleaned_data.get("external_url", None), # a url chosen with autocomplete
            self.cleaned_data.get("title"), # link title
            self.cleaned_data.get("summary"), # link description
            )          

        # misc checks
        if not self.cleaned_data["external_url"]:
            if not self.cleaned_data["hosted_by"]:
                raise forms.ValidationError("A Host is required except for items on external websites - please provide either a Host or an External URL")      
            # must have body or url in order to be published
            if not self.instance and self.instance.body.cmsplugin_set.all():
            # if not self.cleaned_data["body"]:          
                message = "This will not be published until either an external URL or Plugin has been added. Perhaps you ought to do that now."
                messages.add_message(self.request, messages.WARNING, message)


class NewsAndEventsAdmin(AutocompleteMixin, ModelAdminWithTabsAndCMSPlaceholder, SupplyRequestMixin):
    exclude = ('content', 'url')
    search_fields = ['title',]
    list_display = ('short_title', 'date', 'hosted_by',)
    list_editable = ('hosted_by',)
    related_search_fields = ['hosted_by', 'external_url',]
    prepopulated_fields = {
        'slug': ('title',)
            }
        
    def _media(self):
        return super(AutocompleteMixin, self).media + super(ModelAdminWithTabsAndCMSPlaceholder, self).media
    media = property(_media)



class NewsArticleForm(NewsAndEventsForm):
    class Meta(NewsAndEventsForm.Meta):
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
    filter_horizontal = (
        'please_contact',
        'publish_to', 
        )
        
    fieldset_stickiness = ('How this item should behave in lists', {'fields': ('sticky_until', 'is_sticky_everywhere',)})
    tabs = (
            ('Basic', {'fieldsets': (fieldsets["basic"], fieldsets["host"])}),
            ('Date & significance', {'fieldsets': (fieldsets["date"], fieldsets["importance"], fieldset_stickiness)}),
            ('Body', {'fieldsets': (fieldsets["body"],)}),
            ('Where to Publish', {'fieldsets': (fieldsets["where_to_publish"],)}),
            ('Related people', {'fieldsets': (fieldsets["people"],)}),
            ('Links', {'inlines': (ObjectLinkInline,),}),
            ('Advanced Options', {'fieldsets': (fieldsets["url"], fieldsets["slug"],)}),        
        )

class EventForm(NewsAndEventsForm):
    class Meta(NewsAndEventsForm.Meta):
        model = Event

    def clean(self):
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
                    message = "You didn't say, but I am guessing that this is a single-day event on " + str(self.cleaned_data["start_date"]) + "."
                    messages.add_message(self.request, messages.INFO, message)
                else:
                    raise forms.ValidationError("I'm terribly sorry, I can't work out when this event is supposed to start. You'll have to enter that information yourself.")

        # 2. go and do the checks in the parent class
        super(EventForm, self).clean()
        
        # 3. check dates
        if self.cleaned_data["start_date"]:
            if self.cleaned_data["series"]:
                raise forms.ValidationError("An event with a start date can't also be a series of events. Please correct this.")      
            elif self.cleaned_data["end_date"] == self.cleaned_data["start_date"]:
                self.cleaned_data["single_day_event"] = True
            elif not self.cleaned_data["end_date"]:
                self.cleaned_data["single_day_event"] = True
                message = "You didn't enter an end date, so I have assumed this is a single-day event"
                messages.add_message(self.request, messages.INFO, message)
            elif not self.cleaned_data["single_day_event"]:
                if self.cleaned_data["end_date"] < self.cleaned_data["start_date"]:
                    raise forms.ValidationError('This event appears to end before it starts, which is very silly. Please correct the dates.')
                if not self.cleaned_data["start_time"] and self.cleaned_data["end_time"]:
                    self.cleaned_data["end_time"] = None
                    message = "You didn't enter a start time, so I deleted the end time. I hope that's OK."
                    messages.add_message(self.request, messages.WARNING, message)
            
            if self.cleaned_data["single_day_event"]:  
                self.cleaned_data["end_date"] = self.cleaned_data["start_date"]
                if not self.cleaned_data["start_time"]:
                    message = "You have a lovely smile."
                    messages.add_message(self.request, messages.INFO, message)
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
            message = "You didn't enter a start date, so I will assume this is a series of events."
            messages.add_message(self.request, messages.INFO, message)
            self.cleaned_data['start_date'] = self.cleaned_data['end_date'] = self.cleaned_data['start_time'] = self.cleaned_data['end_time'] = None
            self.cleaned_data['single_day_event'] = False
            self.cleaned_data['jumps_queue_on'] = None 
            self.cleaned_data['importance'] = 0
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
        'please_contact',
        'publish_to', 
        'registration_enquiries',
        'featuring', 
        )
    ordering = ['type',]
    change_list_template = "admin/news_and_events/event/change_list.html"
    list_display = ('short_title','parent',   'start_date', 'series', 'slug',)
    list_editable = ('parent',  'start_date',  'series', 'slug',)
    search_fields = ['title',]
    list_filter = ('start_date',)
    save_as = True
    # autocomplete fields
    related_search_fields = ['hosted_by','parent','building', 'external_url']

    # the tabs
    fieldset_when = ('When', {'fields': ('series', 'single_day_event', ('start_date', 'start_time'), ('end_date', 'end_time'))})
    fieldsets_relationships = (
        ('Parent & children', {
            'fields': ('parent', 'child_list_heading',),},),
        ('When displaying the children of this item in lists', {
            'fields': ('show_titles', 'display_series_summary',),},),
        )
    fieldset_registration = ('Registration enquiries', {'fields': ('registration_enquiries',)})   
    fieldset_featuring = ('Featured people', {'fields': ('featuring',)})   
    fieldset_jumpiness = ('How this item should behave in lists', {'fields': ('jumps_queue_on', 'jumps_queue_everywhere')})
    tabs = (
            ('Basic', {'fieldsets': (fieldsets["basic"], fieldsets["host"])}),
            ('Date & significance', {'fieldsets': (fieldset_when, fieldsets["importance"], fieldset_jumpiness)}),
            ('Parent & children', {'fieldsets': fieldsets_relationships}),
            ('Body', {'fieldsets': (fieldsets["body"],)}),
            ('Where to Publish', {'fieldsets': (fieldsets["where_to_publish"],)}),
            ('People', {'fieldsets': (fieldset_featuring, fieldsets["people"], fieldset_registration)}),
            ('Links', {'inlines': (ObjectLinkInline,),}),
            ('Advanced Options', {'fieldsets': (fieldsets["url"], fieldsets["slug"],)}),        
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
