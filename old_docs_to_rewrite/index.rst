.. Arkestra documentation master file, created by
   sphinx-quickstart on Tue May  3 19:31:41 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

########
Arkestra
########

This document refers to version |release|

Arkestra is an intelligent, semantic web content management system for organisations and institutions. 

It is flexible, modular and extensible, and has a rich set of automated web publishing tools.

Arkestra was developed at `Cardiff University School of Medicine <http://medicine.cardiff.ac.uk/>`_  to provide a platform for the School’s web presence.

=================
Design principles
=================

Arkestra has been designed around a number of key principles:

* the system should provide a genuinely semantic framework for information representing the world and work of organisations
* wherever possible, everything the system publishes should be informed by its semantic model
* wherever possible, the system should act on information it holds, including implicit information, to minimise the work the web editor must do

===========
Key modules
===========

Contacts & people
=================

Arkestra is an institutional CMS. It maintains and publishes information about people and their relationships with the entities they belong to, and the relationships between institutions and their parts.

News & events
=============

Arkestra holds information about what’s on, including information about how important news and events items are, and their relevance to different parts of the institution.

The Semantic Presentation editor
================================

As well as maintaining semantic information rather than just mere data at the highest levels, Arkestra does the same at the level of content editing.

Arkestra has a unique editor, based on the WYMEditor, that:

* creates complex, flexible, multiple-column layouts
* requires no knowledge of HTML/CSS
* creates and enforces well-structured semantic HTML

No other web editor can meet more than two of those criteria.

==========
Django CMS
==========

Arkestra integrates with the architecture of `Django CMS <http://django-cms.org/>`_.

Arkestra requires Django CMS, and can be installed alongside an existing Django CMS project without affecting it in any way.

====================
Other Arkestra sites
====================

Other sites currently running on Arkestra include:

* `The Laugharne Weekend <http://thelaugharneweekend.com/>`_, an annual festival of music and literature in Laugharne, west Wales
* `Fudoshin Aikido Cardiff <http://aikidocardiff.com/>`_, a Cardiff-based Aikido club

Contents:

.. toctree::
   :maxdepth: 2
	
   what_arkestra_does
   contacts_and_people


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

