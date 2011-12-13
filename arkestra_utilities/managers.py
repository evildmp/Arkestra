from django.db import models

class ArkestraGenericModelManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)
