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

Note on PIL and pip
===================

Most of these items you need to install are available via PIP (see below).

You can try `pip install PIL`, but it doesn't always seem to work very well. 

This is often because pip installs PIL from source, and if you don't have the development packages 
(C headers) then it won't
compile it with support for all required file formats. Make sure you get the `-dev` packages first. On
a Debian system doing `apt-get install libjpg-dev libpng-dev` before getting PIL via pip fixed a big 
problem with image uploads because thumbnails weren't being generated.
 

The Arkestra applications
=========================

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

Until sekizai becomes Django 1.4-compatible, you'll need to stay with Django version 1.3 and make sure you have a compatible version of MPTT.

* `pip install django==1.3.1`
* `pip install django-mptt==0.5.1`
* `pip install pyquery==1.1.1`
* `pip install easy-thumbnails==1.0-alpha-21`
* `pip install django-cms django-polymorphic BeautifulSoup ElementTree django-typogrify django-appmedia`

Download components from source
===============================

* `hg clone https://bitbucket.org/spookylukey/semanticeditor`
* `git clone git://github.com/evildmp/django-widgetry.git`
* `git clone -b video git://github.com/evildmp/django-filer.git`
* `git clone git://github.com/evildmp/Arkestra.git`

Put them on your PYTHONPATH
===========================

There are other, certainly better, ways of doing this, but it works.

* `cd lib/python2.6/site-packages` # or wherever your site-packages is
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

Note!
=====

When you start up the server, you won't see any of the news/events/vacancies/studentships items you'd expect. 

That's because they're all out of date by now - this database was created some time ago.

Go into the news/events/vacancies/studentships and give them more appropriate dates.
