from django.db import models
from django.db.models import Q
from contacts_and_people.models import Entity, Person, Building, default_entity_id
from links.models import ExternalLink
from cms.models.fields import PlaceholderField
from datetime import datetime
from datetime import date as pythondate
from django.db.models.signals import post_save
from django.template.defaultfilters import date, time, slugify
from arkestra_utilities.output_libraries.dates import nice_date
from filer.fields.image import FilerImageField
import mptt
from cms.models import CMSPlugin
from django.conf import settings

PLUGIN_HEADING_LEVELS = settings.PLUGIN_HEADING_LEVELS
PLUGIN_HEADING_LEVEL_DEFAULT = settings.PLUGIN_HEADING_LEVEL_DEFAULT
COLLECT_TOP_ALL_FORTHCOMING_EVENTS = settings.COLLECT_TOP_ALL_FORTHCOMING_EVENTS


class NewsAndEvents(models.Model):
    IMPORTANCES = (
        (0, u"Normal"),
        (1, u"More important"),
        (10, u"Most important"),
    )
    title = models.CharField(max_length=255,
        help_text="e.g. Outrage as man bites dog in unprovoked attack")
    short_title = models.CharField(max_length=70,  null=True, blank=True,
        help_text= u"e.g. Man bites dog (if left blank, will be copied from Title)")
    subtitle =  models.TextField(verbose_name="Summary",max_length=256,
        null=True, blank=False, 
        help_text="e.g. Cardiff man arrested in latest wave of man-on-dog violence (maximum two lines)",)
    body = PlaceholderField('body')
    url = models.URLField(verify_exists=True, blank=True, null=True,
        help_text=u"To be used <strong>only</strong> for items external to Arkestra. Use with caution!")
    external_url = models.ForeignKey(ExternalLink, related_name="%(class)s_item",
        blank=True, null=True,)
    publish_to = models.ManyToManyField(Entity, null=True, blank=True,
        help_text=u"Use these sensibly - don't send minor items to the home page, for example")
    # though in fact the .save() and the admin between them won't allow null = True
    hosted_by = models.ForeignKey(Entity, default=default_entity_id,
        related_name='%(class)s_hosted_events', null=True, blank=True,
        help_text=u"The entity responsible for publishing this item")
    importance = models.PositiveIntegerField(null=True, blank=False,
        default=0, choices=IMPORTANCES,
        help_text=u"Important items will be featured in lists")

    image = FilerImageField(null=True, blank=True)
    slug=models.SlugField(unique=True, max_length=60, blank=True,
        help_text="Do not meddle with this unless you know exactly what you're doing!")
    content = models.TextField(null=True, blank=True, 
        help_text="Not used or required for external items")
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # if self.external_url:
        #     self.external_url, created = ExternalLink.objects.get_or_create(url=self.url, defaults={'title': self.title, 'description': self.subtitle})   
        #     print created, self.external_url     
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
    
    def external_site(self):
        return self.external_url.external_site
            
    def get_importance(self):
        if self.importance: # if they are not being gathered together, mark them as important
            return "important"
        else:
            return ""

    @property
    def summary(self):
        return self.subtitle


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
    enquiries = models.ManyToManyField(Person, related_name='%(class)s_person', 
        help_text=u'The person to whom enquiries about this should be directed ', 
        null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        
    def __unicode__(self):
        return self.title

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
        try:
            # The render function of CMSNewsAndEventsPlugin can set a temporary sticky attribute for Top news items
            if self.sticky:
                return "Top news"
        except AttributeError:
            pass
        
        date_format = "F Y"
        get_when = nice_date(self.date, date_format)
        return get_when


class Event(NewsAndEvents):
    type = models.ForeignKey('EventType')
    featuring = models.ManyToManyField(Person, related_name='%(class)s_featuring',
        null=True, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    series = models.BooleanField(default=False,
        help_text=u"A series of regular or repeating events, but not an event itself")
    no_direct_access_to_children = models.BooleanField(default=False,
        verbose_name="No links to children",
        help_text=u"If this event has child events, don't link to them - just display them")
    do_not_advertise_children = models.BooleanField(default=False,
        verbose_name="Hide children",
        help_text=u"In events lists, display this parent, instead of all of its children (useful for events with many children)")
    always_display_series = models.BooleanField(
        help_text="Display the series even if there are no future events in this series - use with caution")
    inherit_name = models.BooleanField(verbose_name="Inherit name",
        default=False,
        help_text="This event will inherit its name from its parent. You'll have to customise the slug yourself")
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
    
    class Meta:
        ordering = ['type', 'start_date', 'start_time']
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/event/%s/" % self.slug
        
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
            start_date_format = end_date_format = "l jS F Y"
            now = datetime.now()
            if start_date.year == end_date.year:            # start and end in the same year, so:
                start_date_format = "l jS F"                  # start format example: "3rd May"
                if start_date.month == end_date.month:      # start and end in the same month, so:
                    start_date_format = "l jS"                # start format example: "21st" 
                if end_date.year == now.year:               # they're both this year, so:
                    end_date_format = "l jS F"                # end format example: "23rd May"
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
            try:
            # The render function of CMSNewsAndEventsPlugin can set a sticky attribute for Top news items
                if self.sticky:
                    return "Top events"
            except AttributeError:
                pass
            
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


class NewsAndEventsPlugin(CMSPlugin):
    LAYOUTS = (
        ("sidebyside", u"Side-by-side"),
        ("stacked", u"Stacked"),
        )
    layout = models.CharField("Plugin layout", max_length=25, choices = LAYOUTS, default = "sidebyside")
    DISPLAY = (
        ("news & events", u"News and events"),
        ("news", u"News only"),
        ("events", u"Events only"),
        )
    display = models.CharField("Show", max_length=25,choices = DISPLAY, default = "news_and_events")
    FORMATS = (
        ("title", u"Title only"),
        ("details image", u"Details"),
        )
    format = models.CharField("Item format", max_length=25,choices = FORMATS, default = "details image")    
    heading_level = models.PositiveSmallIntegerField(choices = PLUGIN_HEADING_LEVELS, default = PLUGIN_HEADING_LEVEL_DEFAULT)
    ORDERING = (
        ("date", u"Date alone"),
        ("importance/date", u"Importance & date"),
        )
    order_by = models.CharField(max_length = 25, choices=ORDERING, default="importance/date")
    LIST_FORMATS = (
        ("vertical", u"Vertical"),
        ("horizontal", u"Horizontal"),
        )
    list_format = models.CharField("List format", max_length=25,
        choices=LIST_FORMATS, default="vertical")
    group_dates = models.BooleanField("Show date groups", default=True)
    entity = models.ForeignKey(Entity, null=True, blank=True, 
        help_text="Leave blank for autoselect", 
        related_name="news_events_plugin")
    show_previous_events = models.BooleanField()
    limit_to = models.PositiveSmallIntegerField("Maximum number of items",
        default=5, null=True, blank=True, 
        help_text = u"Leave blank for no limit")
    news_heading_text = models.CharField(max_length=25, default="News")
    events_heading_text = models.CharField(max_length=25, default="Events")
    
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
