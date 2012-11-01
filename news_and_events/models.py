from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from datetime import date as pythondate

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.template.defaultfilters import date, time, slugify

import mptt

from cms.models import CMSPlugin
from cms.models.fields import PlaceholderField

from filer.fields.image import FilerImageField

from contacts_and_people.models import Entity, Person, Building

from links.models import ExternalLink

from arkestra_utilities.output_libraries.dates import nice_date
from arkestra_utilities.generic_models import ArkestraGenericPluginOptions, ArkestraGenericModel
from arkestra_utilities.mixins import URLModelMixin, LocationModelMixin
from arkestra_utilities.managers import ArkestraGenericModelManager
from arkestra_utilities.settings import PLUGIN_HEADING_LEVELS, PLUGIN_HEADING_LEVEL_DEFAULT, COLLECT_TOP_ALL_FORTHCOMING_EVENTS, DATE_FORMAT, AGE_AT_WHICH_ITEMS_EXPIRE

from managers import EventManager

class NewsAndEvents(ArkestraGenericModel, URLModelMixin):

    content = models.TextField(null=True, blank=True, 
        help_text="Not used or required for external items")
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(NewsAndEvents, self).save(*args, **kwargs)

    def link_to_more(self):
        if self.get_hosted_by:
            return self.get_hosted_by.get_related_info_page_url("news-and-events")        

class NewsArticle(NewsAndEvents):
    url_path = "news"
    objects = ArkestraGenericModelManager()
    
    date = models.DateTimeField(default=datetime.now,
        help_text=u"Dateline for the item (the item will not be published until then" ,  )
    display_indefinitely = models.BooleanField(
        help_text=u"Important news; it won't expire from news lists" , )    
    external_news_source = models.ForeignKey('NewsSource', null=True, blank=True, 
        help_text=u"If this news item is from an external source")
    sticky_until = models.DateField(u"Featured until", 
        null=True, blank=True, default=pythondate.today,
        help_text=u"Will remain a featured item until this date")
    is_sticky_everywhere = models.BooleanField(u"Featured everywhere",
        default=False, help_text=u"Will be featured in other entities's news lists") 
    
    class Meta:
        ordering = ['-date']
                
    @property
    def has_expired(self):
       # the item is too old to appear in current lists, and should only be listed in archives
       age = datetime.now() - self.date
       if AGE_AT_WHICH_ITEMS_EXPIRE and age.days > AGE_AT_WHICH_ITEMS_EXPIRE:
           return True

    @property
    def get_when(self):
        """
        get_when provides a human-readable attribute under which items can be grouped.
        Usually, this is an easily-readble rendering of the date (e.g. "April 2010") but it can also be "Top news", for items to be given special prominence.
        """
        if getattr(self, "sticky", None):
            return "Top news"        
        get_when = nice_date(self.date, DATE_FORMAT["date_groups"])
        return get_when


class Event(NewsAndEvents, LocationModelMixin):
    url_path = "event"
    objects = EventManager()

    type = models.ForeignKey('EventType')
    featuring = models.ManyToManyField(Person, related_name='%(class)s_featuring',
        null=True, blank=True,
        help_text="The speakers, lecturers, instructors or other people featured in this event")
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    SERIES = (
        (False, u"an actual event"),
        (True, u"a series of events"),
    )
    series = models.BooleanField("This is", default=False, choices=SERIES)
    SHOW_TITLES = (
        ("series children", u"show title of series followed by title of children"),
        ("series", u"show title of series only"),
        ("children", u"show title of children only"),
    )
    show_titles = models.CharField(u"Titles",
        max_length = 25,
        default="children",
        choices=SHOW_TITLES,
        )
    DISPLAY_SERIES_SUMMARY = (
        (False, u"display children's summaries"),
        (True, u"display the summary for the series"),
    ) 
    display_series_summary = models.BooleanField(u"Summaries",
        default=False,
        choices=DISPLAY_SERIES_SUMMARY,
        )
    child_list_heading = models.CharField(max_length=50, null=True, blank=True, 
        help_text= u"e.g. Conference sessions; Lectures in this series")
    start_date = models.DateField(null=True, blank=True,
        help_text=u"Not required for a series of events")    
    start_time = models.TimeField(null=True, blank=True)    
    end_date = models.DateField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    single_day_event = models.BooleanField(default=False)
    building = models.ForeignKey(Building, null=True, blank=True)
    # this won't appear in the admin
    jumps_queue_on = models.DateField(null=True, blank=True,
        help_text=u"Will become a featured item on this date") 
    jumps_queue_everywhere = models.BooleanField(default=False)
    registration_enquiries = models.ManyToManyField(Person, 
        related_name = '%(class)s_registration', 
        null = True, blank = True,
        help_text=u"The people who responsible for registration, if different from those in <em>Please contact</em>"
        ) 
    
    class Meta:
        ordering = ['type', 'start_date', 'start_time']
    
    @property
    def informative_url(self):
        """ 
        An event has an 'informative_url' if it itself is uninformative, but it is a child of a series
        """
        # print 
        # print "========================================"
        # print "checking", self
        # print "is_uninformative", self.is_uninformative
        # print "self.parent", self.parent
        # 
        if self.is_uninformative and self.parent and self.parent.series:
            # print self, "parent!"
            return self.parent.get_absolute_url()
        else:
            # print self, "self!"
            return self.get_absolute_url()
  
    @property
    def show_parent_series(self):
        """
        checks whether we should show the parent series too in lists
        """
        if self.parent and self.parent.series:
            return self.parent.show_titles

    @property
    def is_uninformative(self):
        # print 
        # print "============================"
        # print self.body
        # if self.body:
        #     print 1, self.body.cmsplugin_set.all()
        #     print 2, self.external_url
        #     print 3, self.please_contact.all()
        #     print 4, self.registration_enquiries.all()
        # print "----------------------------"
        if self.body and self.body.cmsplugin_set.all() or self.external_url or self.please_contact.all() or self.registration_enquiries.all(): # or self.links_set.all():
            # print "uninformative"
            return False
        else:
            # print "informative"
            return True
        
    def save(self):
        def slug_is_bad(self):
            if self.slug in [slug.values()[0] for slug in Event.objects.exclude(id=self.id).values("slug")]:
                return True

        if self.slug == "" or slug_is_bad(self):
            self.slug=slugify(self.short_title)
        if slug_is_bad(self):
            suffix = slugify(date(self.start_date, "Y"))
            if not suffix in self.slug:
                self.slug = self.slug + "-" + suffix
                # print "adding suffix:", suffix, self.slug
        if slug_is_bad(self):
            suffix = slugify(date(self.start_date, "F"))
            if not suffix in self.slug:
                self.slug = self.slug + "-" + suffix
                # print "adding suffix:", suffix, self.slug
        if slug_is_bad(self):
            suffix = slugify(date(self.start_date, "d"))
            if not suffix in self.slug:
                self.slug = self.slug + "-" + suffix
                # print "adding suffix:", suffix, self.slug
        while slug_is_bad(self):
            self.slug=self.slug + "-x"
            # print "adding suffix:", "-x"
        super(Event, self).save()
        
    def get_children_forthcoming(self):
        if self.series:
            return self.children.filter(Q(start_date__gte = datetime.now()) | Q(end_date__gte = datetime.now()) | Q(series = True)).order_by('start_date')
        else:
            return self.children.all()
        
    def get_children_previous(self):
        if self.series:
            return self.children.filter(Q(start_date__lt = datetime.now()) | Q(end_date__lt = datetime.now()) | Q(series = True)).order_by('-start_date')
    
    def get_featuring(self, featuring = None):
        featuring = set(self.featuring.all()) or set()
        if not self.series:
            for child_event in self.children.all():
                featuring.update(child_event.get_featuring(featuring))
        return featuring
    
    @property
    def date(self):
        return self.start_date
    
    def get_date_if_needed_and_time_heading(self):
        date_time_heading = []
        if not self.series:
            if not self.parent.single_day_event:
                date_time_heading.append("date")
            if self.get_times():
                date_time_heading.append("time")
        return date_time_heading
    
    def get_date_if_needed_and_time(self):
        date_and_time = []
        date = self.get_dates()
        time = self.get_times()
        if self.parent.single_day_event and not time:
            date_and_time.append(date)
        if time:
            date_and_time.append(time)        
        return date_and_time
        
    def get_dates(self):
        if not self.series:
            start_date = self.start_date
            end_date = self.end_date
            if not end_date or self.single_day_event:
                end_date = start_date
            start_date_format = end_date_format = DATE_FORMAT["not_this_year"]
            now = datetime.now()
            if start_date.year == end_date.year:            # start and end in the same year, so:
                start_date_format = DATE_FORMAT["not_this_month"]                  # start format example: "3rd May"
                if start_date.month == end_date.month:      # start and end in the same month, so:
                    start_date_format = DATE_FORMAT["this_month"]                # start format example: "21st" 
                if end_date.year == now.year:               # they're both this year, so:
                    end_date_format = DATE_FORMAT["not_this_month"]                # end format example: "23rd May"
            if self.single_day_event:
                dates = nice_date(start_date, end_date_format)
            else:
                dates = nice_date(start_date, start_date_format) + unicode(_(u" to ")) + nice_date(end_date, end_date_format)
            return dates
        else:
            return "Series"
        
    def get_times(self):
        start_time = self.start_time
        if self.single_day_event and start_time:
            end_time = self.end_time
            if end_time:
                times = time(start_time) + "&#8209;" + time(end_time)
            else:
                times = time(start_time)
            return times
        
    def get_image(self):
        return self.image or (self.parent.get_image() if self.parent else None)

    def check_date(self): # we need somehow to send a message to the user about this
        if not self.children.all():
            return
        else:
            for child in self.children.all():
                need_to_save = False
                child.check_date()
                if child.start_date and not self.series:
                    child.check_date() # we start at the leaves and work backwards, so we can assume all descendants are OK
                    if (not self.start_date) or (self.start_date > child.start_date):
                        self.start_date = child.start_date
                        need_to_save = True
                    if not self.end_date:
                        self.end_date = self.start_date
                    child_end_date = child.end_date
                    if not child_end_date:
                        child_end_date = child.start_date
                    if  self.end_date < child_end_date:
                        self.end_date = child_end_date
                        need_to_save = True
                    if need_to_save:
                        self.single_day_event = False
                        self.save()
        return        
    
    def apply_parent_attributes(self): # is this required?
        print "we're in event.apply_parent_attributes - the question is why"
        if self.parent:
            self.enquiries = set(self.parent.enquiries.all())
            self.save()
        return

    @property
    def calculated_summary(self):
        if self.parent and self.parent.display_series_summary:
            return self.parent.summary
        else:
            return self.summary 

    @property        
    def get_when(self):
        if self.start_date:
            if getattr(self, "sticky", None):
                return "Top events"
            
            #return self.start_date
            #now = datetime.now()
            date_format = "F Y" # Aikido Cardiff version
            # date_format = "F Y" # standard version
            #if self.start_date.year == now.year:               # they're both this year, so:
            #    date_format = "F"                # end format example: "23rd May"
            return date(self.start_date, date_format)
            #This is the old method of grouping items
            #diff = self.start_date - datetime.now().date()
            #tddict = {999999999: 'Next month & beyond', 31:'This month', 7: 'This week', }
            #tdlist = sorted(tddict.keys())
            #when_heading =  tddict[tdlist[bisect.bisect(tdlist, diff.days)]]
            #return when_heading
        elif self.series:
            return "Regular events"
        
            
    def get_admin_title(self):
        return self.title + " (" + self.get_dates() + ")"


class EventType(models.Model):
    event_type = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['event_type']
        
    def __unicode__(self):
        return self.event_type


class NewsSource(models.Model):
    external_news_source = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.external_news_source


def receiver_function(sender, **kwargs):
    event = kwargs['instance']    
    event.get_root().check_date()

post_save.connect(receiver_function, sender = Event)


class NewsAndEventsPlugin(CMSPlugin, ArkestraGenericPluginOptions):
    DISPLAY = (
        ("news & events", u"News and events"),
        ("news", u"News only"),
        ("events", u"Events only"),
        )
    display = models.CharField("Show", max_length=25,choices = DISPLAY, default = "news & events")
    show_previous_events = models.BooleanField()
    news_heading_text = models.CharField(max_length=25, default=_(u"News"))
    events_heading_text = models.CharField(max_length=25, default=_(u"Events"))
    
try:
    mptt.register(Event)
except mptt.AlreadyRegistered:
    pass    

''' 
entity: ('name',)
building: ('name', 'number', 'street', 'postcode', 'site__site_name',)
website: ('title_set__title',)
'''
