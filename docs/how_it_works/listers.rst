=======
Listers
=======


How to create custom Lister and List classes
============================================

Create a List class
-------------------

Subclass ``arkestra_utilities.generic_lister.ArkestraGenericList``, and provide
the ``List``'s model::

    class PublicationsList(ArkestraGenericList):
        model = BibliographicRecord

You may need to add other attributes as required, for example::

    item_template = "publications/publications_list_item.html"

The ``List`` class's ``set_items_for_context`` method can be inherited from
``arkestra_utilities.generic_lister.ArkestraGenericList``. If it does, the
model must have a Manager class with a ``listable_objects()`` method. Either
way, it needs to set the ``items_for_context`` attribute.

When this list is displayed, should it provide links to other items?

::

    def other_items(self):
        other_items = []
        # test for the various other_item_kinds that might be needed here
        if "archived" in self.other_item_kinds:
            other_items.append({
                # where we'll find them
                "link": self.entity.get_auto_page_url("publications-archive"),
                # the link title
                "title": "Archived publications",
                # count them
                "count": self.items_for_context.count(),})
            })
        return other_items



Create a Lister class
=====================

A ``Lister`` needs to subclass ``arkestra_utilities.generic_lister.ArkestraGenericLister``. Attributes it must have:

* listkinds - the sets of items that we must calculate now
* display

Should the Lister provide information about the kinds of other items that
should be displayed in this context? For example, if this is the view of
current items and there's an archive, we might use::

    other_item_kinds = ("archived",)

Then we need to create our own ``other_items`` method::

