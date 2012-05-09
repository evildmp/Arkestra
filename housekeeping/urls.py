from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    (r"^housekeeping/statistics/", "housekeeping.statistics.stats"),

    # /housekeeping/repair_mptt/contacts_and_people.Entity/
    (r"^housekeeping/repair_mptt/(?P<slug>[-\w\.]+)/$", "housekeeping.repair_mptt.fix"),

    # then, try to match /housekeeping/<task>/<execute>
    (r"^housekeeping/(?P<task>[^/]+)/(?P<action>[^/]+)/$", "housekeeping.tasks.tasks"),


    # # no match? 
    (r"^housekeeping/", "housekeeping.tasks.tasks"),


    # (r"^housekeeping/clean_plugins/", "housekeeping.clean_plugins.clean"),
    # 
    # 
    
    # (r"^statistics/user/(?P<slug>[-\w]+)$", "housekeeping.statistics.userstats"),
    )    