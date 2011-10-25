from django.db import models
from django.conf import settings

# from cms.models.fields import PlaceholderField
from cms.models import CMSPlugin

# from filer.fields.image import FilerImageField

from arkestra_utilities.output_libraries.dates import nice_date
from arkestra_utilities.universal_plugins import UniversalPluginOptions, UniversalPluginModelMixin
from arkestra_utilities.mixins import URLModelMixin
from contacts_and_people.models import Entity, Person #, default_entity_id

# from links.models import ExternalLink

from managers import VacancyManager, StudentshipManager

PLUGIN_HEADING_LEVELS = settings.PLUGIN_HEADING_LEVELS
PLUGIN_HEADING_LEVEL_DEFAULT = settings.PLUGIN_HEADING_LEVEL_DEFAULT

class CommonVacancyAndStudentshipInformation(UniversalPluginModelMixin, URLModelMixin):
    class Meta:
        abstract = True
        ordering = ['-closing_date']  

    closing_date = models.DateField()
    
    description = models.TextField(null=True, blank=True,
        help_text="No longer used")

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
    url_path = "vacancy"
    
    job_number = models.CharField(max_length=9)
    salary = models.CharField(blank=True, max_length=255, null=True,
        help_text=u"Please include currency symbol")
    
    objects = VacancyManager()

    class Meta:
        verbose_name_plural = "Vacancies"
        

class Studentship(CommonVacancyAndStudentshipInformation):
    url_path = "studentship"
    
    supervisors = models.ManyToManyField(Person, null=True, blank=True,
        related_name="%(class)s_people")

    objects = StudentshipManager()


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