from datetime import datetime
from datetime import date as pythondate

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.template.defaultfilters import date, time, slugify

import mptt

from cms.models import CMSPlugin
from cms.models.fields import PlaceholderField

from filer.fields.image import FilerImageField

from contacts_and_people.models import Entity, Person, Building, default_entity_id

from links.models import ExternalLink

from arkestra_utilities.output_libraries.dates import nice_date
from arkestra_utilities.universal_plugins import UniversalPluginOptions
from arkestra_utilities.mixins import UniversalPluginModelMixin, URLModelMixin

from managers import NewsArticleManager, EventManager

PLUGIN_HEADING_LEVELS = settings.PLUGIN_HEADING_LEVELS
PLUGIN_HEADING_LEVEL_DEFAULT = settings.PLUGIN_HEADING_LEVEL_DEFAULT
COLLECT_TOP_ALL_FORTHCOMING_EVENTS = settings.COLLECT_TOP_ALL_FORTHCOMING_EVENTS
DATE_FORMAT = settings.ARKESTRA_DATE_FORMAT

class NewsAndEvents(UniversalPluginModelMixin, URLModelMixin):

    content = models.TextField(null=True, blank=True, 
        help_text="Not used or required for external items")
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(NewsAndEvents, self).save(*args, **kwargs)
    
    def get_entity(self):
        """
        Real-world information, can be None
        """
        return self.hosted_by or Entity.objects.get(id=default_entity_id)
    
    def get_website(self):
        """
        for internal Arkestra purposes only
        """
        if self.get_entity():
            return self.get_entity().get_website()
        else:
            return None
        

class NewsArticle(NewsAndEvents):
    date = models.DateTimeField(default=datetime.now,
        help_text=u"Dateline for the item - it won't appear until then" ,  )
    display_indefinitely = models.BooleanField(
        help_text=u"Important news; it won't expire from news lists" , )    
    external_news_source = models.ForeignKey('NewsSource', null=True, blank=True, 
        help_text=u"If this news item is from an external source")
    sticky_until = models.DateField(null=True, blank=True, default=pythondate.today,
        help_text=u"Will be a  featured item until this date")
    is_sticky_everywhere = models.BooleanField(default=False, help_text=u"Will be sticky for other entities") 
    objects = NewsArticleManager()
    
    class Meta:
        ordering = ['-date']
        
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/news/%s/" % self.slug
        
    def get_when(self):
        """
        get_when() provides a human-readable attribute under which items can be grouped.
        Usually, this is an easily-readble rendering of the date (e.g. "April 2010") but it can also be "Top news", for items to be given special prominence.
        """
        if getattr(self, "sticky", None):
            return "Top news"        
        get_when = nice_date(self.date, DATE_FORMAT["date_groups"])
        return get_when


class Event(NewsAndEvents):
    type = models.ForeignKey('EventType')
    featuring = models.ManyToManyField(Person, related_name='%(class)s_featuring',
        null=True, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    SERIES = (
        (False, u"an actual event"),
        (True, u"a series of events"),
    )
    series = models.BooleanField("This is", default=False, choices=SERIES)
    # DO_NOT_LINK_TO_CHILDREN = (
    #     (False, u"have their own pages"),
    #     (True, u"are displayed within this item"),
    # )
    # do_not_link_to_children = models.BooleanField(u"Child events",
    #     default=False,
    #     choices=DO_NOT_LINK_TO_CHILDREN,
    #     )
    DISPLAY_SERIES_NAME = (
        (False, u"display children's names only"),
        (True, u"also display series name"),
    )
    display_series_name = models.BooleanField(u"In lists",
        default=False,
        choices=DISPLAY_SERIES_NAME,
        )
    DISPLAY_SERIES_SUMMARY = (
        (False, u"display children's summaries"),
        (True, u"display the summary for the series"),
    ) 
    display_series_summary = models.BooleanField(u"In lists",
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
    precise_location = models.CharField(max_length=50, null=True, blank=True,
        help_text=u"Precise location within building, for visitors")
    access_note = models.CharField(max_length=255, null=True, blank=True,
        help_text=u"Notes on access/visiting hours/etc")
    # this won't appear in the admin
    jumps_queue_on = models.DateField(null=True, blank=True,
        help_text=u"Will become a featured item on this date") 
    jumps_queue_everywhere = models.BooleanField(default=False)
    registration_enquiries = models.ManyToManyField(Person, 
        related_name = '%(class)s_registration', 
        null = True, blank = True
        )
    objects = EventManager()
    
    class Meta:
        ordering = ['type', 'start_date', 'start_time']
    
    def get_absolute_url(self):
        # should we link to the parent?
        if self.external_url:
            return self.external_url.url
        else:
            return "/event/%s/" % self.slug
  
    @property
    def show_parent_series(self):
        """
        checks whether we should show the parent series too in lists
        """
        if self.parent and self.parent.series and self.parent.display_series_name:
            return True

    @property
    def is_uninformative(self):
        if self.body.cmsplugin_set.all() or self.external_url or self.please_contact.all() or self.registration_enquiries.all() or self.links:
            return False
        else:
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
                print "adding suffix:", suffix, self.slug
        if slug_is_bad(self):
            suffix = slugify(date(self.start_date, "F"))
            if not suffix in self.slug:
                self.slug = self.slug + "-" + suffix
                print "adding suffix:", suffix, self.slug
        if slug_is_bad(self):
            suffix = slugify(date(self.start_date, "d"))
            if not suffix in self.slug:
                self.slug = self.slug + "-" + suffix
                print "adding suffix:", suffix, self.slug
        while slug_is_bad(self):
            self.slug=self.slug + "-x"
            print "adding suffix:", "-x"
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
                dates = nice_date(start_date, start_date_format) + " to " + nice_date(end_date, end_date_format)
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
        
    def get_short_title(self):
        return self.short_title
    
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


class NewsAndEventsPlugin(CMSPlugin, UniversalPluginOptions):
    DISPLAY = (
        ("news & events", u"News and events"),
        ("news", u"News only"),
        ("events", u"Events only"),
        )
    display = models.CharField("Show", max_length=25,choices = DISPLAY, default = "news_and_events")
    entity = models.ForeignKey(Entity, null=True, blank=True, 
        help_text="Leave blank for autoselect", 
        related_name="news_events_plugin")
    show_previous_events = models.BooleanField()
    news_heading_text = models.CharField(max_length=25, default="News")
    events_heading_text = models.CharField(max_length=25, default="Events")
    
try:
    mptt.register(Event)
except mptt.AlreadyRegistered:
    pass    

''' 
entity: ('name',)
building: ('name', 'number', 'street', 'postcode', 'site__site_name',)
website: ('title_set__title',)
'''
