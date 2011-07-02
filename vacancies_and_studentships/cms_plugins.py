from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import VacanciesPlugin, Vacancy, Studentship
from django.utils.translation import ugettext as _
from django import forms


from contacts_and_people.templatetags.entity_tags import work_out_entity
from functions import get_vacancies_and_studentships

# for tabbed interface
from arkestra_utilities import admin_tabs_extension

from arkestra_utilities.admin import AutocompleteMixin

class VacanciesPluginForm(forms.ModelForm):
    class Meta:
        model = VacanciesPlugin
    def clean(self):
        if "featured" in self.cleaned_data["format"]:
            self.cleaned_data["order_by"] = "importance/date"
        if self.cleaned_data["format"] == "featured horizontal":
            self.cleaned_data["layout"] = "stacked"
            if self.cleaned_data["limit_to"] >3:
                self.cleaned_data["limit_to"] = 3
            if self.cleaned_data["limit_to"] < 2:
                self.cleaned_data["limit_to"] = 2
        if self.cleaned_data["limit_to"] == 0: # that's a silly number, and interferes with the way we calculate later
            self.cleaned_data["limit_to"] = None
        return self.cleaned_data


class CMSVacanciesPlugin(AutocompleteMixin, CMSPluginBase):
    model = VacanciesPlugin
    name = _("Vacancies & Studentships")
    text_enabled = True
    form = VacanciesPluginForm
    render_template = "vacancies_and_studentships_lists.html"
    admin_preview = False
    
    fieldsets = (
        (None, {
        'fields': (('display', 'layout',),  ( 'format', 'order_by',), 'limit_to')
    }),
        ('Advanced options', {
        'classes': ('collapse',),
        'fields': ('entity', 'heading_level', ('vacancies_heading_text', 'studentships_heading_text'),),
    }),
    )

    # autocomplete fields
    related_search_fields = ['entity',]

    def render(self, context, instance, placeholder):
        #print self.render_template
        print "-- in render of CMSVacanciesPlugin --"
        instance.entity = getattr(instance, "entity", None) or work_out_entity(context, None)
        instance.type = getattr(instance, "type", "plugin")
        instance.show_images = getattr(instance, "show_images", True)
        print "instance.show_images", instance.show_images
        try:
            render_template = instance.render_template
        except AttributeError:
            pass
        get_vacancies_and_studentships(instance)
        context.update({ 
            'get_vacancies_and_studentships': instance,
            'placeholder': placeholder,
            })
        print "returning context"
        return context

    def icon_src(self, instance):
        return "/static/plugin_icons/vacancies_and_studentships.png"

plugin_pool.register_plugin(CMSVacanciesPlugin)