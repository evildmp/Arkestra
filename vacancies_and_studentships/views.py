from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.template import RequestContext

from contacts_and_people.models import Entity, default_entity

from models import VacanciesPlugin, Vacancy, Studentship 
from cms_plugins import CMSVacanciesPlugin

layout = getattr(settings, "NEWS_AND_EVENTS_LAYOUT", "sidebyside")

MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH = settings.MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
IN_BODY_HEADING_LEVEL = settings.IN_BODY_HEADING_LEVEL

def common_settings(request, slug):
    # general values - entity, request, template
    entity = Entity.objects.get(slug=slug) or default_entity
    request.auto_page_url = request.path
    request.path = entity.get_website().get_absolute_url() # for the menu, so it knows where we are
    request.current_page = entity.get_website()
    context = RequestContext(request)
    instance = VacanciesPlugin()
    instance.limit_to = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.default_limit = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.entity = entity
    instance.heading_level = IN_BODY_HEADING_LEVEL
    instance.display = "vacancies-and-studentships"
    instance.format = "details image"
    instance.layout = layout
    instance.view = "current"
    instance.main_page_body_file = "arkestra/universal_plugin_lister.html"
    return instance, context, entity

def vacancies_and_studentships(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)    

    instance.type = "main_page"

    meta = {"description": "Vacancies and studentships",}
    title = str(entity)  + " vacancies & studentships"
    pagetitle = str(entity) + " vacancies & studentships"

    CMSVacanciesPlugin().render(context, instance, None)

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file, 
        "intro_page_placeholder": entity.vacancies_page_intro,
        'everything': instance,
        }
        )

    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )



def archived_vacancies(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "vacancies"
    instance.limit_to = None

    meta = {"description": "Archive of vacancies",}
    title = str(entity)  + " archived vacancies"
    pagetitle = str(entity) + " archived vacancies"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )
        
def all_current_vacancies(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "current"
    instance.display = "vacancies"
    instance.limit_to = None

    CMSVacanciesPlugin().render(context, instance, None)

    meta = {"description": "All current vacancies",}
    title = str(entity)  + " current vacancies"
    pagetitle = str(entity) + " current vacancies"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )

def archived_studentships(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "studentships"
    instance.limit_to = None

    CMSVacanciesPlugin().render(context, instance, None)

    meta = {"description": "Archive of studentships",}
    title = str(entity)  + " archived studentships"
    pagetitle = str(entity) + " archived studentships"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )
        
def all_current_studentships(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "current"
    instance.display = "studentships"
    instance.limit_to = None

    CMSVacanciesPlugin().render(context, instance, None)

    meta = {"description": "All current studentships",}
    title = str(entity)  + " current studentships"
    pagetitle = str(entity) + " current studentships"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )

def vacancy_and_studentship(item):
    entity = item.hosted_by or default_entity
    item.link_to_vacancies_and_studentships_page = entity.get_related_info_page_url("vacancies-and-studentships")
    item.template = entity.get_template()
    return item

def vacancy(request, slug):
    """
    Responsible for publishing vacancy
    """
    vacancy = get_object_or_404(Vacancy, slug=slug)
    vacancy = vacancy_and_studentship(vacancy)
    
    return render_to_response(
        "vacancies_and_studentships/vacancy.html",
        {"vacancy":vacancy,
        "entity": vacancy.hosted_by,
        "meta": {"description": vacancy.description,}
        },
        RequestContext(request),
    )

def studentship(request, slug):
    """
    Responsible for publishing a studentship
    """
    studentship = get_object_or_404(Studentship, slug=slug)
    studentship = vacancy_and_studentship(studentship)
    
    # featuring = event.get_featuring()

    return render_to_response(
        "vacancies_and_studentships/studentship.html",
        {"studentship": studentship,
        "entity": studentship.hosted_by,
        "meta": {"description": studentship.description,},
        },
        RequestContext(request),
    )
