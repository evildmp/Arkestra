####################################
Migrating from an older installation
####################################

If you have been using a version of Arkestra prior to the publishing of version 2.0 on Github, you have a bit of work to do.

This may look unpleasant, but it's been tested and is mainly a matter of making sure that you paste into the right place.

Before you do anything else
===========================
Work on a copy of your repository and database. You were going to do that anyway, right?

Clear out the old migration records
===================================
Find your south_migrationhistory table and clear out the old migration records. We're going to re-create these, so you need to:

* DELETE FROM `south_migrationhistory` WHERE `app_name`='arkestra_image_plugin'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='contacts_and_people'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='links'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='news_and_events'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='vacancies_and_studentships'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='video'; 

Trash your old migrations
=========================
Now, for each Arkestra application, trash its migrations directory (because we want to get rid of the old messy trail of migrations, and have just a single clean initial migration for each).

Do this in the Arkestra directory:

* `rm -r arkestra_image_plugin/migrations contacts_and_people/migrations links/migrations news_and_events/migrations vacancies_and_studentships/migrations video/migrations`

Create new migrations
=====================
Then create new, clean initial migrations for each one.

Make sure you're in the project directory:

* `python manage.py convert_to_south arkestra_image_plugin`
* `python manage.py convert_to_south contacts_and_people`
* `python manage.py convert_to_south links`
* `python manage.py convert_to_south news_and_events`
* `python manage.py convert_to_south vacancies_and_studentships`
* `python manage.py convert_to_south video`

Now your migrations should match your models, and your database records should indicate that they match.

Move your migrations
====================
In a moment, you'll pull in the new version of Arkestra, but you don't want to overwrite the new migrations you just created, so put them in a safe place: 

Do this in the Arkestra directory (we'll use --delete-ghost-migrations on the first one just in case):

* mv `arkestra_image_plugin/migrations arkestra_image_plugin/my_migrations --delete-ghost-migrations`
* mv `contacts_and_people/migrations contacts_and_people/my_migrations`
* mv `links/migrations links/my_migrations`
* mv `news_and_events/migrations news_and_events/my_migrations`
* mv `vacancies_and_studentships/migrations vacancies_and_studentships/my_migrations`
* mv `video/migrations video/my_migrations`

Checkout the new version of Arkestra
====================================
Switch to the branch of Arkestra with cleaned up migrations.

Fetch updated references from Github:

* `git fetch origin`

Checkout the reference clean-migrations branch.

* git `checkout clean-migrations`

Replace its migrations with the ones you created
================================================
* `rm -r arkestra_image_plugin/migrations contacts_and_people/migrations links/migrations news_and_events/migrations vacancies_and_studentships/migrations video/migrations`

* `mv arkestra_image_plugin/my_migrations arkestra_image_plugin/migrations`
* `mv contacts_and_people/my_migrations contacts_and_people/migrations`
* `mv links/my_migrations links/migrations`
* `mv news_and_events/my_migrations news_and_events/migrations`
* `mv vacancies_and_studentships/my_migrations vacancies_and_studentships/migrations`
* `mv video/my_migrations video/migrations`

Now you should have:

* the new Arkestra models
* a set of migrations matching your database tables

Create migrations to get from your tables to the new models
===========================================================
Make sure you're in the project directory:

* `python manage.py schemamigration --auto arkestra_image_plugin`
* `python manage.py schemamigration --auto contacts_and_people`
* `python manage.py schemamigration --auto links`
* `python manage.py schemamigration --auto news_and_events`
* `python manage.py schemamigration --auto vacancies_and_studentships`
* `python manage.py schemamigration --auto video`

For any models where your previous version differed from the new, you'll now have a second migration to get from old to new.

Apply the new migrations
========================
It's always sensible to use --db-dry-run first to check:

* `python manage.py migrate --db-dry-run`

then if that seems ok:

* `python manage.py migrate`

Now your database tables and models are up-to-date!

Get back to the Arkestra codebase
=================================
Do this in the Arkestra directory - be warned, it will delete everything it finds there that wasn't in the branch you checked out :

* `git clean -dxf`

Clear out the migration records (again)
=======================================
Once again, find your south_migrationhistory table and clear out the relevant migration records. We're going to re-create these, so you need to:

* DELETE FROM `south_migrationhistory` WHERE `app_name`='arkestra_image_plugin'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='contacts_and_people'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='links'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='news_and_events'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='vacancies_and_studentships'; 
* DELETE FROM `south_migrationhistory` WHERE `app_name`='video'; 

Fake the migrations
===================
Back to the project directory:

* `python manage.py migrate --fake arkestra_image_plugin`
* `python manage.py migrate --fake contacts_and_people`
* `python manage.py migrate --fake links`
* `python manage.py migrate --fake news_and_events`
* `python manage.py migrate --fake video`

Finally, all the following should be in agreement with each other:

* models
* database tables
* migrations
* south's database records of applied migrations

Apply any newer migrations
==========================
At the moment, your code and database are up-to-date with the 2.0 release. But, things might have moved on since then. There could be new migrations in master, or another branch. 

So, in the Arkestra directory:

* `git checkout master` [or the branch you want]

Back to the project directory:
                     
* `python manage.py migrate`

And hopefully, that will be that!