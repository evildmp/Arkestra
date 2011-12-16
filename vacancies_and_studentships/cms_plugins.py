from django import forms
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from arkestra_utilities.generic_models import ArkestraGenericPlugin
from arkestra_utilities.generic_models import ArkestraGenericPluginForm
from arkestra_utilities.mixins import AutocompleteMixin

from contacts_and_people.templatetags.entity_tags import work_out_entity

from models import VacanciesPlugin, Vacancy, Studentship
from mixins import VacancyStudentshipPluginMixin
from menu import menu_dict

class VacanciesStudentshipsPluginForm(ArkestraGenericPluginForm, forms.ModelForm):
    class Meta:
        model = VacanciesPlugin


class CMSVacanciesPlugin(VacancyStudentshipPluginMixin, ArkestraGenericPlugin, AutocompleteMixin, CMSPluginBase):
    model = VacanciesPlugin
    name = _("Vacancies & Studentships")
    form = VacanciesStudentshipsPluginForm
    menu_cues = menu_dict
    
    fieldsets = (
        (None, {
        'fields': (('display', 'layout', 'list_format',),  ( 'format', 'order_by', 'group_dates',), 'limit_to')
    }),
        ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('entity', 'heading_level', ('vacancies_heading_text', 'studentships_heading_text'),),
    }),
    )

    # autocomplete fields
    related_search_fields = ['entity',]

    def icon_src(self, instance):
        return "/static/plugin_icons/vacancies_and_studentships.png"

plugin_pool.register_plugin(CMSVacanciesPlugin)