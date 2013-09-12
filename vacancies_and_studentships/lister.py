import operator
from datetime import datetime, timedelta

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from django_easyfilters import FilterSet

from arkestra_utilities.generic_lister import ArkestraGenericLister, ArkestraGenericList

from arkestra_utilities.settings import NEWS_AND_EVENTS_LAYOUT, MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH, AGE_AT_WHICH_ITEMS_EXPIRE

from .models import Vacancy, Studentship
from menu import menu_dict


class VacanciesStudentshipsList(ArkestraGenericList):
    item_collections = (
        "open",
        "archived"
        )
    
    def create_item_collections(self):

        if any(kind in self.item_collections for kind in (
            "open", 
            "archived"
            )):

            if "open" in self.item_collections:
                self.open = self.items_for_context.filter(date__gte=self.now)

            if "archived" in self.item_collections:
                self.archived = self.items_for_context.filter(date__lte=self.now)
                
            self.items = getattr(self, self.item_collections[0])

class VacanciesList(VacanciesStudentshipsList):
    model = Vacancy
    heading_text = _(u"Vacancies")


    def other_items(self):
        other_items_attributes = {
            "open": {
                "link": self.entity.get_auto_page_url("open-vacancies"),
                "title": "All open vacancies",
                "count": self.open.count(),
                },
            "archived": {
                "link": self.entity.get_auto_page_url("previous-vacancies"),
                "title": "Archived vacancies",
                "count": self.archived.count(),
                },
            "main": {
                "link": self.entity.get_auto_page_url(menu_dict["url_attribute"]),
                "title": "%s %s" % (
                    self.entity.short_name,
                    getattr(self.entity, menu_dict["title_attribute"]).lower()
                    ),
                "cls": "main"
                },
            }                    
        
        other_items = []
        for kind in self.other_item_kinds:
            if getattr(self, kind):
                other_items.append(other_items_attributes[kind])
        
        return other_items


class VacanciesFilterSet(FilterSet):
    fields = ['date',]

class VacanciesFilterList(ArkestraGenericList):
    filter_set = VacanciesFilterSet
    search_fields = [
        {
            "field_name": "text",
            "field_label": "Title/summary",
            "placeholder": "Search",
            "search_keys": [
                "title__icontains",
                "summary__icontains",
                ],
            },
        ]

    def additional_list_processing(self):
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)


class VacanciesListCurrent(VacanciesList):
    other_item_kinds = ("archive",)

    def additional_list_processing(self):
        # self.remove_expired()
        self.truncate_items()
        self.set_show_when()


class VacanciesListArchive(VacanciesFilterList, VacanciesList):
    item_collections = ("archived", "open")
    other_item_kinds = ("open", "main")


class VacanciesListForthcoming(VacanciesFilterList, VacanciesList):
    item_collections = ("open", "archived")
    other_item_kinds = ("archived", "main")


class VacanciesListCurrent(VacanciesList):
    item_collections = ("open", "archived")
    other_item_kinds = ("archived", "open")


class VacanciesListPlugin(VacanciesList):
    def additional_list_processing(self):
        self.remove_expired()
        self.truncate_items()
        self.set_show_when()


class StudentshipsList(VacanciesStudentshipsList):
    model = Studentship
    heading_text = _(u"Studentships")

    def other_items(self):
        other_items_attributes = {
            "open": {
                "link": self.entity.get_auto_page_url("open-studentships"),
                "title": "All open studentships",
                "count": self.open.count(),
                },
            "archived": {
                "link": self.entity.get_auto_page_url("previous-studentships"),
                "title": "Archived studentships",
                "count": self.archived.count(),
                },
            "main": {
                "link": self.entity.get_auto_page_url(menu_dict["url_attribute"]),
                "title": "%s %s" % (
                    self.entity.short_name,
                    getattr(self.entity, menu_dict["title_attribute"]).lower()
                    ),
                "cls": "main"
                },
            }                    
        
        other_items = []
        for kind in self.other_item_kinds:
            if getattr(self, kind, None):
                other_items.append(other_items_attributes[kind])
        
        return other_items


class StudentshipsFilterSet(FilterSet):
    fields = ['date',]

class StudentshipsFilterList(ArkestraGenericList):
    filter_set = StudentshipsFilterSet
    search_fields = [
        {
            "field_name": "text",
            "field_label": "Title/summary",
            "placeholder": "Search",
            "search_keys": [
                "title__icontains",
                "summary__icontains",
                ],
            },
        ]

    def additional_list_processing(self):
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)

class StudentshipsListArchive(StudentshipsFilterList, StudentshipsList):
    item_collections = ("archived", "open")
    other_item_kinds = ("open", "main")


class StudentshipsListForthcoming(StudentshipsFilterList, StudentshipsList):
    item_collections = ("open", "archived")
    other_item_kinds = ("archived", "main")


class StudentshipsListCurrent(StudentshipsList):
    item_collections = ("open", "archived")
    other_item_kinds = ("archived", "open")


class StudentshipsListCurrent(StudentshipsList):
    other_item_kinds = ("archived",)

    def additional_list_processing(self):
        self.remove_expired()
        self.truncate_items()
        self.set_show_when()


class StudentshipsListPlugin(StudentshipsList):
    def additional_list_processing(self):
        # self.remove_expired()
        self.truncate_items()
        self.set_show_when()


class StudentshipsListForPerson(StudentshipsList):
    item_collections = ("open",)

    def additional_list_processing(self):
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()

    def set_items_for_context(self):
        self.items_for_context = self.all_listable_items.filter(supervisors=self.person)


class VacanciesAndStudentshipsCurrentLister(ArkestraGenericLister):
    listkinds=[
        ("vacancies", VacanciesListCurrent),
        ("studentships", StudentshipsListCurrent),
            ]
    display="vacancies studentships"
    order_by="importance/date"
    layout=NEWS_AND_EVENTS_LAYOUT
    limit_to=MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH


class VacanciesAndStudentshipsMenuLister(ArkestraGenericLister):
    listkinds=[
        ("vacancies", VacanciesListCurrent),
        ("studentships", StudentshipsListCurrent),
            ]
    display="vacancies and studentships"
    limit_to=MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH


class VacanciesAndStudentshipsPluginLister(ArkestraGenericLister):
    listkinds = [
        ("vacancies", VacanciesListPlugin),
        ("studentships", StudentshipsListPlugin),
            ]


    def other_items(self):
        return [{
            "link": self.entity.get_auto_page_url("vacancies-and-studentships"),
            "title": "More %s" % self.display,
            "cls": "main"
            }]


class VacanciesAndStudentshipsPersonLister(ArkestraGenericLister):
    layout=NEWS_AND_EVENTS_LAYOUT
    listkinds = [
        ("studentships", StudentshipsListForPerson),
            ]
    display="studentships"


class VacanciesArchiveLister(ArkestraGenericLister):
    listkinds=[("vacancies", VacanciesListArchive)]
    display="vacancies"


class VacanciesForthcomingLister(ArkestraGenericLister):
    listkinds=[("vacancies", VacanciesListForthcoming)]
    display="vacancies"


class StudentshipsArchiveLister(ArkestraGenericLister):
    listkinds=[("studentships", StudentshipsListArchive)]
    display="studentships"


class StudentshipsForthcomingLister(ArkestraGenericLister):
    listkinds=[("studentships", StudentshipsListForthcoming)]
    display="studentships"

