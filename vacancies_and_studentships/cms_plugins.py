from django.utils.translation import ugettext as _
from django import forms

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from arkestra_utilities.universal_plugins import UniversalPlugin
from arkestra_utilities.universal_plugins import UniversalPluginForm
from arkestra_utilities import admin_tabs_extension
from arkestra_utilities.mixins import AutocompleteMixin

from contacts_and_people.templatetags.entity_tags import work_out_entity
from functions import get_vacancies_and_studentships

from models import VacanciesPlugin, Vacancy, Studentship
from mixins import VacancyStudentshipPluginMixin

# for tabbed interface

class VacanciesStudentshipsPluginForm(UniversalPluginForm, forms.ModelForm):
    class Meta:
        model = VacanciesPlugin


class CMSVacanciesPlugin(UniversalPlugin, VacancyStudentshipPluginMixin, AutocompleteMixin, CMSPluginBase):
    model = VacanciesPlugin
    name = _("Vacancies & Studentships")
    form = VacanciesStudentshipsPluginForm
    auto_page_attribute = "auto_vacancies_page"
    auto_page_slug = "vacancies-and-studentships"
    auto_page_menu_title = "vacancies_page_menu_title"
    
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

    def render(self, context, instance, placeholder):
        self.set_defaults(instance)

        instance.entity = getattr(instance, "entity", None) or work_out_entity(context, None)
        instance.type = getattr(instance, "type", "plugin")
        render_template = getattr(instance, "render_template", "")
        self.get_items(instance)
        self.add_link_to_main_page(instance)
        self.add_links_to_other_items(instance)
        self.set_limits_and_indexes(instance)
        self.determine_layout_settings(instance)
        self.set_layout_classes(instance)
        instance.lists = self.lists
        context.update({ 
            'everything': instance,
            'placeholder': placeholder,
            })
        print "returning context"
        return context

    def icon_src(self, instance):
        return "/static/plugin_icons/vacancies_and_studentships.png"

plugin_pool.register_plugin(CMSVacanciesPlugin)