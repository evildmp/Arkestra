from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry

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

        return
        
    def last_edit(self):    
        try:
            last_edit = self.edits()[0].action_time
        except IndexError:
            last_edit = "Never"
        
        return last_edit


from django.db import models
from cms.plugins.twitter.models import TwitterSearch
from django.utils.translation import ugettext_lazy as _

class ArkestraTwitterSearch(TwitterSearch):
    twitter_user = models.CharField(_('twitter user'), max_length=75)