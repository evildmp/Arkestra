from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    # news and events items
    (r"^arkestra-lightbox-item/(?P<id>\d+)/$", "arkestra_image_plugin.views.lightbox_item"),
    )
                                                                                               