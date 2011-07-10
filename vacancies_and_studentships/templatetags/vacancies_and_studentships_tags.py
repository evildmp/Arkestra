from django import template
from vacancies_and_studentships.models import Studentship, Vacancy, VacanciesPlugin
from entity_tags import work_out_entity, entity_for_page

from vacancies_and_studentships.cms_plugins import CMSVacanciesPlugin

from cms.models import Page
from django.db.models import Q

register = template.Library()

@register.inclusion_tag('vacancies_and_studentships_list.html', takes_context=True)
def vacancies_and_studentships(context, heading=3, format=0, max_items=20, entity=None):
    """
    Depends on Cardiff's row/column CSS
    Publishes a date-ordered list of vacancies and studentships
    {% vacancies_and_studentships format max_items %}
    """        
    instance = VacanciesPlugin()
        
    if not entity:
        entity = work_out_entity(context, entity)
    
    instance.entity = entity
    instance.heading_level = heading
    instance.display = 0
    instance.limit_to = max_items
    instance.format = format
    
    nep = CMSVacanciesPlugin()
    
    nep.render(context, instance, None)
    
    return context
    """
    if not entity:
        entity = work_out_entity(context, entity)
    vacancies = Vacancy.objects.filter(
        Q(hosted_by__in=entity.get_descendants(include_self = True)) | Q(also_advertise_on__in=entity.get_descendants(include_self = True))
        )
    studentships = Studentship.objects.filter(
        Q(hosted_by__in=entity.get_descendants(include_self = True)) | Q(also_advertise_on__in=entity.get_descendants(include_self = True))
        )
    cols = "columns1"
    vacancies_class = studentships_class = "firstcolumn"
    if vacancies and studentships:
        cols="columns2"
        vacancies_class = "firstcolumn"
        studentships_class = "lastcolumn"
    more_vacancies = False
    if len(vacancies) > max_items:
        more_vacancies = True 
    more_studentships = False
    if len(studentships) > max_items:
        more_studentships = True        
    return {
        'cols': cols,
        'vacancies_class': vacancies_class,
        'studentships_class': studentships_class,
        'more_vacancies': more_vacancies,
        'more_studentships': more_studentships,
        'vacancies': vacancies[0: max_items],
        'studentships': studentships[0: max_items],
        'format': format,
        'entity': entity,
        'heading': heading,
        }
    """
    
@register.inclusion_tag('vacancylist.html', takes_context=True)
def vacancies(context, entity=None, max_items=20):
    """
    Publishes a date-ordered list of vacancies
    """
    entity = work_out_entity(context, entity)
    vacancies = gather_vacancies(entity)
    return {
        'vacancies': vacancies,
        }

@register.inclusion_tag('studentshiplist.html', takes_context=True)
def studentships(context, entity=None, max_items=20):
    """
    Publishes a date-ordered list of studentships
    """
    entity = work_out_entity(context, entity)
    studentships = gather_studentships(entity)
    return {
        'studentships': studentships,
        }



@register.inclusion_tag('listofvacancies.html', takes_context=True)
def list_vacancies_for_entity(context, page):
    entity = entity_for_page(page)
    if entity:
        vacancies = gather_vacancies(entity)
        return {
            'vacancies': vacancies,
            }
    else:
        return {
            'vacancies': ["no","vacancies",]
            }

@register.inclusion_tag('listofstudentships.html', takes_context=True)
def list_studentships_for_entity(context, page):
   entity = entity_for_page(page)
   if entity:
       studentships = gather_studentships(entity)
       return {
           'studentships': studentships,
           }
   else:
       return {
           'studentships': ["no","studentships",]
           }

def gather_vacancies(entity):
    vacancylist = Vacancy.objects.filter(
        Q(hosted_by__in=entity.get_descendants(include_self=True)) |
        Q(also_advertise_on__in=entity.get_descendants(include_self=True))
    )
    return vacancylist

def gather_studentships(entity):
    studentshiplist = Studentship.objects.filter(
        Q(hosted_by__in=entity.get_descendants(include_self=True)) |
        Q(also_advertise_on__in=entity.get_descendants(include_self=True))
    )
    """for item in studentshiplist:
        print item
    
    studentshiplist = set()
    for entity in entity.get_descendants(include_self = True):
        studentshiplist.update(entity.studentship_set.all())
        studentshiplist.update(entity.studentship_advertise_on.all())"""
    
    return studentshiplist
