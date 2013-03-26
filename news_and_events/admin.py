from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.db.models import ForeignKey
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext_lazy as _

from widgetry.tabs.placeholderadmin import ModelAdminWithTabsAndCMSPlaceholder

from treeadmin.admin import TreeAdmin

from arkestra_utilities.admin_mixins import GenericModelAdmin, GenericModelForm, HostedByFilter, fieldsets

from links.admin import ExternalLinkForm, ObjectLinkInline

from models import NewsArticle, NewsSource, Event, EventType

class NewsAndEventsForm(GenericModelForm):
    # a shared form for news and events
    pass
    
from contacts_and_people.models import Entity

class NewsAndEventsAdmin(GenericModelAdmin):
    exclude = ('content', 'url')
    search_fields = ['title',]
    list_display = ('short_title', 'date', 'hosted_by',)
    list_editable = ('hosted_by',)
    related_search_fields = ['hosted_by', 'external_url',]
    prepopulated_fields = {
        'slug': ('title',)
            }
    list_max_show_all = 400
    list_per_page = 400
        
    def _media(self):
        return super(ModelAdminWithTabsAndCMSPlaceholder, self).media
    media = property(_media)

# this or something like it can be enabled when the 
# autocomplete-stop-sworking-after-adding-an-inlin
# bug has been addressed
# it will hugely speed up loading of news, events etc with lots of people in the m2m

# class NewsPersonInline(AutocompleteMixin, admin.TabularInline):
#     model = NewsArticle.please_contact.through
#     related_search_fields = ["person", ]
#     extra = 1
#     def _media(self):
#         return super(AutocompleteMixin, self).media
#     media = property(_media)
    
class NewsArticleForm(NewsAndEventsForm):
    class Meta(NewsAndEventsForm.Meta):
        model = NewsArticle
        
    def clean(self):
        super(NewsArticleForm, self).clean()
        
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
    list_filter = ('date', HostedByFilter)
    read_only_fields = ('sticky_until')
    filter_horizontal = (
        'please_contact',
        'publish_to', 
        )
    # inlines = [MembershipInline,]    
    fieldset_stickiness = ('How this item should behave in lists', {'fields': ('sticky_until', 'is_sticky_everywhere',)})
    tabs = (
            ('Basic', {'fieldsets': (fieldsets["basic"], fieldsets["host"], fieldsets["image"], fieldsets["publishing_control"],),}),
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
                    message = u"You didn't say, but I am guessing that this is a single-day event on " + unicode(self.cleaned_data["start_date"]) + u"."
                    messages.add_message(self.request, messages.INFO, message)
                else:
                    raise forms.ValidationError(u"I'm terribly sorry, I can't work out when this event is supposed to start. You'll have to enter that information yourself.")

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
                message = u"You didn't enter an end date, so I have assumed this is a single-day event"
                messages.add_message(self.request, messages.INFO, message)
            elif not self.cleaned_data["single_day_event"]:
                if self.cleaned_data["end_date"] < self.cleaned_data["start_date"]:
                    raise forms.ValidationError('This event appears to end before it starts, which is very silly. Please correct the dates.')
                if not self.cleaned_data["start_time"] and self.cleaned_data["end_time"]:
                    self.cleaned_data["end_time"] = None
                    message = u"You didn't enter a start time, so I deleted the end time. I hope that's OK."
                    messages.add_message(self.request, messages.WARNING, message)
            
            if self.cleaned_data["single_day_event"]:  
                self.cleaned_data["end_date"] = self.cleaned_data["start_date"]
                if not self.cleaned_data["start_time"]:
                    message = u"You have a lovely smile."
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
            message = u"You didn't enter a start date, so I will assume this is a series of events."
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

class EventIsSeries(SimpleListFilter):
    title = _('actual/series')
    parameter_name = 'series'

    def lookups(self, request, model_admin):
        return (
            ('actual', _('Actual')),
            ('series', _('Series')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'actual':
            return queryset.filter(series=False)
        if self.value() == 'series':
            return queryset.filter(series=True)


class EventAdmin(NewsAndEventsAdmin, TreeAdmin):
    
    # some general settings
    form = EventForm
    filter_horizontal = (
        'please_contact',
        'publish_to', 
        'registration_enquiries',
        'featuring', 
        )
    ordering = ['type',]
    list_display = ('short_title', 'hosted_by', 'start_date')
    list_editable = ()
    search_fields = ['title']
    list_filter = (EventIsSeries, 'start_date', HostedByFilter)
    save_as = True
    # autocomplete fields
    related_search_fields = ['hosted_by','parent','building', 'external_url']


    # the tabs
    fieldset_type = ('Type', {'fields': ('type',)},)
    fieldset_building = ('Building', {'fields': ('building',)},)
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
            ('Basic', {'fieldsets': (fieldsets["basic"], fieldset_type, fieldsets["host"], fieldsets["image"], fieldsets["publishing_control"],)}),
            ('Date & significance', {'fieldsets': 
                ( 
                    fieldset_when, 
                    fieldsets["importance"], 
                    fieldset_jumpiness,)}
                    ),
            ('Location', {'fieldsets': (fieldset_building, fieldsets["location"],)}),
            ('Parent & children', {'fieldsets': fieldsets_relationships}),
            ('Body', {'fieldsets': (fieldsets["body"],)}),
            ('Where to Publish', {'fieldsets': (fieldsets["where_to_publish"],)}),
            ('People', {'fieldsets': (fieldset_featuring, fieldsets["people"], fieldset_registration)}),
            ('Links', {'inlines': (ObjectLinkInline,),}),
            ('Advanced Options', {'fieldsets': (fieldsets["url"], fieldsets["slug"],)}),        
        )


class EventTypeAdmin(admin.ModelAdmin):
    pass

class NewsSourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Event,EventAdmin)
admin.site.register(NewsSource,NewsSourceAdmin)
admin.site.register(EventType,EventTypeAdmin)
admin.site.register(NewsArticle,NewsArticleAdmin)
