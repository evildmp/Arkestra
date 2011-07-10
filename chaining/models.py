from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey('Category')
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Sub-Category'
        verbose_name_plural = 'Sub-Categories'

    def __unicode__(self):
        return self.name


class Product(models.Model):
    name = models.SlugField(max_length=255)
    subcategory = models.ForeignKey(SubCategory)
    
    def __unicode__(self):
        return self.name.title()

