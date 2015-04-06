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

Set up a development environment
================================

::

    git clone https://github.com/evildmp/Arkestra.git
    cd Arkestra
    make develop
    source .env/bin/activate

From this point you can wrestle Arkestra into submission on your own, or get started using the `example` project included.

Set up the supplied example project
===================================

Arkestra includes an example project for Django 1.4.

Assuming that your code was installed into src/arkestra in your virtualenv::

    cd example
    python manage.py syncdb --noinput --all # set up a new database; don't prompt for superuser and use syncdb even on applications with migrations
    python manage.py loaddata example_database.json # load the example database from the fixture

Fire up the server
==================

::

    python manage.py runserver 0.0.0.0:8000 # go!

You should see the famous Institute of Mediaeval Medicine website, complete with images and all kinds of interesting content.

Username and password are both `arkestra`.


Note!
=====

When you start up the server, you may not see any of the news/events/vacancies/studentships items you'd expect.

That's because they're out of date by now - this database was created some time ago.

Go into the news/events/vacancies/studentships and give them more appropriate dates.


Run tests
=========

For tests, `pytest <http://pytest.org/latest/>`_ test framework with
nice `pytest-django <https://pypi.python.org/pypi/pytest-django/>`_ plugin is used instead of ``standard``
unittest approach recommended by Django.

To run tests:

::

    py.test tests

For multipython testing, use just:

::

    tox

To see test coverage:

::

    tox -e coveralls
