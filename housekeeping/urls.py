from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
    (r"^repair_mptt/(?P<slug>[-\w\.]+)/$", "housekeeping.repair_mptt.fix"),
    
    (r"^statistics/user/(?P<slug>[-\w]+)$", "housekeeping.statistics.userstats"),
    (r"^statistics/", "housekeeping.statistics.stats"),
    )    