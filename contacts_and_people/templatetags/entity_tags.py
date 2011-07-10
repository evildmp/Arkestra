from django import template
from contacts_and_people.models import Membership, Entity
#import DoesNotExistError

register = template.Library()

@register.inclusion_tag('directory.html', takes_context=True)
def directory(context, entity = None):
    entity = work_out_entity(context, entity)
    print entity.get_descendants()
    return { "entities": entity.get_descendants()}

@register.inclusion_tag('people.html', takes_context=True)
def key_people(context, entity = None):
    """
    Publishes an ordered list of memberships, grouped by people
    """
    entity = work_out_entity(context, entity)
    memberships = Membership.objects.filter(entity = entity, importance_to_entity_gte = 3).order_by('importance_to_entity',) 
    duplicates = set()
    membership_list = []
    for membership in memberships:
        if membership not in duplicates:
            duplicates.add(membership)
            membership_list.append(membership)
    # returns a list of memberships, in the right order - we use a regroup tag to group them by person in the template 
    # this doesn't list people's non-key-roles - should it?
    return {'membership_list': membership_list}

@register.inclusion_tag('includes/people_with_roles.html', takes_context=True)
def people_with_roles(context, letter = None):
    """
   For an Entity, returns a list of members who have roles. 
    """
    entity = work_out_entity(context, None)
    members = list(entity.get_people(letter))
    people = entity.get_roles_for_members(members)
    return {
        'entity' : entity,
        'people': people,
    }  

# think we need some error checking here, in case we get to the last ancestor page without having found an entity
def entity_for_page(page):
    """
    Given a page, returns the entity that has selected the page as its website.
    If the page doesn't have an entity attached to it, will try for the page's parent, and so on.
    """
    if page:
        try:
            return page.entity.get() # return the entity associated with that page
        except Entity.DoesNotExist: # page didn't have an entity
            return entity_for_page(page.parent)
    else:
        return None

# this ought to be a context processor, maybe
def work_out_entity(context,entity):
    """
    One of Arkestra's core functions
    """
    # first, try to get the entity from the context
    entity = context.get('entity', None)
    if not entity:
        # otherwise, see if we can get it from a cms page
        request = context['request']
        if request.current_page:
            entity = entity_for_page(request.current_page)
        else: # we must be in a plugin, either in the page or in admin
            page = context['plugin'].get("page", None)
            if page:
                entity = entity_for_page(page)
            else:
                entity = None
    return entity
