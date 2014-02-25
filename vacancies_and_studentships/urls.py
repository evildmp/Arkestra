from django.conf.urls.defaults import patterns, url
from vacancies_and_studentships import views

urlpatterns = patterns('vacancies_and_studentships.views',

    # vacancies and studentships items
    url(
        r"^vacancy/(?P<slug>[-\w]+)/$",
        "vacancy",
        name="vacancy"
        ),
    url(
        r"^studentship/(?P<slug>[-\w]+)/$",
        "studentship",
        name="studentship"
        ),

    # main vacancies and studentships
    url(
        r"^vacancies-and-studentships/(?:(?P<slug>[-\w]+)/)?$",
        views.VacanciesAndStudentshipsView.as_view(),
        name="vacancies-and-studentships"
        ),

    # current vacancies
    url(
        r"^vacancies/(?:(?P<slug>[-\w]+)/)?$",
        views.VacanciesCurrentView.as_view(),
        name="vacancies-current"
        ),

    # vacancies archives
    url(
        r"^archived-vacancies/(?:(?P<slug>[-\w]+)/)?$",
        views.VacanciesArchiveView.as_view(),
        name="vacancies-archive"
        ),

    # previous studentships
    url(
        r"^archived-studentships/(?:(?P<slug>[-\w]+)/)?$",
        views.StudentshipsArchiveView.as_view(),
        name="studentships-archive"
        ),

    # forthcoming studentships
    url(
        r"^studentships/(?:(?P<slug>[-\w]+)/)?$",
        views.StudentshipsForthcomingView.as_view(),
        name="studentships-current"
        ),
    )
