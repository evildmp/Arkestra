##################################
Migrating from an old installation
##################################

***********************************************
Steps for Cardiff University School of Medicine
***********************************************

* import old database from sql file 


Templates
=========

Templates need to exist in the new site.

If for example the old site had placeholders in a `cardiff/medic.html` template, it will need to find the same template in the new project.

The templates also need to have templatetags in them that will work with the new project.

For example:

* {% load typogrify %} will need to be changed to `typogify_tags`
* any templates using `show_menu` will need to load `menu_tags`


Arkestra image plugin
=====================

This used to be cmsplugin_filer_image. 

* delete the migrations directory
* python manage.py schemamigration --initial arkestra_image_plugin


contacts and people
===================

* delete migration files 31-40 and recreate them:

* `python manage.py schemamigration --auto contacts_and_people`

Note that this will try to delete the `Entity.auto_publications_page`, so comment that out in the migration.


Database operations
===================


Non-existent templates
----------------------

Some pages might have templates that don't exist - find the pages in the database, and set their templates to something appropriate.


Badly-named migrations
----------------------

Some migrations had spaces in their names - these should be removed.

* 161	contacts_and_people	> 0001_researcherteacher
* 167	contacts_and_people > 0002_uniqueslugs
* 299	contacts_and_people	> 0030_auto_links

* 170	news_and_events	> 0001_firsttry
* 178	news_and_events	> 0008_inheritname
* 183	news_and_events	> 0012_urlnull
* 187	news_and_events	> 0013_fieldlengths
* 190	news_and_events	> 0014_startseries
* 234	news_and_events	> 0016_tidyingup
* 236	news_and_events	> 0018_showprevious


Tables to trash
---------------

The please_contact tables for news_and_events shouldn't be there; trash them.

Before running migrations
=========================


semantic editor
---------------

The Semantic editor in Cardiff's site has too many classes to merge easily with the fixtures in Arkestra 2.

* rename arkestra_utilities/fixtures/initial_data.json


Running the migrations etc
==========================


* sudo mv /home/topdog/dist-packages/easy_thumbnails/migrations/ /home/topdog/dist-packages/easy_thumbnails/xmigrations
* python manage.py migrate arkestra_image_plugin --fake --ignore-ghost-migrations
* `python manage.py migrate cms --ignore-ghost-migrations` (see note below)
* `python manage.py migrate --ignore-ghost-migrations`
* python manage.py migrate --delete-ghost-migrations
* python manage.py syncdb (for easy_thumbnails, arkestra_utilities.insert)
* sudo mv /home/topdog/dist-packages/easy_thumbnails/xmigrations/ /home/topdog/dist-packages/easy_thumbnails/migrations
* python manage.py migrate easy_thumbnails --fake --ignore-ghost-migrations


Django CMS
----------

if migration 0033 of cms fails with a ValueError: Cannot find a UNIQUE constraint on table cms_title, columns ['publisher_is_draft', 'language', 'page_id']:

* ALTER TABLE `cms_title` ADD CONSTRAINT `cms_title` UNIQUE (`publisher_is_draft`, `language`, `page_id`);

or even:

* delete the constrains manually, and comment out line 10 of the migration.


Reset tweaks back to normal
===========================

* /arkestra_utilities/fixtures/initial_data.json



Transfer images from the old server
===================================

Get the images:

* scp -p -r cftopdog@v026.medcn.uwcm.ac.uk:/home/cftopdog/arkestra_medic/media/filer_public ./
* rename folder from filer_public to filer
* trash output files except thumbnails: find . -type f -path "*/output/*" \! -name "*32x32*" -exec rm {} \;
* change references in database: update filer_file set file = replace(file, "filer_public/", "" );
* make them all public: update filer_file set is_public = 1

== publications ==

./manage.py migrate --fake publications to 0001




== update filer_file table in database ==

update filer_file set file = replace(file, "filer_public/", "" );