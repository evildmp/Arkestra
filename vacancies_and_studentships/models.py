from django.db import models
from django.conf import settings

from cms.models.fields import PlaceholderField
from cms.models import CMSPlugin

from filer.fields.image import FilerImageField

from arkestra_utilities.output_libraries.dates import nice_date
from arkestra_utilities.universal_plugins import UniversalPluginOptions

from contacts_and_people.models import Entity, Person, default_entity_id

from links.models import ExternalLink

from managers import VacancyManager, StudentshipManager

PLUGIN_HEADING_LEVELS = settings.PLUGIN_HEADING_LEVELS
PLUGIN_HEADING_LEVEL_DEFAULT = settings.PLUGIN_HEADING_LEVEL_DEFAULT

class CommonVacancyAndStudentshipInformation(models.Model):
    IMPORTANCES = (
        (0, u"Normal"),
        (1, u"More important"),
        (10, u"Most important"),
    )
    short_title = models.CharField(blank=True, max_length=50, null=True)
    title = models.CharField(max_length=250)
    closing_date = models.DateField()
    summary = models.TextField(help_text="Maximum two lines")
    description = models.TextField(null=True, blank=True,
        help_text="Not used or required for external items")
    image = FilerImageField(null=True, blank=True)
    body = PlaceholderField('description')
    hosted_by = models.ForeignKey(Entity, default=default_entity_id, 
        related_name='%(class)s_hosted_events', 
        null=True, blank=True, 
        help_text=u"The research group or department responsible for this vacancy")
    url = models.URLField(verify_exists=True, blank=True, null=True,
        help_text=u"To be used <strong>only</strong> for items external to Arkestra. Use with caution!")
    external_url = models.ForeignKey(ExternalLink, related_name="%(class)s_item",
        blank=True, null=True)
    enquiries = models.ManyToManyField(Person, related_name='%(class)s_person', 
        help_text=u'The person to whom enquiries about this should be directed ', 
        null=True, blank=True)
    publish_to = models.ManyToManyField(Entity, related_name="%(class)s_advertise_on",
        help_text=u"Other research groups or departments where this should be advertised", 
        null=True, blank=True)
    importance = models.PositiveIntegerField(null=True, blank=False, default=0,
        choices=IMPORTANCES, help_text=u"Important items will be featured in lists")
    slug=models.SlugField(unique=True)
    
    class Meta:
        abstract = True
        ordering = ['-closing_date']  

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
        get_when = nice_date(self.closing_date, date_format)
        return get_when

    @property
    def date(self):
        return self.closing_date


class Vacancy(CommonVacancyAndStudentshipInformation):
    job_number = models.CharField(max_length=9)
    salary = models.CharField(blank=True, max_length=255, null=True,
        help_text=u"Please include currency symbol")
    
    objects = VacancyManager()

    class Meta:
        verbose_name_plural = "Vacancies"
        
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/vacancy/%s/" % self.slug


class Studentship(CommonVacancyAndStudentshipInformation):
    supervisors = models.ManyToManyField(Person, null=True, blank=True,
        related_name="%(class)s_people")

    objects = StudentshipManager()

    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/studentship/%s/" % self.slug


class VacanciesPlugin(CMSPlugin, UniversalPluginOptions):
    DISPLAY = (
        (u"vacancies & studentships", u"Vacancies and studentships"),
        (u"vacancies", u"Vacancies only"),
        (u"studentships", u"Studentships only"),
    )
    display = models.CharField(max_length=25,choices=DISPLAY, default="vacancies studentships")
    entity = models.ForeignKey(Entity, null=True, blank=True, 
        help_text="Leave blank for autoselect", related_name="vacs_studs_plugin")
    vacancies_heading_text = models.CharField(max_length=25, default="Vacancies")
    studentships_heading_text = models.CharField(max_length=25, default="Studentships")