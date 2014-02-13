import operator

from datetime import datetime, timedelta

from django.db import models
from django.db.models import Q
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE, AGE_AT_WHICH_ITEMS_EXPIRE

class ArkestraGenericModelManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def listable_objects(self):
        return self.model.objects.filter(
            published=True,
            in_lists=True,
            )


    # # this method is not yet used, but will be used as part of the wholesale
    # # rewriting of this code
    # def published_items(self):
    #     return self.model.objects.filter(
    #         published=True,
    #         date__lte = datetime.now(),
    #         )
    # 
    # def listable_published_items(self):
    #     return self.model.objects.filter(
    #         published=True,
    #         date__lte = datetime.now(),
    #         in_lists=True,
    #         )
    # 
    # def get_items_list(
    #     self,
    #     entity=None,
    #     show_expired=True,
    #     order_by="date",
    #     format="",
    #     ):
    # 
    #     items = self.model.objects.filter(
    #         published=True,
    #         in_lists=True,
    #         date__lte=datetime.now(),
    #         )
    # 
    #     if MULTIPLE_ENTITY_MODE and entity:
    #         items = items.filter(
    #             Q(hosted_by=entity) | Q(publish_to=entity)
    #             ).distinct()
    # 
    #     if AGE_AT_WHICH_ITEMS_EXPIRE and not show_expired:
    #         expiry_date = datetime.now() - \
    #            timedelta(days=AGE_AT_WHICH_ITEMS_EXPIRE)
    #         items = items.filter(date__gte=expiry_date)
    # 
    # 
    #     if order_by == "importance/date":
    # 
    #         ordinary_items = []
    # 
    #         # split the within-date items for this entity into two sets
    #         publishable_items = items
    # 
    #         sticky_items = items.order_by('-importance').filter(
    #             Q(hosted_by=entity) | Q(is_sticky_everywhere = True),
    #             sticky_until__gte=datetime.today(),
    #             )
    #         non_sticky_items = items.exclude(
    #             Q(hosted_by=entity) | Q(is_sticky_everywhere = True),
    #             sticky_until__gte=datetime.today(),
    #             )
    # 
    #         top_items = list(sticky_items)
    # 
    #         # now go through the non-top items, and find any that can be
    #         # promoted
    #         # get the set of dates where possible promotable items can be found
    #         dates = non_sticky_items.dates('date', 'day').reverse()
    # 
    #         for date in dates:
    # 
    #             # get all non-top items from this date
    #             possible_top_items = non_sticky_items.filter(
    #                 date__year=date.year,
    #                 date__month=date.month,
    #                 date__day=date.day
    #                 )
    # 
    #             # promotable items have importance > 0
    #             # add the promotable ones to the top items list
    #             top_items.extend(possible_top_items.filter(
    #                 Q(hosted_by=entity) | Q(is_sticky_everywhere = True),
    #                 importance__gte = 1)
    #                 )
    # 
    #             # if this date set contains any unimportant items, then
    #             # there are no more to promote
    #             demotable_items = possible_top_items.exclude(
    #                 Q(hosted_by=entity) | Q(is_sticky_everywhere = True),
    #                 importance__gte = 1
    #                 )
    #             if demotable_items.count() > 0:
    #                 # put those unimportant items into ordinary items
    #                 ordinary_items.extend(demotable_items)
    #                 # and stop looking for any more
    #                 break
    # 
    #         # and add everything left in non-sticky items before this date
    #         if dates:
    #             remaining_items = non_sticky_items.filter(date__lte=date)
    #             ordinary_items.extend(remaining_items)
    #             for item in top_items:
    #                 item.sticky = True
    #                 if format == "title":
    #                     item.importance = None
    #             ordinary_items.sort(
    #                 key=operator.attrgetter('date'),
    #                 reverse = True
    #                 )
    #         items = top_items + ordinary_items
    # 
    #     return items
    # 
    # # --------------------------
    # 
    # def get_items(self, instance):
    #     publishable_items = self.get_publishable_items(instance)
    #     if instance.order_by == "importance/date":
    #         items = self.get_items_ordered_by_importance_and_date(instance, publishable_items)
    #         return items
    #     else:
    #         return publishable_items
    # 
    # def get_publishable_items(self, instance):
    #     # returns items that can be published, latest items first
    #     publishable_items = self.get_items_for_entity(instance) \
    #         .filter(date__lte = datetime.today(), published=True, in_lists=True) \
    #         .order_by('-date')
    #     return publishable_items
    # 
    # def get_items_for_entity(self, instance):
    #     # returns every items item associated with this entity,
    #     # or all items items if MULTIPLE_ENTITY_MODE is False, or
    #     # instance.entity is unspecified
    #     if MULTIPLE_ENTITY_MODE and instance.entity:
    #         items_for_entity = self.model.objects.filter(
    #             Q(hosted_by=instance.entity) | Q(publish_to=instance.entity)
    #             ).distinct()
    #     else:
    #         items_for_entity = self.model.objects.all()
    #     # print "All items", all_items.count()
    #     return items_for_entity
    # 
    # def get_items_ordered_by_importance_and_date(
    #     self,
    #     instance,
    #     publishable_items
    #     ):
    # 
    #     ordinary_items = []
    # 
    #     # split the within-date items for this entity into two sets
    #     publishable_items = self.get_publishable_items(instance)
    # 
    #     sticky_items = publishable_items.order_by('-importance').filter(
    #         Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),
    #         sticky_until__gte=datetime.today(),
    #         )
    #     non_sticky_items = publishable_items.exclude(
    #         Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),
    #         sticky_until__gte=datetime.today(),
    #         )
    # 
    #     top_items = list(sticky_items)
    # 
    #     # now go through the non-top items, and find any that can be promoted
    #     # get the set of dates where possible promotable items can be found
    #     dates = non_sticky_items.dates('date', 'day').reverse()
    # 
    #     for date in dates:
    # 
    #         # get all non-top items from this date
    #         possible_top_items = non_sticky_items.filter(
    #             date__year=date.year,
    #             date__month=date.month,
    #             date__day=date.day
    #             )
    # 
    #         # promotable items have importance > 0
    #         # add the promotable ones to the top items list
    #         top_items.extend(possible_top_items.filter(
    #             Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),
    #             importance__gte = 1)
    #             )
    # 
    #         # if this date set contains any unimportant items, then
    #         # there are no more to promote
    #         demotable_items = possible_top_items.exclude(
    #             Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),
    #             importance__gte = 1
    #             )
    #         if demotable_items.count() > 0:
    #             # put those unimportant items into ordinary items
    #             ordinary_items.extend(demotable_items)
    #             # and stop looking for any more
    #             break
    # 
    #     # and add everything left in non-sticky items before this date
    #     if dates:
    #         remaining_items = non_sticky_items.filter(date__lte=date)
    #         ordinary_items.extend(remaining_items)
    #         for item in top_items:
    #             item.sticky = True
    #             if instance.format == "title":
    #                 item.importance = None
    #         ordinary_items.sort(
    #             key=operator.attrgetter('date'),
    #             reverse = True
    #             )
    #     return top_items + ordinary_items




