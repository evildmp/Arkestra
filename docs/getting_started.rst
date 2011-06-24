###############
Getting Started
###############

************************
Setting up your settings
************************

The easiest way to start is by taking a look at the `example` project in Arkestra.

It contains a ready-made `settings.py` file, not to mention the `urls.py` and so on that you'll need.

Either copy these, or if you know what you're doing, copy the relevant parts to the files in your own project.

*****************
Once it's running
*****************

Start with the Python runserver, and get that going.

In order to make anything work, you'll need to do log in to Admin and do three things.

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

For deployment, point your web hosting platform not at `settings.py`, but `deployment_settings.py`.

It turns off various debug modes. 