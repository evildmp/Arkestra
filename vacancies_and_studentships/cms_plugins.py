from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from models import VacanciesPlugin, Vacancy, Studentship
from django.utils.translation import ugettext as _

from django.db.models import Q

from django.conf import settings

from datetime import date,timedelta

from contacts_and_people.templatetags.entity_tags import work_out_entity

items_expire_after =  date.today() - timedelta(days = getattr(settings, "VACANCIES_EXPIRY_AFTER", 31))

class CMSVacanciesPlugin(CMSPluginBase):
        model = VacanciesPlugin
        name = _("Vacancies & studentships")
        render_template = "vacancies_and_studentships_list.html"
        text_enabled = True
        
        def render(self, context, instance, placeholder):
            print "-- in render of CMSVacanciesPlugin --"
            if instance.entity:
                entity = instance.entity
            else:
                entity = work_out_entity(context, None)
            vacancies = studentships = []
            more_vacancies = False
            max_items = instance.limit_to
            more_studentships = False
            print "instance.display", instance.display
            if instance.heading_level == 0:
                instance.heading_level = None    
            if instance.display == 0 or instance.display == 1:
                print "getting vacancies"
                vacancies = Vacancy.objects.filter(
        Q(hosted_by__in=entity.get_descendants(include_self = True)) | Q(also_advertise_on__in=entity.get_descendants(include_self = True)),
        closing_date__gte = items_expire_after
        ).distinct()
                if len(vacancies) > max_items:
                    more_vacancies = True 
            if instance.display == 0 or instance.display == 2:
                print "getting studentships"
                studentships = Studentship.objects.filter(
        Q(hosted_by__in=entity.get_descendants(include_self = True)) | Q(also_advertise_on__in=entity.get_descendants(include_self = True)),
        closing_date__gte = items_expire_after
        ).distinct()
                if len(studentships) > max_items:
                    more_studentships = True                
            cols = "columns1"
            vacancies_class = studentships_class = "firstcolumn"
            if vacancies and studentships:
                cols="columns2"
                vacancies_class = "firstcolumn"
                studentships_class = "lastcolumn"
            print "entity:",entity
            print "format:", instance.get_format_display()
            context.update({ 
                'entity': entity,
                'vacancies': vacancies,
                'studentships': studentships,
                'format': instance.get_format_display(),
                'heading_level': instance.heading_level,
                'vacancies_heading': instance.vacancies_heading_text,
                'studentships_heading': instance.studentships_heading_text,
                'vacancies_class': vacancies_class,
                'studentships_class': studentships_class,
                'more_vacancies': more_vacancies,
                'more_studentships': more_studentships,
                'vacancies': vacancies[0: max_items],
                'studentships': studentships[0: max_items],
                'more_vacancies_link': instance.more_vacancies_link,
                'more_studentships_link': instance.more_studentships_link,
                'cols': cols,
    
                'object': instance,
                'placeholder': placeholder,
                })
            print "returning from render of CMSVacanciesPlugin"
            return context
        def icon_src(self, instance):
            print "getting icon image for links plugin"
            return "/media/arkestra/vacancies_and_studentships.png"

plugin_pool.register_plugin(CMSVacanciesPlugin)