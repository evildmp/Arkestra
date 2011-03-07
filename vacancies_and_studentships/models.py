from django.db import models
from contacts_and_people.models import Entity, Person
from cms.models import Page
from datetime import datetime

from cms.models import CMSPlugin

class CommonVacancyAndStudentshipInformation(models.Model):
    class Meta:
        abstract = True
        ordering = ['-closing_date']
    short_title = models.CharField(blank=True, max_length = 50, null=True)
    title = models.CharField(max_length = 250)
    closing_date = models.DateField()
    summary = models.TextField(
        help_text = "Maximum two lines",
        )
    description = models.TextField(help_text = "Not used or required for external items",)
    hosted_by = models.ForeignKey(Entity,
        blank=True, null=True,
        help_text = u"The research group or department responsible for this vacancy")
    url = models.URLField(verify_exists=True, blank=True, null=True, help_text = u"To be used <strong>only</strong> for items external to Arkestra. Use with caution!")
    please_contact = models.ForeignKey(Person, 
        related_name = '%(class)s_person', 
        help_text = u'The person to whom enquiries about this should be directed ', 
        null = True, blank = True
        )
    also_advertise_on = models.ManyToManyField(Entity, 
        related_name = "%(class)s_advertise_on",
        help_text = u"Other research groups or departments where this should be advertised", 
        null = True, blank = True
        )
    slug=models.SlugField(unique = True)  
    def __unicode__(self):
        return self.title    

class Vacancy(CommonVacancyAndStudentshipInformation):
    class Meta:
        verbose_name_plural = "Vacancies"
    job_number = models.CharField(max_length = 9)
    salary = models.CharField(blank=True, help_text=u"Please include currency symbol", max_length=255, null=True,)
    def get_absolute_url(self):
        if self.url:
            return self.url
        else:
            return "/vacancy/%s/" % self.slug

class Studentship(CommonVacancyAndStudentshipInformation):
    supervisors = models.ManyToManyField(Person, 
        related_name="%(class)s_people", 
        null = True, blank = True
        )
    def get_absolute_url(self):
        if self.url:
            return self.url
        else:
            return "/studentship/%s/" % self.slug

class VacanciesPlugin(CMSPlugin):
    FORMATS = (
        (0, u"Title only"),
        (1, u"Details"),
        )
    HEADINGS = (
        (0, u"No heading"),
        (3, u"Heading 3"),
        (4, u"Heading 4"),
        (5, u"Heading 5"),
        (6, u"Heading 6"),
        )
    DISPLAY = (
        (0, u"Vacancies and studentships"),
        (1, u"Vacancies only"),
        (2, u"Studentships only"),
        )
    entity = models.ForeignKey(Entity, null = True, blank = True, help_text = "Leave blank for autoselect", related_name = "vacs_studs_plugin")
    display = models.IntegerField(choices = DISPLAY, default = 0)
    format = models.IntegerField(choices = FORMATS, default = 0)
    current_items_only = models.BooleanField(default = True)
    limit_to = models.PositiveSmallIntegerField(default = 5, null = True, blank = True, help_text = u"Leave blank for no limit")
    heading_level = models.PositiveSmallIntegerField(choices = HEADINGS, default = 3)
    vacancies_heading_text = models.CharField(max_length = 25, default = "Vacancies")
    studentships_heading_text = models.CharField(max_length = 25, default = "Studentships")
    more_vacancies_link = models.ForeignKey(Entity, null = True, blank = True, help_text = "Offer a link to all vacancies in chosen entity", related_name = "vacs_plugin_link")
    more_studentships_link = models.ForeignKey(Entity, null = True, blank = True, help_text = "Offer a link to all studentships in chosen entity", related_name = "studs_plugin_link")
