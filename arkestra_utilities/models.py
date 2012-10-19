from cms.models.fields import PlaceholderField
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.db import models

class ArkestraUser(User):
    class Meta:
        proxy = True

    def edits(self):
        return LogEntry.objects.filter(user = self).order_by('-id')
        
    def last_10_edits(self):
        last_edit = self.edits()[10]

        return last_edit
        
    def last_edit(self):    
        last_edit = self.edits()[0].action_time
        
        return last_edit

        
class Insert(models.Model):
    insertion_point=models.SlugField(unique=True, max_length=60,
        help_text="Matches the parameter passed to the {% insert %} tag in "
        "your templates")
    content = PlaceholderField('insert')
    description =  models.TextField(max_length=256, null=True, blank=False,
        help_text="To help remind you what this is for")

    def __unicode__(self):
        return self.insertion_point

# from contacts_and_people.models import Entity #, Person, default_entity_id
# from contacts_and_people.templatetags.entity_tags import work_out_entity

# 
# class ArkestraGenericModel(models.Model):
#     class Meta:
#         abstract = True
# 
#     # core fields
#     title = models.CharField(max_length=255,
#         help_text="e.g. Outrage as man bites dog in unprovoked attack")
#     short_title = models.CharField(max_length=255,  null=True, blank=True,
#         help_text= u"e.g. Man bites dog (if left blank, will be copied from Title)")
#     summary = models.TextField(verbose_name="Summary",
#         null=False, blank=False, 
#         help_text="e.g. Cardiff man arrested in latest wave of man-on-dog violence (maximum two lines)",)
#     body = PlaceholderField('body', help_text="Not used or required for external items")    
#     image = FilerImageField(null=True, blank=True)
# 
#     # universal plugin fields 
#     hosted_by = models.ForeignKey(Entity, default=default_entity_id,
#         related_name='%(class)s_hosted_events', null=True, blank=True,
#         help_text=u"The entity responsible for publishing this item")
#     publish_to = models.ManyToManyField(Entity, null=True, blank=True, related_name="%(class)s_publish_to",
#         help_text=u"Use these sensibly - don't send minor items to the home page, for example")
#     please_contact = models.ManyToManyField(Person, related_name='%(class)s_person', 
#         help_text=u'The person to whom enquiries about this should be directed ', 
#         null=True, blank=True)
#     IMPORTANCES = (
#         (0, u"Normal"),
#         (1, u"More important"),
#         (10, u"Most important"),
#     )
#     importance = models.PositiveIntegerField(null=True, blank=False,
#         default=0, choices=IMPORTANCES,
#         help_text=u"Important items will be featured in lists")
# 
#     def get_importance(self):
#         if self.importance: # if they are not being gathered together, mark them as important
#             return "important"
#         else:
#             return ""
# 
#     @property
#     def links(self):
#         return self.object_links_set.all()
# 
#     @property
#     def external_url(self):
#         # if the inheriting model doesn't have an external_url attribute, we'll give it a None one just in case this is needed
#         return None
#     
#     @property
#     def is_uninformative(self):
#         if self.external_url or self.body.cmsplugin_set.all() or self.please_contact.all() or self.links:
#             return False
#         else:
#             return True
