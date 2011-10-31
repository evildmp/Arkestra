from django.db import models
from django.db.models import Q
from django.conf import settings
from datetime import datetime
import operator

from arkestra_utilities.universal_plugins import UniversalPluginModelManagerMixin

MULTIPLE_ENTITY_MODE = settings.MULTIPLE_ENTITY_MODE

class StudentshipManager(UniversalPluginModelManagerMixin):
    def get_items(self, instance):
        """
        returns current_studentships, archived_studentships, series_studentships
        """
        # print "____ get_studentships() ____"
        if instance.type == "for_person":
            all_studentships = instance.person.studentship_featuring.all()
        elif instance.type == "for_place":
            all_studentships = instance.place.studentship_set.all()
        # most likely, we're getting studentships related to an entity
        elif MULTIPLE_ENTITY_MODE and instance.entity:
            all_studentships = self.model.objects.filter( \
            Q(hosted_by__in=instance.entity.get_descendants(include_self = True)) | \
            Q(publish_to=instance.entity)).distinct().order_by('closing_date')
        else:
            all_studentships = self.model.objects.all()

            # if an entity should automatically publish its descendants' items
            #     all_studentships = Event.objects.filter(Q(hosted_by__in=instance.entity.get_descendants(include_self=True)) | Q(publish_to=instance.entity)).distinct().order_by('start_date')
        # print "All studentships", instance.type, all_studentships.count()
            
        instance.current_studentships = all_studentships.filter(closing_date__gte = datetime.now())
        instance.archived_studentships = all_studentships.exclude(closing_date__gte = datetime.now())
        
        # print "Previous studentships", instance.archived_studentships.count()
        
        return self.model.objects.all()
    
class VacancyManager(UniversalPluginModelManagerMixin):
    def get_items(self, instance):
        """
        """
        # print "____ get_vacancies() ____"
        if instance.type == "for_person":
            all_vacancies = instance.person.vacancy_featuring.all()
        # most likely, we're getting vacancies related to an entity
        elif MULTIPLE_ENTITY_MODE and instance.entity:
            all_vacancies = self.model.objects.filter( \
            Q(hosted_by__in=instance.entity.get_descendants(include_self = True)) | \
            Q(publish_to=instance.entity)).distinct().order_by('closing_date')
        else:
            all_vacancies = self.model.objects.all()

            # if an entity should automatically publish its descendants' items
            #     all_vacancies = Event.objects.filter(Q(hosted_by__in=instance.entity.get_descendants(include_self=True)) | Q(publish_to=instance.entity)).distinct().order_by('start_date')
        # print "All vacancies", all_vacancies.count()
            
        instance.current_vacancies = all_vacancies.filter(closing_date__gte = datetime.now())
        instance.archived_vacancies = all_vacancies.exclude(closing_date__gte = datetime.now())
        return self.model.objects.all()
