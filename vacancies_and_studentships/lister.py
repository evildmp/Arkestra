from django.utils.translation import ugettext_lazy as _

from arkestra_utilities.generic_lister import (
    ArkestraGenericLister, ArkestraGenericList, ArkestraGenericFilterSet
    )

from arkestra_utilities.settings import (
    NEWS_AND_EVENTS_LAYOUT, LISTER_MAIN_PAGE_LIST_LENGTH,
    MULTIPLE_ENTITY_MODE
    )

from .models import Vacancy, Studentship
import menu


class List(ArkestraGenericList):
    """
    Base List for both Vacancies and Studentships
    """
    item_collections = ("open", "archived")

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.create_item_collections()
        self.truncate_items()
        self.set_show_when()

    def create_item_collections(self):
        if any(
            kind in self.item_collections
                for kind in ("open", "archived")
                ):

            if "open" in self.item_collections:
                self.open = self.items.filter(date__gte=self.now)

            if "archived" in self.item_collections:
                self.archived = self.items.filter(date__lt=self.now)

            self.items = getattr(self, self.item_collections[0])

    def other_items(self):
        other_items = []

        if "open" in self.other_item_kinds and self.open.exists():
            other_items.append({
                "link": self.entity.get_auto_page_url("vacancies-current"),
                "title": "All open vacancies",
                "count": self.open.count(),
                })

        if "archived" in self.other_item_kinds and self.archived.exists():
            other_items.append({
                "link": self.entity.get_auto_page_url("vacancies-archive"),
                "title": "Archived vacancies",
                "count": self.archived.count(),
                })

        if "main" in self.other_item_kinds:
            auto_page_title = menu.menu_dict["title_attribute"]

            if not MULTIPLE_ENTITY_MODE:
                title = getattr(self.entity, auto_page_title)
            else:
                title = "%s %s" % (
                    self.entity.short_name,
                    getattr(self.entity, auto_page_title).lower()
                    )

            other_items.append({
                "link": self.entity.get_auto_page_url("vacancies-and-studentships"),
                "title": title,
                "css_class": "main"
            })
        return other_items


class VacanciesListMixin(object):
    """
    Any Vacancy list needs to inherit this
    """
    model = Vacancy


class StudentshipsListMixin(object):
    """
    Any Studentship list needs to inherit this
    """
    model = Studentship


class VacanciesListCurrent(VacanciesListMixin, List):
    """
    For the main list of Vacancies
    """
    item_collections = ("open", "archived")
    other_item_kinds = ("open", "archived")


class StudentshipsListCurrent(StudentshipsListMixin, List):
    """
    For the main list of Studentships
    """
    item_collections = ("open", "archived")
    other_item_kinds = ("open", "archived")


class VacanciesPluginList(VacanciesListMixin, List):
    """
    For plugins.
    """
    item_collections = ("open", "archived")


class StudentshipsPluginList(StudentshipsListMixin, List):
    """
    For plugins.
    """
    item_collections = ("open", "archived")


class StudentshipsListForPerson(StudentshipsListMixin, List):
    """
    For plugins.
    """
    item_collections = ("open", "archived")

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_person()
        self.create_item_collections()
        self.truncate_items()
        self.set_show_when()


class FilterSet(ArkestraGenericFilterSet):
    fields = ["date"]


class FilterList(List):
    filter_set = FilterSet
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

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.create_item_collections()
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)


class ForthcomingVacanciesList(VacanciesListMixin, FilterList):
    item_collections = ("open", "archived")
    other_item_kinds = ("archived", "main")


class ForthcomingStudentshipsList(StudentshipsListMixin, FilterList):
    item_collections = ("open", "archived")
    other_item_kinds = ("archived", "main")


class VacanciesArchiveList(VacanciesListMixin, FilterList):
    item_collections = ("archived", "open")
    other_item_kinds = ("open", "main")


class StudentshipsArchiveList(StudentshipsListMixin, FilterList):
    item_collections = ("archived", "open")
    other_item_kinds = ("open", "main")


class VacanciesAndStudentshipsCurrentLister(ArkestraGenericLister):
    listkinds = [
        ("vacancies", VacanciesListCurrent),
        ("studentships", StudentshipsListCurrent),
        ]
    display = "vacancies studentships"
    order_by = "importance/date"
    layout = NEWS_AND_EVENTS_LAYOUT
    limit_to = LISTER_MAIN_PAGE_LIST_LENGTH


class VacanciesAndStudentshipsMenuLister(ArkestraGenericLister):
    listkinds = [
        ("vacancies", VacanciesListCurrent),
        ("studentships", StudentshipsListCurrent),
        ]
    display = "vacancies and studentships"
    limit_to = LISTER_MAIN_PAGE_LIST_LENGTH


class VacanciesAndStudentshipsPluginLister(ArkestraGenericLister):
    listkinds = [
        ("vacancies", VacanciesPluginList),
        ("studentships", StudentshipsPluginList),
        ]

    def other_items(self):
        return [{
            "link": self.entity.get_auto_page_url(
                "vacancies-and-studentships"
                ),
            "title": "More %s" % self.display,
            "css_class": "main"
            }]


class StudentshipsPersonLister(ArkestraGenericLister):
    layout = NEWS_AND_EVENTS_LAYOUT
    listkinds = [
        ("studentships", StudentshipsListForPerson),
        ]
    display = "studentships"


class VacanciesArchiveLister(ArkestraGenericLister):
    listkinds = [("vacancies", VacanciesArchiveList)]
    display = "vacancies"


class VacanciesForthcomingLister(ArkestraGenericLister):
    listkinds = [("vacancies", ForthcomingVacanciesList)]
    display = "vacancies"


class StudentshipsArchiveLister(ArkestraGenericLister):
    listkinds = [("studentships", StudentshipsArchiveList)]
    display = "studentships"


class StudentshipsForthcomingLister(ArkestraGenericLister):
    listkinds = [("studentships", ForthcomingStudentshipsList)]
    display = "studentships"
