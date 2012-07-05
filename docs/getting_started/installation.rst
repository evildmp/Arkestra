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

* `pip install -e git+git@github.com:evildmp/Arkestra.git@pip#egg=Arkestra` # install Arkestra & dependencies
* `pip install -r src/arkestra/REQUIREMENTS.txt` # install the things that pip can't do automatically


From this point you can wrestle Arkestra into submission on your own, or get started using the `example` project included.

Set up the supplied example project
===================================

Arkestra includes example projects for both Django 1.4 and earlier versions.

Assuming that your code was installed into src/arkestra in your virtualenv:
                                   
* `cd src/arkestra/example_14/example_14` # for Django 1.4
* `cd src/arkestra/example_14/example_14` # for Django 1.4

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

