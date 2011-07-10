# from django.utils.translation import ugettext_lazy as _
from django.db import models
from cms.models import CMSPlugin

class VideoPluginEditor(CMSPlugin):
    caption = models.TextField(_("Caption"), blank=True, null=True)
    
    def __unicode__(self):
        return 'Video'
