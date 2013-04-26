#############################
More notes about installation
#############################

With luck you won't even need to refer to this, but just in case, here it is.

The Arkestra applications
=========================

Arkestra is a collection of applications, each of which needs to be put on your PYTHONPATH (Arkestra's setup.py should do this for you):

* arkestra_image_plugin
* arkestra_utilities
* contacts_and_people
* housekeeping
* links
* news_and_events
* vacancies_and_studentships
* video

Other components
================

Akestra requires installation of various components (Arkestra's setup.py should do this for you). They include:

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

pip freeze
==========

This is what `pip freeze` reports, just for your information:

* -e git+git@github.com:evildmp/Arkestra.git@a4cba94661af4b22025a301e70c1c5438bbecd65#egg=Arkestra-dev
* BeautifulSoup==3.2.1
* Django==1.4
* Pillow==1.7.7
* South==0.7.5
* cssselect==0.7.1
* django-classy-tags==0.3.4.1
* -e git+git@github.com:divio/django-cms.git@56afb01890396fe0562c3ce6700afbff81487f80#egg=django_cms-dev
* -e git+https://github.com/stefanfoulis/django-filer.git@52aa62b11b7c890e45ed0eb45ef37d0300d5d3ee#egg=django_filer-dev
* django-mptt==0.5.2
* django-polymorphic==0.2
* django-sekizai==0.6.1
* django-typogrify==1.3
* -e git+git@github.com:evildmp/django-widgetry.git@87885698bb3b1c0913a642a0b242a21557b3da09#egg=django_widgetry-dev
* easy-thumbnails==1.0.3
* html5lib==0.95
* lxml==2.3.4
* pyquery==1.2.1
* -e hg+https://bitbucket.org/spookylukey/semanticeditor@6a344716ddd2791c98af773fdfc6bb50107c3b8f#egg=semanticeditor-dev
* smartypants==1.6.0.3
* wsgiref==0.1.2


Pillow and PIL
==============

Arkestra will install Pillow. It'll work with PIL too, but Pillow is much easier to use with setuptools.

If you must use PIL
-------------------

You can try `pip install PIL`, but it doesn't always seem to work very well. 

This is often because pip installs PIL from source, and if you don't have the development packages 
(C headers) then it won't
compile it with support for all required file formats. Make sure you get the `-dev` packages first. On
a Debian system doing `apt-get install libjpg-dev libpng-dev` before getting PIL via pip fixed a big 
problem with image uploads because thumbnails weren't being generated.
 

