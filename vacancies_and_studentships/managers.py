from django.db import models
from django.db.models import Q
from django.conf import settings
from datetime import datetime
import operator

from arkestra_utilities.managers import ArkestraGenericModelManager
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE
    
class ItemManager(ArkestraGenericModelManager):
    def get_items(self, instance):
        """
        returns forthcoming_items, previous_items, series_items
        """

        # most likely, we're getting items related to an entity
        if MULTIPLE_ENTITY_MODE and instance.entity:
            all_items = self.model.objects.filter(
            Q(hosted_by__in=instance.entity.get_descendants(include_self = True)) | \
            Q(publish_to=instance.entity)).distinct().order_by('-closing_date')
        else:
            all_items = self.model.objects.all().order_by('-closing_date')
    
        instance.forthcoming_items = all_items.filter(closing_date__gte = datetime.now())  
        instance.previous_items = all_items.exclude(closing_date__gte = datetime.now())  
        
        if instance.view == "archive":
            instance.items = list(instance.previous_items)

        else: 
            instance.items = list(instance.forthcoming_items)

        return instance.items

class StudentshipManager(ItemManager):
    pass

class VacancyManager(ItemManager):
    pass