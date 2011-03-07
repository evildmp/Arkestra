from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
    (r"^repair_mptt/(?P<slug>[-\w\.]+)/$", "arkestra_utilities.housekeeping.repair_mptt.fix"),
    
    (r"^statistics/user/(?P<slug>[-\w]+)$", "arkestra_utilities.housekeeping.statistics.userstats"),
    (r"^statistics/", "arkestra_utilities.housekeeping.statistics.stats"),
    )    