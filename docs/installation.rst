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

Prerequisites
=============

These steps assume that you have the following available on your system:

* pip
* Git
* Mercurial

In addition, Arkestra will need the Python Imaging Library (PIL) to be installed on your system.

Via PIP
=======

Most of these items are available via PIP:

`pip install django-cms django-polymorphic BeautifulSoup django-typogrify pyquery easy-thumbnails django-appmedia`

You can try `pip install PIL`, but it doesn't always seem to work very well. This is often because
pip installs PIL from source, and if you don't have the development packages (C headers) then it won't
compile it with support for all required file formats. Make sure you get the `-dev` packages first. On
a Debian system doing `apt-get install libjpg-dev libpng-dev` before getting PIL via pip fixed a big 
problem with image uploads because thumbnails weren't being generated.
 

From source
===========

Others are currently best installed from source:

* `the Semantic Presentation Editor <https://bitbucket.org/spookylukey/semanticeditor/>`_: `hg clone https://bitbucket.org/spookylukey/semanticeditor`
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

* `pip install django-cms django-polymorphic BeautifulSoup django-typogrify pyquery easy-thumbnails django-appmedia`

Download components from source
===============================

* `hg clone https://bitbucket.org/spookylukey/semanticeditor`
* `git clone git://github.com/evildmp/django-widgetry.git`
* `git clone -b video git://github.com/evildmp/django-filer.git`
* `git clone git://github.com/evildmp/Arkestra.git`

Put them on your PYTHONPATH
===========================

There are other, probably better, ways of doing this, but it works.

* `cd lib/python2.6/site-packages` 
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

From this point you can wrestle Arkestra into submission on your own, or get started using the `example` project included.

Set up the supplied example database
====================================

* `cd ../../../Arkestra/example/`
* `python manage.py syncdb`

Answer `no` to the question about setting up a superuser.

* `python manage.py reset contenttypes`

Answer `yes`.

* `python manage.py loaddata example_database.json`

Fire up the server
==================

* `python manage.py runserver 0.0.0.0:8000`

Username and password are both `arkestra`.
