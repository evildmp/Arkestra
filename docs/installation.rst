############
Installation
############

************
Requirements
************

Components available via PIP
============================

Django CMS
----------

Arkestra requires a working installation of `Django CMS <http://django-cms.org/>`_ as well as numerous other components.

Django CMS has its own installation requirements; installing Django CMS will ensure that most of the components required by Arkestra are also installed.

You'll need to follow `Django CMS's installation instructions <https://www.django-cms.org/en/documentation/>`_; do that first, before installing Arkestra, but basically:

* `pip install django-cms`

will do the trick.


Other components
----------------

In addition, Akestra requires installation of:

* django-polymorphic
* BeautifulSoup
* django-typogrify
* pyquery
* easy-thumbnails
* django-appmedia
* PIL (note: I have had better results installing PIL using other methods)

Installing components via PIP
-----------------------------

`pip install django-cms django-polymorphic BeautifulSoup django-typogrify pyquery easy-thumbnails django-appmedia PIL`

Best currently installed from source
====================================

For now, this is the best way to get hold of these items:

* `the Semantic Presentation Editor <https://bitbucket.org/spookylukey/semanticeditor/>`_: `hg clone https://bitbucket.org/spookylukey/semanticeditor`
* `Django Widgetry <https://github.com/evildmp/django-widgetry/>`_ (a tweaked version): `git clone git://github.comevildmp/django-widgetry.git`
* `the development version of Django Filer <https://github.com/stefanfoulis/django-filer/>`_: `git clone git://github.com/stefanfoulis/django-filer.git`

Arkestra itself
===============

* `Arkestra <https://github.com/evildmp/Arkestra/>`_: `git clone git://github.com/evildmp/Arkestra.git`

Arkestra is a collection of applications, each of which needs to be put on your PYTHONPATH:

* arkestra_image_plugin
* arkestra_utilities
* contacts_and_people
* housekeeping
* links
* news_and_events
* vacancies_and_studentships
* video

The actual installation steps
=============================

Set up a virtual environment 
----------------------------

* virtualenv arkestra
* cd arkestra/
* source bin/activate

Install PIP components
----------------------

* pip install django-cms django-polymorphic BeautifulSoup django-typogrify pyquery easy-thumbnails django-appmedia

Download components from source
-------------------------------

* hg clone https://bitbucket.org/spookylukey/semanticeditor
* git clone git://github.com/evildmp/django-widgetry.git
* git clone git://github.com/stefanfoulis/django-filer.git
* git clone git://github.com/evildmp/Arkestra.git

Put them on your PYTHONPATH
---------------------------

* cd lib/python2.5/site-packages/ (note - might be some other version of Python)
* ln -s ../../../Arkestra/arkestra_image_plugin/
* ln -s ../../../Arkestra/arkestra_utilities/
* ln -s ../../../Arkestra/contacts_and_people/
* ln -s ../../../Arkestra/news_and_events/
* ln -s ../../../Arkestra/vacancies_and_studentships/
* ln -s ../../../Arkestra/housekeeping/
* ln -s ../../../Arkestra/links/
* ln -s ../../../Arkestra/video/
* ln -s ../../../semanticeditor/semanticeditor/
* ln -s ../../../django-filer/filer/
* ln -s ../../../django-widgetry/widgetry/

From this point you can wrestle Arkestra into submission on your own, or get started using the `example` project included, as described in `Getting started`

Fire up the server
------------------

cd ../../../Arkestra/example/
python manage.py runserver 0.0.0.0:8000
