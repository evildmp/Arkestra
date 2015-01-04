from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    (r'^semantic/', include('semanticeditor.urls')),
    (r"", include("contacts_and_people.urls")),
    url(r"", include("links.urls")),

    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
)

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('',
    url('^autocomplete/$', 'widgetry.views.search', name='widgetry-search'),
    url(r'^', include('cms.urls')),
)

