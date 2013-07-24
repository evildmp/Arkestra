# this file exists to help avoid circular imports - it imports nothing from
# Arkestra

from django.db import models

class ArkestraGenericPluginItemManager(models.Manager):
    def active_items(self):
        return self.filter(active=True)
        
class ArkestraGenericPluginItemOrdering(models.Model):
    class Meta:
        abstract = True
        ordering = ['-position']

    objects = ArkestraGenericPluginItemManager()
    inline_item_ordering = models.PositiveSmallIntegerField(
        "Position",
        help_text="0 is first", 
        default = 0, 
        ) 
    active = models.BooleanField(default=True)
