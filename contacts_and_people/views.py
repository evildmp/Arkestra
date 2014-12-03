from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
import django.http as http
from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings

from links.link_functions import object_links
from arkestra_utilities.settings import PERSON_TABS
from models import Person, Building, Membership, Entity


applications = getattr(settings, 'INSTALLED_APPS')


def contacts_and_people(request, slug):
    slug = slug or getattr(Entity.objects.base_entity(), "slug", None)
    entity = get_object_or_404(Entity, slug=slug, external_url=None)

    # for the menu, because next we mess up the path
    request.auto_page_url = request.path

    # for the menu, so it knows where we are
    # request.path = entity.get_website.get_absolute_url()
    request.current_page = entity.get_website
    template = entity.get_template()

    # meta values - title and meta
    title = "Contact information for %s" % entity
    meta = {
        "description": """
            Addresses, phone numbers, staff lists and other contact information
            """,
        }

    people, initials = entity.get_people_and_initials()

    # only show pagetitle if there are people
    if people:
        pagetitle = u"Contacts & people"
    else:
        pagetitle = u""

    # are there Key People to show? show key roles, plus list
    if entity.get_key_people():
        people_list_heading = _(u"Also")
        # now remove the Key People from the people list
        people = [
            person for person in people if person not in set(
                [role.person for role in entity.get_key_people()]
            )
        ]
    else:  # otherwise, just a list of the people with roles
        people_list_heading = _(u"People")
    # convert the list of Persons into a list of Members
    people = entity.get_roles_for_members(people)
    search_fields = [
        {
            "field_name": "name",
            "field_label": "Name",
            "placeholder": "Surname or first name",
            "search_keys": [
                "given_name__icontains",
                "surname__icontains",
                ],
            },
        {
            "field_name": "role",
            "field_label": "Roles",
            "placeholder": "All roles",
            "search_keys": [
                "member_of__role__icontains",
                ]
            }
        ]

    people_qs = entity.get_people()
    search = False

    for search_field in search_fields:
        field_name = search_field["field_name"]
        if field_name in request.GET:
            query = request.GET[field_name]
            search_field["value"] = query
            if query:
                search = True

            q_object = Q()
            for search_key in search_field["search_keys"]:
                lookup = {search_key: query}
                q_object |= Q(**lookup)
            people_qs = people_qs.distinct().filter(q_object)

    if search:
        people_qs = entity.get_roles_for_members(people_qs)

    return render_to_response(
        # this is a catch-all template, that then uses includes to bring in
        # extra information
        "contacts_and_people/contacts_and_people.html",
        {
            "entity": entity,
            "pagetitle": pagetitle,
            "entity.website.template": template,
            "email": entity.email,
            "title": title,
            "meta": meta,
            "precise_location": entity.precise_location,
            "intro_page_placeholder": entity.contacts_page_intro,
            "phone": entity.phone_contacts.all(),
            "full_address": entity.get_full_address,
            "building": entity.get_building,
            "people": people,
            "people_list_heading": people_list_heading,
            "initials_list": initials,
            "search_fields": search_fields,
            "people_qs": people_qs,
            "search": search,
        },
        RequestContext(request),
        )


def people(
    request,
    slug=getattr(Entity.objects.base_entity(), "slug", None),
    letter=None
):
    """
    Responsible for lists of people
    """
    # general values needed to set up and construct the page and menus
    slug = slug or getattr(Entity.objects.base_entity(), "slug", None)
    entity = get_object_or_404(Entity, slug=slug, external_url=None)

    # for the menu, because next we mess up the path
    request.auto_page_url = entity.get_auto_page_url("contact-entity")

    # for the menu, so it knows where we are
    # request.path = entity.get_website.get_absolute_url()
    request.current_page = entity.get_website
    template = entity.get_template()
    generic_lister_template = "includes/people_list_with_index.html"

    # meta values - title and meta
    meta = {u"description": "People in %s" % entity}
    title = u"%s: people" % entity

    # content values
    people, initials = entity.get_people_and_initials()

    if letter:
        people = entity.get_people(letter)
        title = u"%s, people by surname: %s" % (entity, letter.upper())

    return render_to_response(
        "arkestra/entity_generic_lister_page.html",
        {
            "entity": entity,
            "pagetitle": entity,
            "entity.website.template": template,
            "generic_lister_template": generic_lister_template,

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
        {"entity": entity},
        RequestContext(request),
    )


def person(request, slug, active_tab=""):
    """
    Responsible for the person pages
    """
    # does this Person even exist?
    person = get_object_or_404(Person, slug=slug, active=True)

    meta = {}

    tabs = PERSON_TABS(person, active_tab)

    if active_tab:
        if active_tab not in tabs.live_tabs:
            raise Http404

        active_tab = "_" + tabs.live_tabs[active_tab]["tab"]
        meta = {"description": tabs.description}

    person.links = object_links(person)

    # we have a home_role, but we should also provide a role, even where it's
    # good enough to give us an address
    home_role = person.get_role

    if home_role:
        entity = home_role.entity
    # don't rely on home_role.entity - could be None or overridden
    entity = person.get_entity

    building = person.get_building

    email = person.get_email()
    phone = person.get_phone_contacts()

    # contact = person.get_please_contact()

    if person.please_contact:
        precise_location = None
    else:
        precise_location = person.precise_location
    access_note = person.access_note

    if home_role:
        description = ", ".join(
            (home_role.__unicode__(), entity.__unicode__())
        )
        request.current_page = entity.get_website
    else:
        description = Entity.objects.base_entity().__unicode__()
        request.current_page = Entity.objects.base_entity().get_website

    # if we don't have an active_tab, meta["description"] is ""
    meta.setdefault(
        "description", " ".join((person.__unicode__(), description))
        )

    if entity:
        template = entity.get_template()
    # no memberships, no useful information
    else:
        template = Entity.objects.base_entity().get_template()

    if tabs.tabs:
        if not active_tab:
            # find out what to add to the url for this tab
            active_tab = tabs.tabs[0]["address"]
            # mark the tab as active for the template
            tabs.tabs[0]["active"] = True
        # fewer than 2? not worth having tabs!
        if len(tabs.tabs) == 1:
            tabs.tabs = []

    # there's a problem here - pages such as Cardiff's
    # /person/dr-kathrine-jane-craig/ don't get the menu right - why?
    # print "****", request.auto_page_url, request.path, request.current_page,
    # entity.get_website

    return render_to_response(
        "contacts_and_people/person%s.html" % active_tab,
        {
            "person": person,  # personal information
            "home_role": home_role,  # entity and position
            "entity": entity,
            "template": template,  # from entity
            "building": building,
            "email": email,  # from person or please_contact
            "precise_location": precise_location,  # from person, or None
            "phone": phone,
            "full_address": person.get_full_address,
            "access_note": access_note,  # from person
            "tabs": tabs.tabs,
            "tab_object": person,
            "active_tab": active_tab,
            "meta": meta,
        },
        RequestContext(request),
    )


def place(request, slug, active_tab=""):
    """
    Receives active_tab from the slug.

    The template receives "_" + active_tab to identify the correct template
    (from includes).
    """
    place = get_object_or_404(Building, slug=slug)
    # information for each kind of place page
    tabs_dict = {
        "about": {
            "tab": "about",
            "title": "About",
            "address": "",
            "meta_description_content": place.summary,
        },
        "map": {
            "tab": "map",
            "title": "Map",
            "address": "map",
            "meta_description_content": "Map for " + place.__unicode__(),
        },
        "getting-here": {
            "tab": "getting-here",
            "title": "Getting here",
            "address": "getting-here",
            "meta_description_content": "How to get to " + place.__unicode__(),
        },
        "events": {
            "tab": "events",
            "title": "What's on here",
            "address": "events",
            "meta_description_content": "What's on at " + place.__unicode__(),
        },
    }

    if active_tab and not active_tab in tabs_dict:
        raise Http404

    # mark the active tab, if there is one
    if active_tab in tabs_dict:
        tabs_dict[active_tab]["active"] = True

    # add tabs to the list of tabs
    tabs = [tabs_dict["about"]]
    if place.has_map():
        tabs.append(tabs_dict["map"])
    if (
        place.getting_here and place.getting_here.cmsplugin_set.all()
        ) or (
        place.access_and_parking and
        place.access_and_parking.cmsplugin_set.all()
    ):
        tabs.append(tabs_dict["getting-here"])
    if place.events.lists:
        tabs.append(tabs_dict["events"])

    if not active_tab:
        # find out what to add to the url for this tab
        active_tab = tabs[0]["address"]
        # mark the tab as active for the template
        tabs[0]["active"] = True
    # fewer than 2? not worth having tabs!
    if len(tabs) == 1:
        tabs = []

    meta_description_content = tabs_dict[
        active_tab or "about"
        ]["meta_description_content"]

    if active_tab:
        active_tab = "_" + active_tab

    meta = {"description": meta_description_content}
    page = Entity.objects.base_entity().get_website
    request.current_page = page
    template = page.get_template()

    return render_to_response(
        "contacts_and_people/place%s.html" % active_tab,
        {
            "place": place,
            "tabs": tabs,
            "tab_object": place,
            "active_tab": active_tab,
            "template": template,
            "meta": meta,
        },
        RequestContext(request),
    )


def ajaxGetMembershipForPerson(request):
    # Which person was/is selected
    try:
        person_id = int(request.GET.get("person_id"))
    except ValueError:
        person_id = 0
    # If editing a current displayrole
    try:
        displayrole_id = int(request.GET.get("displayrole_id"))
    except ValueError:
        displayrole_id = 0
    # If editing a current membership
    try:
        membership_id = int(request.GET.get("membership_id"))
    except ValueError:
        membership_id = 0
    # Server response to AJAX
    response = http.HttpResponse()
    # BLANK option
    response.write('<option value="">---------</option>')
    # If valid person selected make <option> list of all their existing
    # memberships
    if (person_id > 0):
        membership_forperson_list = Membership.objects.filter(
            person__id=person_id
            ).order_by('entity__name')

        for membership in membership_forperson_list:
            # dont include this membership if it is the one we are editing
            if membership.id != membership_id:
                # add a SELECTED clause if this is the display_role that
                # was previously chosen
                if membership.id == displayrole_id:
                    is_selected = " selected "
                else:
                    is_selected = ""
                # return an <option> entry for that membership
                response.write(
                    '<option ' + is_selected + ' value="' +
                    unicode(membership.id) + '">' +
                    unicode(membership.entity) + ' - ' +
                    unicode(membership.role) + '</option>'
                    )

    return response
