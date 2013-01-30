# this file exists to help avoid circular imports

from django.db import models

class ArkestraGenericPluginItemOrdering(models.Model):
    class Meta:
        abstract = True

    inline_item_ordering = models.PositiveSmallIntegerField(
        "Position",
        help_text="0 is first", 
        default = 0, 
        ) 
    active = models.BooleanField(default=True)
