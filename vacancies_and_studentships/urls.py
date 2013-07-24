from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('vacancies_and_studentships.views',
    
    # vacancies and studentship items
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
    
    # archived vacancies 
    url(
        r'^archived-vacancies/$', 
        "archived_vacancies", 
        {"slug": None}, 
        "archived-vacancies-base"
        ),
    url(
        r'^archived-vacancies/(?:(?P<slug>[-\w]+)/)$', 
        "archived_vacancies", 
        name="archived-vacancies"
        ),

    # all current vacancies 
    url(
        r'^current-vacancies/$', 
        "all_current_vacancies", 
        {"slug": None}, 
        name="current-vacancies-base"
        ),
    url(
        r'^current-vacancies/(?:(?P<slug>[-\w]+)/)$', 
        "all_current_vacancies", 
        name="current-vacancies"
        ),

    # archived studentships 
    url(
        r'^archived-studentships/$', 
        "archived_studentships", 
        {"slug": None}, 
        "archived-studentships-base"
        ),
    url(
        r'^archived-studentships/(?:(?P<slug>[-\w]+)/)$', 
        "archived_studentships", 
        name="archived-studentships"
        ),

    # all current studentships 
    url(
        r'^current-studentships/$', 
        "all_current_studentships", 
        {"slug": None}, 
        "current-studentships-base"
        ),
    url(
        r'^current-studentships/(?:(?P<slug>[-\w]+)/)$', 
        "all_current_studentships", 
        name="current-studentships"
        ),

    # main vacancies and studentships 
    url(
        r"^vacancies-and-studentships/$", 
        "vacancies_and_studentships", 
        {"slug": None}, 
        "vacancies-and-studentships-base"
        ),
    url(
        r"^vacancies-and-studentships/(?:(?P<slug>[-\w]+)/)$", 
        "vacancies_and_studentships", 
        name="vacancies-and-studentships"
        ),

)
