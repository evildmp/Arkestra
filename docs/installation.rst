############
Installation
############

************
Requirements
************

Akestra requires installation of:

* `Django CMS <http://django-cms.org/>`_
* Django Filer
* Django Widgetry
* Semantic Presentation Editor
* django-polymorphic
* BeautifulSoup
* django-typogrify
* pyquery
* easy-thumbnails
* django-appmedia
* PIL


*********************
Installing components
*********************

Via PIP
=======

Most of these items are available via PIP:

`pip install django-cms django-polymorphic BeautifulSoup django-typogrify pyquery easy-thumbnails django-appmedia PIL`

Note that on some systems at least PIL does not install adequately via pip (it will not handle any image format other than PNG).

From source
===========

Others are currently best installed from source:

* `the Semantic Presentation Editor <https://bitbucket.org/spookylukey/semanticeditor/>`_: `hg clone https://bitbucket.org/spookylukey/semanticeditor` - please note that the current version of the Semantic Presentation Editor does not work with Django's jQuery 1.4.2. This will be remedied shortly, but in the meantime a simple fix is to locate and replace Django's bundled jQuery.js with jQuery 1.3.2.
* `Django Widgetry <https://github.com/evildmp/django-widgetry/>`_ (a tweaked version): `git clone git://github.com/evildmp/django-widgetry.git`
* `the development version of Django Filer <https://github.com/stefanfoulis/django-filer/>`_: `git clone git://github.com/stefanfoulis/django-filer.git`

Installing Arkestra
===================

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

********************
Step-by-step process
********************

Set up a virtual environment 
============================
* `virtualenv arkestra`
* `cd arkestra/`
* `source bin/activate`

Install PIP components
======================

* `pip install django-cms django-polymorphic BeautifulSoup django-typogrify pyquery easy-thumbnails django-appmedia pil`

Download components from source
===============================

* `hg clone https://bitbucket.org/spookylukey/semanticeditor`
* `git clone git://github.com/evildmp/django-widgetry.git`
* `git clone git://github.com/stefanfoulis/django-filer.git`
* `git clone git://github.com/evildmp/Arkestra.git`

Put them on your PYTHONPATH
===========================

There are other, probably better, ways of doing this, but it works.

* `cd lib/python2.5/site-packages` (note - might be some other version of Python)
* `ln -s ../../../Arkestra/arkestra_image_plugin`
* `ln -s ../../../Arkestra/arkestra_utilities`
* `ln -s ../../../Arkestra/contacts_and_people`
* `ln -s ../../../Arkestra/news_and_events`
* `ln -s ../../../Arkestra/vacancies_and_studentships`
* `ln -s ../../../Arkestra/housekeeping`
* `ln -s ../../../Arkestra/links`
* `ln -s ../../../Arkestra/video`
* `ln -s ../../../semanticeditor/semanticeditor`
* `ln -s ../../../django-filer/filer`
* `ln -s ../../../django-widgetry/widgetry`

From this point you can wrestle Arkestra into submission on your own, or get started using the `example` project included, as described in `Getting started`

Fire up the server
==================

* `cd ../../../Arkestra/example/`
* `python manage.py runserver 0.0.0.0:8000`