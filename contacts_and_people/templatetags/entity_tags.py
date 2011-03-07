from django import template
from django.db.models import Q
from django.shortcuts import render_to_response
from contacts_and_people.models import Membership, Entity
from cms.models import Page
import operator
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

@register.inclusion_tag('people_all.html', takes_context=True)
def all_people_with_roles(context, letter = None):
    """
   For an Entity, returns a list of members who have roles. 
   
   This is very slow and inefficient.
    """
    entity = work_out_entity(context, None)
    print "I am working out the members for:", entity
    members = list(entity.get_people(letter))
    #members.sort(key=operator.attrgetter('surname', 'given_name', 'middle_names'))
    member_list = []
    print "... there are", len(member_list), "members"
    for member in members:
        print "Person:", member
        memberships = []
        ms = Membership.objects.filter(person = member)
        print "... has", len(ms), "memberships"        
        # get the best named membership in the entity
        named_memberships = list(ms.filter(entity=entity).exclude(role ="").order_by('-importance_to_person'))
        if named_memberships:
            member.membership = named_memberships[0]
            print "... and she has a specified role here, the best of which is", member.membership
        else:            
            # see if there's a display_role membership - actually this one should go first
            display_role_memberships = list(ms.filter(entity=entity).exclude(display_role = None).order_by('-importance_to_person',)) 
            if display_role_memberships:
                member.membership = display_role_memberships[0].display_role
                print "... she doesn't have a specified role in this enitity, but does have a display_role, which is", member.membership
            else:                 
                # find the best named membership anywhere we can
                best_named_membership = list(ms.exclude(role = "").order_by('-importance_to_person',)) 
                if best_named_membership:
                    member.membership = best_named_membership[0]
                    print "... she doesn't have a role here, or a display_role, but the very best membership is", member.membership
                else:                        
                    # add the unnamed membership for this entity - it's all we have
                    unnamed_memberships = list(ms.order_by('-importance_to_person',)) 
                    member.membership = unnamed_memberships[0]
                    print "... I didn't find any named memberships for", member                    
    return {
        'entity' : entity,
        'membership_list': members
            }  


# think we need some error checking here, in case we get to the last ancestor page without having found an entity
def entity_for_page(page):
    """
    Given a page, returns the entity that has selected the page as its website.
    If the page doesn't have an entity attached to it, will try for the page's parent, and so on.
    """
    print "entity_for_page()"
    try:
        return page.entity.get() # what on earth is this?
    except Entity.DoesNotExist: # this is very bad: we don't know what the exception is
        return entity_for_page(page.parent)

# this ought to be a context processor
def work_out_entity(context,entity):
    """
    One of Arkestra's core functions
    """
    # first, try to get the entity from the context
    entity = context.get('entity', None)
    print "> entity from context: ", entity
    if not entity:
        # otherwise, see if we can get it from a cms page
        request = context['request']
        if request.current_page:
            print "We're in a page"
            entity = entity_for_page(request.current_page)
            print "> entity from page: ", entity
        else: # we must be in a plugin, either in the page or in admin
            print "We're in a plugin"
            print context['plugin']
            page = context['plugin'].get("page", None)
            if page:
                entity = entity_for_page(page)
            else:
                entity = None
            print "> entity from plugin: ", entity
    return entity


"""
def members_for_entity(entity): # is this actually used anywhere - yes

looks like this can be eplaced by the much simpler:

people = Person.objects.filter(member_of__entity__in = self.get_descendants(include_self = True)).distinct().order_by('surname', 'given_name', 'middle_names')

    memberlist = set()
    for descendant_entity in entity.get_descendants(include_self = True):
        memberlist.update(descendant_entity.people.all())
    return memberlist
    
def real_ancestor(entity): # what on earth is this for?
    for ancestor in entity.get_ancestors(ascending = True):
        if not ancestor.abstract_entity:
            entity = ancestor
            break    
    return entity
"""
