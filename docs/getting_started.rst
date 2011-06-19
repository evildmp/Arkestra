###############
Getting Started
###############

In order to make anything work, you'll need to do log in to Admin and do three things.

* create a Page
* create an Entity
* link the Entity to the Page, by selecting the Page as the Entity's /Home page/

And since Arkestra needs to know what the *base entity* of your site is, in your ``arkestra_settings`` file add something like::

ARKESTRA_BASE_ENTITY = 1

where the value corresponds to the id of your base entity.