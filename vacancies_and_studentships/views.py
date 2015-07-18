import datetime
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404

from arkestra_utilities.views import ArkestraGenericView

from contacts_and_people.models import Entity

from models import Studentship, Vacancy
from lister import VacanciesAndStudentshipsCurrentLister, \
    VacanciesArchiveLister, VacanciesForthcomingLister, \
    StudentshipsArchiveLister, StudentshipsForthcomingLister


from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE

class VacanciesAndStudentshipsView(ArkestraGenericView, ):
    auto_page_attribute = "auto_vacancies_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()
        
        self.lister = VacanciesAndStudentshipsCurrentLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_lister.html"
        self.meta = {"description": "Recent vacancies and forthcoming studentships",}
        self.title = unicode(self.entity) + u" vacancies & studentships"
        if MULTIPLE_ENTITY_MODE:
            self.pagetitle = unicode(self.entity) + u" vacancies & studentships"
        else:
            self.pagetitle = "Vacancies & studentships"
        
        
        return self.response(request)

class VacanciesCurrentView(ArkestraGenericView):
    auto_page_attribute = "auto_vacancies_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = VacanciesForthcomingLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable list of forthcoming studentships",}
        self.title = u"Forthcoming studentships for %s" % unicode(self.entity)
        self.pagetitle = u"Forthcoming studentships for %s" % unicode(self.entity)

        return self.response(request)

class VacanciesArchiveView(ArkestraGenericView):
    auto_page_attribute = "auto_vacancies_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = VacanciesArchiveLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable archive of vacancies items",}
        self.title = u"Vacancies archive for %s" % unicode(self.entity)
        self.pagetitle = u"Vacancies archive for %s" % unicode(self.entity)

        return self.response(request)

class StudentshipsArchiveView(ArkestraGenericView):
    auto_page_attribute = "auto_vacancies_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = StudentshipsArchiveLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable archive of studentships",}
        self.title = u"Studentships archive for %s" % unicode(self.entity)
        self.pagetitle = u"Studentships archive for %s" % unicode(self.entity)

        return self.response(request)


class StudentshipsForthcomingView(ArkestraGenericView):
    auto_page_attribute = "auto_vacancies_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = StudentshipsForthcomingLister(
            entity=self.entity,
            request=self.request
            )

        self.generic_lister_template = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable list of forthcoming studentships",}
        self.title = u"Forthcoming studentships for %s" % unicode(self.entity)
        self.pagetitle = u"Forthcoming studentships for %s" % unicode(self.entity)

        return self.response(request)


def vacancy(request, slug):
    """
    Responsible for publishing vacancies
    """
    if request.user.is_staff:
        vacancy = get_object_or_404(Vacancy, slug=slug)
    else:
        vacancy = get_object_or_404(Vacancy, slug=slug, published=True, date__gte=datetime.datetime.now())
        
    return render_to_response(
        "vacancies_and_studentships/vacancy.html",
        {
        "vacancy":vacancy,
        "entity": vacancy.get_hosted_by,
        "meta": {"description": vacancy.summary,}
        },
        RequestContext(request),
    )

def studentship(request, slug):
    """
    Responsible for publishing an studentship
    """
    if request.user.is_staff:
        studentship = get_object_or_404(Studentship, slug=slug)
    else:
        studentship = get_object_or_404(Studentship, slug=slug, published=True, date__gte=datetime.datetime.now())
        

    return render_to_response(
        "vacancies_and_studentships/studentship.html",
        {"studentship": studentship,
        "entity": studentship.get_hosted_by,
        "meta": {"description": studentship.summary,},
        },
        RequestContext(request),
        )
