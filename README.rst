Arkestra is a semantic web publishing system for organisations, created in Django.

Documentation & support
***********************

Documentation is in progress; what exists can be found at http://readthedocs.org/docs/arkestra/.

* website: http://arkestra-project.org
* email list and archives: http://groups.google.com/group/django-arkestra
* IRC: #arkestra on irc.freenode.net

Relationship with django CMS
****************************

Arkestra works alongside django CMS https://github.com/divio/django-cms/.

If you're already familiar with django CMS you can regard Arkestra as a set of applications that greatly extend its ability to represent information about the world.

Alternatively, Arkestra is a powerful system that uses django CMS's frameworks to publish information about an institution, its organisation, internal structures and relations with other institutions, people, news, events, place, vacancies, studentships and more.

Arkestra is intelligent
***********************

Arkestra has been designed to make the web editor's job as easy as possible.

It is an intelligent system - it structures information and makes use of connections between data to automate the task of web publishing in useful ways.

It uses these connections, explicit and implicit, to automate as much as can be automated, so that the web editor does not need to do anything that the system should have worked out for itself.

Arkestra is a semantic CMS
**************************

It's also a semantic system - it doesn't simply store data, but manages information according to a model of the real world. This means that every item of information in the system (including for example information published in Django CMS pages) has meaning because it is associated with real-world objects, and placed in their context.

Arkestra in practice
********************

A large project
===============

Arkestra currently publishes the website of Cardiff University School of Medicine: http://medicine.cf.ac.uk/; this includes information about:

1700 people, in 
2700 different roles, in 
160 entities (i.e. parts of the organisation), as well as
330 news articles and 570 events.

It also publishes over 10000 pages, around 90% of which are published automatically by the system.

All this information is managed by a team of over 40 web editors.

In other words it is suited to the needs of large organisations; it's robust and performs well.

Smaller projects
================

It also works well for much smaller projects, its core concepts scale up and down effectively. Two much smaller sites using Arkestra include:

* http://aikidocardiff.com/
* http://thelaugharneweekend.com/

Work to be done
***************

There is much work to be done in Arkestra. It works extremely well, but its codebase needs to be improved to conform with good practice and to make it possible to develop it effectively; it requires:

* better comments
* proper logging
* better documentation
* tests


It also lack some features that it should have; the most urgent of these is multilingual support.