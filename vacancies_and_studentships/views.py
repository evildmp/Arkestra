from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404

from contacts_and_people.models import Entity

from models import VacanciesPlugin, Vacancy, Studentship 
from cms_plugins import CMSVacanciesPlugin

from arkestra_utilities.settings import NEWS_AND_EVENTS_LAYOUT, MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH, IN_BODY_HEADING_LEVEL


def common_settings(request, slug):
    if slug:
        entity = get_object_or_404(Entity, slug=slug)
    else:
        entity = Entity.objects.base_entity()
    if not (entity.website and entity.website.published and entity.auto_vacancies_page):
        raise Http404 

    request.auto_page_url = request.path
    # request.path = entity.get_website.get_absolute_url() # for the menu, so it knows where we are
    request.current_page = entity.get_website
    context = RequestContext(request)
    instance = VacanciesPlugin()
    instance.limit_to = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.entity = entity
    instance.heading_level = IN_BODY_HEADING_LEVEL
    instance.display = "vacancies-and-studentships"
    instance.format = "details image"
    instance.layout = NEWS_AND_EVENTS_LAYOUT
    instance.view = "current"
    instance.main_page_body_file = "arkestra/universal_plugin_lister.html"
    return instance, context, entity

def vacancies_and_studentships(request, slug):
    instance, context, entity = common_settings(request, slug)    

    instance.type = "main_page"

    meta = {"description": "Vacancies and studentships",}
    title = unicode(entity) + u" vacancies & studentships"
    pagetitle = unicode(entity) + u" vacancies & studentships"

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
        "arkestra_utilities/entity_auto_page.html",
        context,
        )

def archived_vacancies(request, slug):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "vacancies"
    instance.limit_to = None

    meta = {"description": "Archive of vacancies",}
    title = unicode(entity) + u" archived vacancies"
    pagetitle = unicode(entity) + u" archived vacancies"

    CMSVacanciesPlugin().render(context, instance, None)

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "arkestra_utilities/entity_auto_page.html",
        context,
        )
        
def all_current_vacancies(request, slug):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "current"
    instance.display = "vacancies"
    instance.limit_to = None

    CMSVacanciesPlugin().render(context, instance, None)

    meta = {"description": "All current vacancies",}
    title = unicode(entity) + u" current vacancies"
    pagetitle = unicode(entity) + u" current vacancies"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "arkestra_utilities/entity_auto_page.html",
        context,
        )

def archived_studentships(request, slug):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "studentships"
    instance.limit_to = None

    CMSVacanciesPlugin().render(context, instance, None)

    meta = {"description": "Archive of studentships",}
    title = unicode(entity) + u" archived studentships"
    pagetitle = unicode(entity) + u" archived studentships"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "arkestra_utilities/entity_auto_page.html",
        context,
        )
        
def all_current_studentships(request, slug):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "current"
    instance.display = "studentships"
    instance.limit_to = None

    CMSVacanciesPlugin().render(context, instance, None)

    meta = {"description": "All current studentships",}
    title = unicode(entity) + u" current studentships"
    pagetitle = unicode(entity) + u" current studentships"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "arkestra_utilities/entity_auto_page.html",
        context,
        )

def vacancy_and_studentship(item):
    entity = item.hosted_by or Entity.objects.base_entity()
    item.link_to_vacancies_and_studentships_page = entity.get_auto_page_url("vacancies-and-studentships")
    item.template = entity.get_template()
    return item

def vacancy(request, slug):
    """
    Responsible for publishing vacancy
    """
    if request.user.is_staff:
        vacancy = get_object_or_404(Vacancy, slug=slug)
    else:
        vacancy = get_object_or_404(Vacancy, slug=slug, published=True)

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
    if request.user.is_staff:
        studentship = get_object_or_404(Studentship, slug=slug)
    else:
        studentship = get_object_or_404(Studentship, slug=slug, published=True)
    
    return render_to_response(
        "vacancies_and_studentships/studentship.html",
        {"studentship": studentship,
        "entity": studentship.hosted_by,
        "meta": {"description": studentship.description,},
        },
        RequestContext(request),
    )
