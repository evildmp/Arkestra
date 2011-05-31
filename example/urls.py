from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
    
    (r'^semantic/', include('semanticeditor.urls')),
    (r"", include("contacts_and_people.urls")),
    (r"", include("features.urls")),
        
    
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
)

if settings.DEBUG:
    urlpatterns+= patterns('',
        url(r'^media/cms/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.CMS_MEDIA_ROOT, 'show_indexes': True}),
        # url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        (r'^' + settings.MEDIA_URL.lstrip('/'), include('appmedia.urls')),
    )

urlpatterns += patterns('',
    url('^autocomplete/$', 'widgetry.views.search', name='widgetry-search'),
    url(r'^', include('cms.urls')),
)
