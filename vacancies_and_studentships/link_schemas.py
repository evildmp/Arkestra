# register all interesting models for search
#print "LOADING link_schemas.py for %s" % __name__

from vacancies_and_studentships import models, admin
from links import schema
from django.utils.encoding import smart_unicode

from datetime import datetime
from django.template.defaultfilters import date


def smart_description(obj):
    r = []
    date_format = "jS F Y"
    now = datetime.now()
    if obj.date.year == now.year: # this year
        date_format = "jS F"
    date = date(obj.date, date_format) 
    
    s = u"Closing date: %s" % date
    if obj.please_contact:
        s += u" contact: %s" % smart_unicode(obj.please_contact)
    r.append(s) 
    r.append(u"%s" % obj.summary)
    #r.append(u"%s" % obj.description)
    return "<br />".join(r)

schema.register(models.Vacancy, search_fields=admin.VacancyAdmin.search_fields,
    title=lambda obj: u"%s (%s)" % (obj.title, obj.job_number),
    description='summary',
    short_text='short_title',
    heading='"Related vacancies"',
#                description=smart_description,
    )
schema.register(models.Studentship, search_fields=admin.StudentshipAdmin.search_fields,
    title=lambda obj: u"%s (%s)" % (obj.title, obj.job_number),
    description='summary',
    short_text='short_title',
    heading='"Related studentships"',)