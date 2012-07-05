from django.contrib.staticfiles.storage import AppStaticStorage
from django.contrib.staticfiles.finders import AppDirectoriesFinder

class LegacyAppMediaStorage(AppStaticStorage):
    source_dir = 'media'

class LegacyAppDirectoriesFinder(AppDirectoriesFinder):
    storage_class = LegacyAppMediaStorage