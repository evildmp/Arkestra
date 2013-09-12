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
        r"^vacancies-and-studentships/(?:(?P<slug>[-\w]+)/)$",
        views.VacanciesAndStudentshipsView.as_view(),
        name="vacancies-and-studentships"
        ),

    url(
        r"^vacancies-and-studentships/$",
        views.VacanciesAndStudentshipsView.as_view(),
        {"slug": None},
        name="vacancies-and-studentships-base"
        ),

    # vacancies archives
    url(
        r"^vacancies-archive/(?:(?P<slug>[-\w]+)/)$",
        views.VacanciesArchiveView.as_view(),
        name="vacancies-archive"
        ),

    url(
        r'^vacancies-archive/$',
        views.VacanciesArchiveView.as_view(),
        {"slug": None},
        name="vacancies-archive-base"
        ),

    # previous studentships
    url(
        r"^previous-studentships/(?:(?P<slug>[-\w]+)/)$",
        views.StudentshipsArchiveView.as_view(),
        name="studentships-archive"
        ),

    url(
        r'^previous-studentships/$',
        views.StudentshipsArchiveView.as_view(),
        {"slug": None},
        name="studentships-archive-base"
        ),

    # forthcoming studentships
    url(
        r"^forthcoming-studentships/(?:(?P<slug>[-\w]+)/)$",
        views.StudentshipsForthcomingView.as_view(),
        name="studentships-forthcoming"
        ),

    url(
        r'^forthcoming-studentships/$',
        views.StudentshipsForthcomingView.as_view(),
        {"slug": None},
        name="studentships-forthcoming-base"
        ),
    )
