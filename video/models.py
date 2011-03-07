# from django.utils.translation import ugettext_lazy as _
from django.db import models
# from cms.models import CMSPlugin, Page
# from sorl.thumbnail.main import DjangoThumbnail
# from django.utils.translation import ugettext_lazy as _
# from posixpath import join, basename, splitext, exists
#from filer.fields.image import FilerImageField
#from filer.fields.file import FilerFileField
# from cms import settings as cms_settings
# from django.conf import settings

class VideoPluginEditor(CMSPlugin):
    
    caption = models.TextField(_("Caption"), blank=True, null=True)
    def __unicode__(self):
        return 'Video'