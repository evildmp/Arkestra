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
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _

class ArkestraTwitterSearch(CMSPlugin):
    twitter_user = models.CharField(_('twitter user'), max_length=75)
    title = models.CharField(_('title'), max_length=75, blank=True)
    query = models.CharField(_('query'), max_length=200, blank=True, default='', help_text=_('Example: "brains AND zombies AND from:umbrella AND to:nemesis": tweets from the user "umbrella" to the user "nemesis" that contain the words "brains" and "zombies"'))
    count = models.PositiveSmallIntegerField(_('count'), help_text=_('Number of entries to display'), default=3)
    
    def __unicode__(self):
        return self.title