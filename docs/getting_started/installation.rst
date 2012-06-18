############
Installation
############


***********
Quick start
***********

Prerequisites
=============

These steps assume that you have the following available on your system:

* pip
* Git
* Mercurial

Set up a virtual environment 
============================
* `virtualenv arkestra`
* `cd arkestra/`
* `source bin/activate`

Install PIP components
======================

* `pip install -e git+git@github.com:divio/django-cms.git@develop#egg=django-cms`
* `pip install -e git+git@github.com:evildmp/Arkestra.git@pip#egg=Arkestra`
* `pip install -e hg+https://bitbucket.org/spookylukey/semanticeditor#egg=semanticeditor`
* `pip install -e git+git@github.com:evildmp/django-widgetry.git#egg=django-widgetry`
* `pip install -e git+https://github.com/stefanfoulis/django-filer.git#egg=django-filer`


From this point you can wrestle Arkestra into submission on your own, or get started using the `example` project included.

Set up the supplied example database
====================================

* `cd src/arkestra/example` # or wherever your Arkestra source gets put

* `python manage.py syncdb` # set up a new database

Answer `no` to the question about setting up a superuser.

* `python manage.py reset contenttypes` # reset all the contenttype relations; we'll supply them in the fixture below

Answer `yes`.

* `python manage.py loaddata example_database.json` # load the example database from the fixture

Fire up the server
==================

* `python manage.py runserver 0.0.0.0:8000` # go!

Username and password are both `arkestra`.     

Note!
=====

When you start up the server, you won't see any of the news/events/vacancies/studentships items you'd expect. 

That's because they're all out of date by now - this database was created some time ago.

Go into the news/events/vacancies/studentships and give them more appropriate dates.

