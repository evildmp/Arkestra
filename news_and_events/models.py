from django.db import models
from django.db.models import Q
from contacts_and_people.models import Entity, Person, Building
from links.models import ExternalLink
from cms.models import Page
from cms.models.fields import PlaceholderField
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.template.defaultfilters import date, time
from django.template import TemplateSyntaxError
import bisect
from filer.fields.image import FilerImageField
from django.template.defaultfilters import slugify
import mptt

from django.conf import settings
from cms.models import CMSPlugin

# if not in multiple_entity_mode, use the default_entity where we can - we need to get this out of here
multiple_entity_mode = getattr(settings, "MULTIPLE_ENTITY_MODE", False)
if not multiple_entity_mode and Entity.objects.all():
    default_entity = Entity.objects.get(id = getattr(settings, 'ARKESTRA_BASE_ENTITY'))
else:
    default_entity = None
get_when_format = getattr(settings, "GET_WHEN_FORMAT", "F Y D")
collect_top_events = getattr(settings, 'COLLECT_TOP_EVENTS', True)

class NewsAndEvents(models.Model):
    # if not in multiple_entity_mode, use the default_entity where we can - we need to get this out of here
    multiple_entity_mode = getattr(settings, "MULTIPLE_ENTITY_MODE", False)
    if not multiple_entity_mode and Entity.objects.all():
        default_entity = Entity.objects.get(id = getattr(settings, 'ARKESTRA_BASE_ENTITY'))
    else:
        default_entity = None
    print default_entity
    class Meta:
        abstract = True
    title = models.CharField(
        help_text = "e.g. Outrage as man bites dog in unprovoked attack",
        max_length=255,        )
    short_title = models.CharField(
        max_length=70, 
        help_text= u"e.g. Man bites dog (if left blank, will be copied from Title)",
        null = True, blank = True
        )
    subtitle =  models.TextField(
        verbose_name = "Summary",
        max_length=256, 
        null = True, blank = False, 
        help_text = "e.g. Cardiff man arrested in latest wave of man-on-dog violence (maximum two lines)",)
    body = PlaceholderField('body',)
    url = models.URLField(verify_exists=True, blank = True, null = True, help_text = u"To be used <strong>only</strong> for items external to Arkestra. Use with caution!")
    external_url = models.ForeignKey(ExternalLink, related_name = "%(class)s_item", blank = True, null = True,)
    publish_to = models.ManyToManyField(Entity, 
        verbose_name = "Additional publishing destinations",
        help_text = u"Use these sensibly - don't send minor items to the home page, for example", 
        null = True, blank = True,
        )
    hosted_by = models.ForeignKey(Entity, default = default_entity.id, related_name = '%(class)s_hosted_events', null = True, blank = True, # though in fact the .save() and the admin between them won't allow null = True
        help_text = u"The entity responsible for publishing this item",
        )
    IMPORTANCES = (
        (0, u"Normal"),
        (1, u"More important"),
        (10, u"Most important"),
        )
    importance = models.PositiveIntegerField(null=True, blank = False, default = 0, choices = IMPORTANCES, help_text = u"Important items will be featured in lists")

    image = FilerImageField(null=True, blank=True)
    slug=models.SlugField(unique = True, max_length = 60, blank = True,
        help_text = "Do not meddle with this unless you know exactly what you're doing!")
    content = models.TextField(null = True, blank = True, 
        help_text = "Not used or required for external items",)

    def get_importance(self):
        if self.importance and not collect_top_events: # only of they are not being gathered together
            return "important"
        else:
            return ""

    def external_site(self):
        return self.external_url.external_site
            
    def save(self, *args, **kwargs):
        print "saving news/event", self
                # print "ext url", self.input_url
        # if self.external_url:
        #     self.external_url, created = ExternalLink.objects.get_or_create(url=self.url, defaults={'title': self.title, 'description': self.subtitle})   
        #     print created, self.external_url     
        super(NewsAndEvents, self).save(*args, **kwargs)



class NewsArticle(NewsAndEvents):
    class Meta:
        ordering = ['-date']
    date = models.DateTimeField(default=datetime.now,
        help_text = u"Dateline for the item - it won't appear until then" , 
        )
    display_indefinitely = models.BooleanField(
        help_text = u"Important news; it won't expire from news lists" , 
        )    
    external_news_source = models.ForeignKey('NewsSource', null = True, blank = True, 
        help_text = u"If this news item is from an external source"
        )
    sticky_until = models.DateField(null=True, blank = True, default=datetime.now, help_text = u"Will be a  featured item until this date")
    is_sticky_everywhere = models.BooleanField(default = False, help_text = u"Will be sticky for other entities") 
    enquiries = models.ManyToManyField(Person, 
        related_name = '%(class)s_person', 
        help_text = u'The person to whom enquiries about this should be directed ', 
        null = True, blank = True
        )
    def __unicode__(self):
        return self.title
    def get_when(self):
        """
        get_when() provides a human-readable attribute under which items can be grouped.
        Usually, this is an easily-readble rendering of the date (e.g. "April 2010") but it can also be "Top news", for items to be given special prominence.
        """
        try:
            # The render function of CMSNewsAndEventsPlugin can set a temporary sticky attribute for Top news items
            if self.sticky:
                return "Top news"
        except AttributeError:
            pass
        
        date_format = "F Y"
        get_when = date(self.date, date_format)
        return get_when
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/news/%s/" % self.slug
    #def save(self):
    #    self.short_title = self.short_title or self.title
    #    super(NewsArticle, self).save()

class Event(NewsAndEvents):
    class Meta:
        ordering = ['type', 'start_date', 'start_time']
    type = models.ForeignKey('EventType')
    featuring = models.ManyToManyField(Person, 
        related_name = '%(class)s_featuring', 
        null = True, blank = True
        )
    # registration_enquiries = models.ManyToManyField(Person, 
    #     related_name = '%(class)s_registration', 
    #     null = True, blank = True
    #     )
    # organisers = models.ManyToManyField(Person, 
    #     related_name = '%(class)s_organiser', 
    #     null = True, blank = True
    #     )
    parent = models.ForeignKey('self', blank=True, null = True, related_name='children')
    series = models.BooleanField(
        help_text = u"A series of regular or repeating events, but not an event itself", 
        default = False)
    no_direct_access_to_children = models.BooleanField(
        verbose_name = "No links to children",
        help_text = u"If this event has child events, don't link to them - just display them", 
        default = False,)
    do_not_advertise_children = models.BooleanField(
        verbose_name = "Hide children",
        help_text = u"In events lists, display this parent, instead of all of its children (useful for events with many children)", 
        default = False,
        )
    always_display_series = models.BooleanField(help_text = "Display the series even if there are no future events in this series - use with caution")
    inherit_name = models.BooleanField(verbose_name = "Inherit name", default = False, help_text = "This event will inherit its name from its parent. You'll have to customise the slug yourself")
    child_list_heading = models.CharField(
        max_length=50, 
        help_text= u"e.g. Conference sessions; Lectures in this series",
        null = True, blank = True,
        )
    start_date = models.DateField(null = True, blank = True, help_text = u"Not required for a series of events")    
    start_time = models.TimeField(null = True, blank = True)    
    end_date = models.DateField(null = True, blank = True)
    end_time = models.TimeField(null = True, blank = True)
    single_day_event = models.BooleanField(default = False)
    building = models.ForeignKey(Building, null = True, blank=True)
    precise_location = models.CharField(help_text=u"Precise location within building, for visitors",
        max_length=50, null = True, blank=True
        )
    access_note = models.CharField(help_text = u"Notes on access/visiting hours/etc",
        max_length=255, null = True, blank=True
        )
    jumps_queue_on = models.DateField(null=True, blank = True, help_text = u"Will become a featured item on this date") # this won't appear in the admin
    jumps_queue_everywhere = models.BooleanField(default = False)
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
            start_date_format = end_date_format = "jS F Y"
            now = datetime.now()
            if start_date.year == end_date.year:            # start and end in the same year, so:
                start_date_format = "jS F"                  # start format example: "3rd May"
                if start_date.month == end_date.month:      # start and end in the same month, so:
                    start_date_format = "jS"                # start format example: "21st" 
                if end_date.year == now.year:               # they're both this year, so:
                    end_date_format = "jS F"                # end format example: "23rd May"
            if self.single_day_event:
                dates = date(start_date, end_date_format)
            else:
                dates = date(start_date, start_date_format) + " to " + date(end_date, end_date_format)
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
    """
    def save(self):
        print "models.save thinks parent is:", self.parent
        if self.parent:
            attribute_list = ['building', 'precise_location', 'hosted_by', 'access_note'] 
            for attribute in attribute_list:
                print "checking which attributes to inherit:", attribute
                if not getattr(self, attribute):
                    print "setting parent attribute", attribute
                    setattr(self, attribute, getattr(self.parent, attribute))
        if self.inherit_name and self.parent:
            self.short_title = self.parent.short_title
            self.title = self.parent.title
    """
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
        
            
    def get_when(self):
        if self.start_date:
            try:
            # The render function of CMSNewsAndEventsPlugin can set a sticky attribute for Top news items
                if self.sticky:
                    return "Top events"
            except AttributeError:
                pass
            
            #return self.start_date
            #now = datetime.now()
            date_format = "F Y D" # Aikido Cardiff version
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
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/event/%s/" % self.slug
    """
    This is going to have to be rewritten, to work on links
    
    def get_related_news(self, related_news = set()):
        related_news.update(self.related_news.all())
        for child_event in self.children.all():
            related_news.update(child_event.get_related_news(related_news))
        return related_news
    def get_related_events(self, related_events = set()):
        related_events.update(self.related_events.all())
        for child_event in self.children.all():
            related_events.update(child_event.get_related_events(related_events))
        return related_events
    def get_related_pages(self, related_pages = set()):
        if not self.series:
            related_pages.update(self.related_pages.all())
            for child_event in self.children.all():
                related_pages.update(child_event.get_related_pages(related_pages))
        return related_pages
    def get_related_people(self, related_people = set()):
        if not self.series:
            related_people.update(self.related_people.all())
            for child_event in self.children.all():
                related_people.update(child_event.get_related_people(related_people))
        return related_people
    """

class EventType(models.Model):
    class Meta:
        ordering = ['event_type']
    event_type = models.CharField(max_length=50)
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

class NewsAndEventsPlugin(CMSPlugin):
    LAYOUTS = (
        ("sidebyside", u"Side-by-side"),
        ("stacked", u"Stacked"),
        )
    layout = models.CharField(max_length=25, choices = LAYOUTS, default = "sidebyside")
    DISPLAY = (
        ("news_and_events", u"News and events"),
        ("news", u"News only"),
        ("events", u"Events only"),
        )
    display = models.CharField(max_length=25,choices = DISPLAY, default = "news_and_events")
    FORMATS = (
        ("title", u"Title only"),
        ("details", u"Details"),
        ("featured horizontal", u"Featured items (horizontal)"),
        ("featured vertical", u"Featured items (vertical)"),
        )
    format = models.CharField(max_length=25,choices = FORMATS, default = "title")
    
    heading_level = models.PositiveSmallIntegerField(choices = settings.HEADINGS, default = settings.H_MAIN_BODY)
    ORDERING = (
        ("date", u"Date"),
        ("importance/date", u"Importance & date"),
        )
    order_by = models.CharField(max_length = 25, choices=ORDERING, default="date")
    entity = models.ForeignKey(Entity, null = True, blank = True, 
        help_text = "Leave blank for autoselect", 
        related_name = "news_events_plugin")
    show_previous_events = models.BooleanField()
    limit_to = models.PositiveSmallIntegerField(default = 5, null = True, blank = True, 
        help_text = u"Leave blank for no limit")
    news_heading_text = models.CharField(max_length = 25, default = "News")
    events_heading_text = models.CharField(max_length = 25, default = "Events")
    def sub_heading_level(self): # requires that we change 0 to None in the database
        if self.heading_level == None: # this means the user has chosen "No heading"
            return 6 # we need to give sub_heading_level a value
        else:
            return self.heading_level + 1 # so if headings are h3, sub-headings are h4
try:
    mptt.register(Event)
except mptt.AlreadyRegistered:
    pass    

''' 
entity: ('name',)
building: ('name', 'number', 'street', 'postcode', 'site__site_name',)
website: ('title_set__title',)
'''
