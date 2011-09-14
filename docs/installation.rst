############
Installation
############

************
Requirements
************

Django CMS
==========

Arkestra requires a working installation of `Django CMS <http://django-cms.org/>`_.

Django CMS has its own installation requirements; installing Django CMS will ensure that most of the components required by Arkestra are also installed.

You'll need to follow `Django CMS's installation instructions <https://www.django-cms.org/en/documentation/>`_; do that first, before installing Arkestra, but basically:

* `pip install django-cms`

will do the trick.



Other components
================

In addition, Akestra requires installation of:

Available through pip
---------------------

* django-filer
* django-polymorphic
* BeautifulSoup
* django-typogrify
* pyquery
* easy-thumbnails
* django-appmedia

`pip install django-filer django-polymorphic BeautifulSoup django-typogrify pyquery easy-thumbnails django-appmedia`

Best currently installed from source
------------------------------------

For now, this is the best way to get hold of these items:

* `the Semantic Presentation Editor <https://bitbucket.org/spookylukey/semanticeditor/>`_: `hg clone https://bitbucket.org/spookylukey/semanticeditor`
* `Django Widgetry <https://github.com/evildmp/django-widgetry/>`_ (a tweaked version): `git clone git@github.com:evildmp/django-widgetry.git`

Arkestra itself
===============

* `Arkestra <https://github.com/evildmp/Arkestra/>`_

Arkestra is a collection of applications, each of which needs to be put on your PYTHONPATH:

* arkestra_image_plugin
* arkestra_utilities
* contacts_and_people
* housekeeping
* links
* news_and_events
* vacancies_and_studentships
* video

From this point you can wrestle Arkestra into submission on your own, or get started using the `example` project included, as described in `Getting started`