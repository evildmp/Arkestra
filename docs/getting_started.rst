###############
Getting Started
###############

*********************************
Using the bundled example project
*********************************

*Note* - at present, the database included with the example project requires a slightly older, and slightly tweaked, version of Django CMS.

That version can be obtained from: https://github.com/evildmp/django-cms

and: git checkout feature/pageflags

This is a temporary nuisance, and will be remedied as soon as possible.

Arkestra comes with a bundled example project - in the `example` folder - which is ready to go, complete with database (the media files are not yet included; sorry).

* `cd example`
* `python manage.py syncdb` (answer `no` when asked to create a super user)
* `python manage.py reset contenttypes` (otherwise the database won't load properly)
* `python manage.py loaddata example.json`
* `python manage.py runserver 0.0.0.0:8000`

************************
Running your own project
************************

The `example` project in Arkestra contains a ready-made `settings.py` file, not to mention the `urls.py` and so on that you'll need.

Either copy these, or if you know what you're doing, copy the relevant parts to the files in your own project.

Start with the Python runserver, and get that going.

In order to make anything work, you'll need to do log in to Admin (username and password are both `arkestra`) and do three things.

* create a Page
* create an Entity
* link the Entity to the Page, by selecting the Page as the Entity's /Home page/

And since Arkestra needs to know what the *base entity* of your site is, in your ``arkestra_settings`` file add something like::

ARKESTRA_BASE_ENTITY = 1

where the value corresponds to the id of your base entity.

*************
In production
*************

Run `collectstatic` - https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/- and the equivalent `symlinkmedia` -https://github.com/divio/django-appmedia - for media files to get them into the right place.

For deployment, point your web hosting platform not at `settings.py`, but `deployment_settings.py`, which turns off various debug modes. 