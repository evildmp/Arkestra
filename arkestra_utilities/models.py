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
        try:
            last_edit = self.edits()[10]
        except IndexError:
            last_edit = "Never"

        return last_edit
        
    def last_edit(self):    
        try:
            last_edit = self.edits()[0].action_time
        except IndexError:
            last_edit = "Never"
        
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
