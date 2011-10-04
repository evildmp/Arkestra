import django.http as http
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from models import Person, Building, Membership, Entity, default_entity
from links.link_functions import object_links

from django.conf import settings

applications = getattr(settings, 'INSTALLED_APPS')

if 'publications' in applications:
    from publications.models import BibliographicRecord
    from publications.models import Researcher # required for publications

def contacts_and_people(request, slug=getattr(default_entity, "slug", None)):
    # general values needed to set up and construct the page and menus
    entity = Entity.objects.get(slug=slug)
    # for the menu, because next we mess up the path
    request.page_path = request.path
    request.path = entity.get_website().get_absolute_url()
    template = entity.get_template()
    main_page_body_file = "contacts_and_people/entity_contacts_and_people.html"

    # meta values - title and meta
    title = "Contact information for %s" % entity
    meta = {
        "description": "Addresses, phone numbers, staff lists and other contact information",
        }
        
    people, initials = entity.get_people_and_initials()
    # are there Key People to show?    
    if entity.get_key_people(): # if so we will show a list of people with key roles, then a list of other people
        people_list_heading = "All other people"
        # now remove the Key People from the people list
        people = [ person for person in people if person not in set([role.person for role in entity.get_key_people()])]
    else: # otherwise, just a list of the people with roles
        people_list_heading = "People"
    people = entity.get_roles_for_members(people) # convert the list of Persons into a list of Members

    return render_to_response(
        "contacts_and_people/entity_information.html", # this is a catch-all template, that then uses includes to bring in extra information
        {
            "entity":entity,
            "pagetitle": entity,
            "entity.website.template": template,
            "main_page_body_file": main_page_body_file,
            "email": entity.email,
            "title": title,
            "meta": meta,
            "location": entity.precise_location, 
            "intro_page_placeholder": entity.contacts_page_intro,

            "people": people,
            "people_list_heading": people_list_heading,
            "initials_list": initials,
        },
        RequestContext(request),
        )        

def people(request, slug, letter=None):
    """
    Responsible for lists of people
    """
    # general values - entity, request, template
    entity = Entity.objects.get(slug=slug)
    request.page_path = request.path # for the menu, because next we mess up the path
    request.path = entity.get_website().get_absolute_url()
    template = entity.get_template()
    main_page_body_file = "includes/people_list_with_index.html"
    # meta values - title and meta
    meta = {
        "description": "People in %s" % entity,
        }
    title = "%s: people" % entity
    # content values
    people, initials = entity.get_people_and_initials()
    if letter:
        people = entity.get_people(letter)
        title = "%s, people by surname: %s" % (entity, letter.upper())
    return render_to_response(
        "contacts_and_people/entity_information.html",
        {
            "entity":entity,
            "pagetitle": entity,
            "entity.website.template": template,
            "main_page_body_file": main_page_body_file,

            "title": title,
            "meta": meta,

            "people": people,
            "initials_list": initials,
            "letter": letter,
        },
        RequestContext(request),
    )

def publications(request, slug):
    entity = Entity.objects.get(slug=slug)
    request.current_page = entity.website
    return render_to_response(
        "contacts_and_people/publications.html",
        {"entity":entity,},
        RequestContext(request),
    )        

def person(request, slug, active_tab=""):
    """
    Responsible for the person pages
    """
    person = get_object_or_404(Person,slug=slug)
    links = object_links(person)
    # we have a home_role, but we should also provide a role, even where it's good enough to give us an address
    home_role = person.get_role()
    if home_role:
        entity = home_role.entity
    entity = person.get_entity() # don't rely on home_role.entity - could be None or overridden
    # address = person.get_address()
   
    contact = person.get_please_contact()
    email = contact.email
    phone = contact.phone_contacts

    if person.override_entity or person.please_contact:
        location = None
    else:
        location = person.precise_location
    access_note = person.access_note
        
    if home_role:
        description = ", ".join((home_role.__unicode__(), entity.__unicode__()))
        request.current_page = entity.get_website() 
    else:
        description = default_entity.__unicode__()
        request.current_page = default_entity.get_website()

    meta = {
        "description": ": ".join((person.__unicode__(), description))
    }
    
    if entity:
        template = entity.get_template() 
    else: # no memberships, no useful information
        print "no memberships, no useful information"
        template = default_entity.get_template()

    tabs = []
    if 'publications' in applications:
        try:
            if person.researcher and person.researcher.publishes:
                tabs.extend(("research","publications"))
        except Researcher.DoesNotExist:
            pass

    return render_to_response(
        "contacts_and_people/persondetails" + str(active_tab) + ".html",
        {
            "person":person, # personal information
            "home_role": home_role, # entity and position
            "entity": entity,
            "template": template, # from entity
            # "address": address, # from entity
            "email": email, # from person or please_contact
            "location": location, # from person, or None 
            "contact": contact, # from person or please_contact
            "phone": phone,
            "access_note": access_note, # from person
            "tabs": tabs,
            "active_tab": active_tab,
            "meta": meta,
            "links": links,
        },
        RequestContext(request),
    )

def place(request, slug, active_tab=""):
    """
    Receives active_tab from the slug.
    
    The template receives "_" + active_tab to identify the correct template (from includes).
    """
    place = Building.objects.get(slug=slug)
    places_dict = { # information for each kind of place page
        "about": {
            "title": "About",
            "address": "",
            "meta_description_content": place.summary,
        },
        "directions": {
            "title": "Directions etc.",
            "address": "directions",
            "meta_description_content": "How to get to " + place.get_name(),
        },
        "events": {
            "title": "What's on",
            "address": "events",
            "meta_description_content": "What's on at " + place.get_name(),
        },
    }
    # mark the active tab (no active_tab must be "about")
    places_dict[active_tab or "about"]["active"] = True
    tabs = []
    if place.events().forthcoming_events:
        tabs.append(places_dict["events"])  
    print place.getting_here.cmsplugin_set.all() , place.access_and_parking.cmsplugin_set.all() , place.has_map
    if place.getting_here.cmsplugin_set.all() or place.access_and_parking.cmsplugin_set.all() or place.has_map:
        tabs.append(places_dict["directions"])
    # if we're going to show tabs, put the about tab first
    if tabs:
        tabs.insert(0, places_dict["about"])
    meta_description_content = places_dict[active_tab or "about"]["meta_description_content"] 
    if active_tab:
        active_tab = "_" + active_tab
    meta = {
        "description": meta_description_content,
        }
    if default_entity:
        page =  default_entity.get_website()
        request.current_page = page
        template = page.get_template()
    else:
        page =  entity.get_website()
        request.current_page = page # for the menu, so it knows where we are
        template = page.get_template()
        
    return render_to_response(
        "contacts_and_people/place%s.html" % active_tab,
        {
        "place":place,
        "tabs": tabs,
        "active_tab": active_tab,
        "template": template,
        "meta": meta,
        },
        RequestContext(request),        )
        
        
def ajaxGetMembershipForPerson(request):
    #Which person was/is selected
    try:
        person_id = int( request.GET.get("person_id") )
    except ValueError:
        person_id = 0
    #If editing a current displayrole
    try:
        displayrole_id = int( request.GET.get("displayrole_id") )
    except ValueError:
        displayrole_id = 0      
    #If editing a current membership
    try:
        membership_id = int( request.GET.get("membership_id") )
    except ValueError:
        membership_id = 0
    #Server response to AJAX
    response = http.HttpResponse()
    #BLANK option
    response.write ('<option value="">---------</option>')
    #If valid person selected make <option> list of all their existing memberships
    if (person_id > 0 ):
        membership_forperson_list = Membership.objects.filter(person__id = person_id).order_by('entity__name')
        for membership in membership_forperson_list:
            #dont include this membership if it is the one we are editing
            if membership.id != membership_id:
                #add a SELECTED clause if this is the display_role that was previously chosen
                if membership.id == displayrole_id:
                    is_selected = " selected "
                else:
                    is_selected = ""
                #return an <option> entry for that membership
                response.write('<option ' + is_selected + ' value="' + str(membership.id) + '">' + \
                                     str(membership.entity) + ' - ' + str(membership.role) + \
                                 '</option>')
    #Done
    return response        