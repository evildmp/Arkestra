# from django.db import models
# from django.conf import settings
# 
# PLUGIN_HEADING_LEVELS = settings.PLUGIN_HEADING_LEVELS
# PLUGIN_HEADING_LEVEL_DEFAULT = settings.PLUGIN_HEADING_LEVEL_DEFAULT
# 
# class UniversalPluginOptions(models.Model):
#     class Meta:
#         abstract = True
#     LAYOUTS = (
#         ("sidebyside", u"Side-by-side"),
#         ("stacked", u"Stacked"),
#         )
#     layout = models.CharField("Plugin layout", max_length=25, choices = LAYOUTS, default = "sidebyside")
#     FORMATS = (
#         ("title", u"Title only"),
#         ("details image", u"Details"),
#         )
#     format = models.CharField("Item format", max_length=25,choices = FORMATS, default = "details image")    
#     heading_level = models.PositiveSmallIntegerField(choices = PLUGIN_HEADING_LEVELS, default = PLUGIN_HEADING_LEVEL_DEFAULT)
#     ORDERING = (
#         ("date", u"Date alone"),
#         ("importance/date", u"Importance & date"),
#         )
#     order_by = models.CharField(max_length = 25, choices=ORDERING, default="importance/date")
#     LIST_FORMATS = (
#         ("vertical", u"Vertical"),
#         ("horizontal", u"Horizontal"),
#         )
#     list_format = models.CharField("List format", max_length = 25, choices=LIST_FORMATS, default="vertical")
#     group_dates = models.BooleanField("Show date groups", default = True)
#     limit_to = models.PositiveSmallIntegerField("Maximum number of items", default = 5, null = True, blank = True, 
#         help_text = u"Leave blank for no limit")
# 
#     def sub_heading_level(self): # requires that we change 0 to None in the database
#         if self.heading_level == None: # this means the user has chosen "No heading"
#             return 6 # we need to give sub_heading_level a value
#         else:
#             return self.heading_level + 1 # so if headings are h3, sub-headings are h4
