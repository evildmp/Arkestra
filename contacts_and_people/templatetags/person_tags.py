from django import template
from contacts_and_people.models import Membership

register = template.Library()

@register.inclusion_tag('entitytrees.html', takes_context=True)
def membership_tree_roots(context, person):
    """
    Produces a list of tree roots. For each of these, uses
    make_membership_tree to display the entities in the tree that the person
    belongs to.
    """
    roots = set()
    for entity in person.entities.all():
        # get the closest-to-root non-abstract entity
        if entity.get_ancestors().filter(abstract_entity = False):
            roots.add(entity.get_ancestors().filter()[0])
        # or this entity, if it's not an abstract entity
        elif not entity.abstract_entity:
            roots.add(entity)
            
    return {
        'roots': list(roots),
        'person': person,
    }

@register.inclusion_tag('entitytree.html')
def make_membership_tree(person, node):
    """
    Builds a tree representation of the entities that the person belongs to.
    
    This function recurses, by using the template entitytree.html which in turn
    calls this function
    
    This can certainly be made more efficient - it renders to the template far
    too many times
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
        return {
            'node': node,
            'person': person,
            'roles': roles,
        }
