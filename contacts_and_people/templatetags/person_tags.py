from django import template
from django.shortcuts import render_to_response
from contacts_and_people.models import Membership
from cms.models import Page

register = template.Library()

@register.inclusion_tag('entitytrees.html', takes_context=True)
def membership_tree_roots(context, person):
    """
    Produces a list of tree roots. For each of these, uses make_membership_tree to display the entities in the tree that the person belongs to.
    """
    roots = set()
    for entity in person.entities.all(): # was Membership.objects.filter(person = person) - this seems simpler
        roots.add(entity.get_root())
    return {
        'roots': list(roots),
        'person': person,
    }

@register.inclusion_tag('entitytree.html')
def make_membership_tree(person, node):
    """
    Builds a tree representation of the entities that the person belongs to.
    
    This function recurses, by using the template entitytree.html which in turn calls this function
    
    This can certainly be made more efficient - it renders to the template far too many times
    """    
    if node in person.gather_entities():
        if not node.abstract_entity or node.is_root_node():
            node.display = True
        memberships = Membership.objects.filter(entity=node, person = person)
        roles = []
        for membership in memberships:   
            if membership.role:
                if membership.importance_to_person == 5:
                    node.home = True
                roles.append(membership.role)
                print "appending: " + str(membership.role)
        return {
            'node': node,
            'person': person,
            'roles': roles,
            }

@register.inclusion_tag('address.html', takes_context=True)
def address(context):
    """
    Publishes address for a person.
    """
    print " -------- person_tags.address --------"
    person = context.get('person')
    entity = person.get_entity()        
    address = entity.get_address()
    return {'address': address, 'entity': entity}
    
