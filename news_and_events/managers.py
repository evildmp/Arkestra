from django.db import models
from django.db.models import Q
from django.conf import settings
from datetime import datetime
import operator

from arkestra_utilities.managers import ArkestraGenericModelManager
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE, COLLECT_TOP_ALL_FORTHCOMING_EVENTS


class EventManager(ArkestraGenericModelManager):

    # this method is not yet used, but will be used as part of the wholesale 
    # rewriting of this code
    def published_items(self):
        return self.model.objects.filter(
            published=True,
            end_date__gte = datetime.now(),            
            )

    def listable_published_items(self):
        return self.published_items().filter(
            in_lists=True,
            )
    
    # --------------------------


    def get_items(self, instance):    
        self.get_events(instance) # gets previous_events, forthcoming_events, top_events, ordinary_events
        if instance.view == "archive":
            instance.events = list(instance.previous_events)
        # keep top events together where appropriate - not in long lists if COLLECT_TOP_ALL_FORTHCOMING_EVENTS is False
        elif instance.order_by == "importance/date" and (instance.view == "current" or COLLECT_TOP_ALL_FORTHCOMING_EVENTS):
            self.get_events_ordered_by_importance_and_date(instance)
            instance.events = instance.top_events + instance.ordinary_events
        else: 
            instance.events = list(instance.forthcoming_events)
        return instance.events
        
    def get_events(self, instance):
        """
        returns forthcoming_events, previous_events, series_events
        """
        if instance.type == "for_person":
            all_events = instance.person.event_featuring.all().order_by('start_date', 'start_time')
        elif instance.type == "for_place":
            all_events = instance.place.event_set.all().order_by('start_date', 'start_time')
        # most likely, we're getting events related to an entity
        elif MULTIPLE_ENTITY_MODE and instance.entity:
            all_events = self.model.objects.filter(Q(hosted_by=instance.entity) | \
            Q(publish_to=instance.entity)).distinct().order_by('start_date', 'start_time')
        else:
            all_events = self.model.objects.all().order_by('start_date', 'start_time')
    
        all_events = all_events.filter(published=True, in_lists=True)
        
        actual_events = all_events.filter(
            # if it's (not a series and not a child) - series events are excluded, children too unless:
            # the child's parent is a series and its children can be advertised
            # tough luck if it's the child of a series and can't be advertised
            Q(series = False, parent = None) | \
            Q(parent__series = True), 
            )
        
        instance.forthcoming_events = actual_events.filter(  
            # ... and it's (a single-day event starting after today) or (not a single-day event and ends after today)     
            Q(single_day_event = True, start_date__gte = datetime.now()) | \
            Q(single_day_event = False, end_date__gte = datetime.now())
            )

        instance.previous_events = actual_events.exclude(  
            # ... and it's (a single-day event starting after today) or (not a single-day event and ends after today)     
            Q(single_day_event = True, start_date__gte = datetime.now()) | \
            Q(single_day_event = False, end_date__gte = datetime.now())
            ).order_by('-start_date', '-start_time')
        
        instance.series_events = all_events.filter(series = True)
        
    def get_events_ordered_by_importance_and_date(self, instance):
        """
        When we need more than just a simple list-by-date, this keeps the top items separate
        """
        ordinary_events = []
        # split the within-date items for this entity into two sets
        actual_events = instance.forthcoming_events
        # top_events jump the queue
        top_events = actual_events.filter(
            Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
            jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
            ).order_by('importance').reverse()  
        # non_top events are the rest
        non_top_events = actual_events.exclude(
            Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
            jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
            )

        # now we have to go through the non-top items, and find any that can be promoted to top_events
        # get the set of dates where possible promotable items can be found             
        dates = non_top_events.dates('start_date', 'day')
        for date in dates:
            # get all non-top items from this date
            possible_top_events = non_top_events.filter(
                start_date = date)
            # promotable items have importance > 0
            # promote the promotable items
            list(top_events).extend(possible_top_events.filter(Q(hosted_by=instance.entity) | \
            Q(jumps_queue_everywhere = True),importance__gte = 1))
            top_events = top_events | possible_top_events.filter(Q(hosted_by=instance.entity) | \
            Q(jumps_queue_everywhere = True),importance__gte = 1)
            # if this date set contains any unimportant items, then there are no more to promote
            demotable_items = possible_top_events.exclude(Q(hosted_by=instance.entity) | \
            Q(jumps_queue_everywhere = True),importance__gte = 1)
            if demotable_items.count() > 0:
                # put those unimportant items into ordinary news
                ordinary_events = demotable_items
                # and stop looking for any more
                break
        # and everything left in non-top items after this date
        if dates:
            remaining_items = non_top_events.filter(start_date__gt=date)
            if ordinary_events:
                ordinary_events = ordinary_events | remaining_items
            top_events = top_events
            ordinary_events = list(ordinary_events)
            for item in top_events:
                item.sticky = True
                if instance.format == "title":
                    item.importance = None
        
        instance.top_events, instance.ordinary_events = list(top_events), ordinary_events
    
