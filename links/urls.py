from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    url(
        r'^chainedselectchoices$',
        views.ChainedSelectChoices.as_view(),
        name = 'chained_select_choices'
    ),
)
