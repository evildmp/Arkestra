from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    # first, try to match /housekeeping/<task>/<execute>
    (r"^housekeeping/(?P<task>[^/]+)/(?P<action>[^/]+)/$", "housekeeping.tasks.tasks"),
    # # no match? 
    (r"^housekeeping/", "housekeeping.tasks.tasks"),


    # (r"^housekeeping/statistics/", "housekeeping.statistics.stats"),
    # (r"^housekeeping/clean_plugins/", "housekeeping.clean_plugins.clean"),
    # 
    # 
    # (r"^repair_mptt/(?P<slug>[-\w\.]+)/$", "housekeeping.repair_mptt.fix"),
    
    # (r"^statistics/user/(?P<slug>[-\w]+)$", "housekeeping.statistics.userstats"),
    )    