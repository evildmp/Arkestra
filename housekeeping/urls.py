from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
    (r"^housekeeping/statistics/", "housekeeping.statistics.stats"),
    (r"^housekeeping/clean_plugins/", "housekeeping.clean_plugins.clean"),
    (r"^housekeeping/convert_to_placeholders/", "housekeeping.convert_to_placeholders.convert"),

    (r"^housekeeping/", "housekeeping.housekeeping.options"),

    (r"^repair_mptt/(?P<slug>[-\w\.]+)/$", "housekeeping.repair_mptt.fix"),
    
    (r"^statistics/user/(?P<slug>[-\w]+)$", "housekeeping.statistics.userstats"),
    )    