Methods
=======

Entity
------
Each office, department, committee, centre within an institution is an Entity.
Entities are organised into a hierarchy, for example:

	The University
		Faculties
		    Faculty of Humanities
		        Department of Philosophy
		            Philosophy Examination Board


### Entity.gather_members()

For an entity, and all its descendants, produces a list of members (it returns a set).

### Entity.build_address()

Assembles the institutional (as opposed to postal) part of an entity's address.

The build_address function allows us to eliminate unnecessary or undesired lines from the ancestry for the purpose of constructing address. For example, "Cardiff University School of Medicine" does not need to show its parent ("Cardiff University") in its address - that would just look silly.

Also, we leave out abstract entities (e.g. "Faculties").

Person
------

### Person.gather_entities()

For a person, produces a list of entities that the person belongs to. It also includes all the descendants of these entities (if you belong to a child you belong to its parent). 


Templatetags
============

in *contacts_and_people_tags.py*

{% make_membership_tree person root %}
--------------------------------------

For a person, will list all the entities they belong to, whether explicitly or implicitly, and make a tree to display them in.

root is the starting point of the tree.

The easiest way to get root is by using MPTT's *get_root()*, as in:

	{% make_membership_tree entity.get_root %}

See http://www.jonathanbuchanan.plus.com/mptt/models.html for more on get_root().

make_membership_tree recurses - it uses the template entitytree.html, which in turn calls make_membership tree, until they run out of tree nodes to process.

{% find_entity_for_page page %}
-------------------------------



{% list_members_of_entity entity %}
-----------------------------------

For an entity, and all its descendants, produces a list of members. 

