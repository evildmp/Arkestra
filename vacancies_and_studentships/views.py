import django.http as http
import django.shortcuts as shortcuts
from vacancies_and_studentships.models import *
from django.conf import settings
from links.link_functions import object_links
from django.template import RequestContext

def vacancies_and_studentships(request, slug):
    entity = Entity.objects.get(slug=slug)
    request.current_page = entity.website
    return shortcuts.render_to_response(
        "vacancies_and_studentships/vacancies_and_studentships.html",
        {"entity":entity,
        },
        RequestContext(request),
        )        
      
def vacancy(request, slug):
    """
    Responsible for publishing vacancy
    """
    print " -------- views.vacancy --------"
    vacancy = Vacancy.objects.get(slug=slug)
    entity = vacancy.hosted_by
    template = getattr(entity, "__get_template__", getattr(settings, "CMS_DEFAULT_TEMPLATE", "base.html"))
    links = object_links(vacancy)
    return shortcuts.render_to_response(
        "vacancies_and_studentships/vacancy.html",
        {"vacancy":vacancy,
        "template": template,
        "entity": entity,
        "links": links,
        },
        RequestContext(request),
        )

def studentship(request, slug):
    studentship = Studentship.objects.get(slug=slug)
    entity = studentship.hosted_by
    template = getattr(entity, "__get_template__", getattr(settings, "CMS_DEFAULT_TEMPLATE", "base.html"))    
    links = object_links(studentship)
    return shortcuts.render_to_response(
        "vacancies_and_studentships/studentship.html",
        {"studentship":studentship,
        "template": template,
        "entity": entity,
        "links": links,
        },
        RequestContext(request),
        )