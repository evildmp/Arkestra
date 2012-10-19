import logging

#app = contacts_and_people
from django.db import models
from django.db.utils import DatabaseError
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.conf import settings

from cms.models import Page, CMSPlugin
from cms.models.fields import PlaceholderField

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
# import mptt

from filer.fields.image import FilerImageField

# from news_and_events.models import NewsAndEventsPlugin
# from news_and_events.cms_plugins import CMSNewsAndEventsPlugin

from arkestra_utilities.mixins import URLModelMixin
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE, ARKESTRA_BASE_ENTITY, DEFAULT_NEWS_PAGE_TITLE, DEFAULT_CONTACTS_PAGE_TITLE, DEFAULT_VACANCIES_PAGE_TITLE, DEFAULT_PUBLICATIONS_PAGE_TITLE
from links.models import ExternalLink

import news_and_events

base_entity_id = ARKESTRA_BASE_ENTITY

# Page = models.get_model('cms', 'Page')
# CMSPlugin = models.get_model('cms', 'CMSPlugin')

class Site(models.Model):
    """Maintains a list of an institution's geographical sites"""
    site_name = models.CharField(max_length=50, unique=True)
    post_town = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)
    
    class Meta:
        ordering = ('country','site_name', 'post_town',)
    
    def __unicode__(self):
        return self.site_name

    @property
    def maps(self):
        # return self.building_set.filter(has_map = True)
        return [building for building in self.building_set.all() if building.has_map]
         
class BuildingManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

class Building(models.Model):
    """Each Building is on a Site."""
    objects=BuildingManager()
    name = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=10, null=True, blank=True)
    street = models.CharField("Street name", max_length=100, null = True, blank=True)
    additional_street_address = models.CharField(help_text=u"If required",
        max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=9, null=True, blank=True)
    site = models.ForeignKey(Site, related_name="place")
    slug = models.SlugField(blank=True, help_text=u"Please leave blank/amend only if required", 
        max_length=255, null=True, unique=True)
    image = FilerImageField(null=True, blank=True)
    # for the place page
    summary =  models.TextField(verbose_name="Summary", max_length=256, default ="",
        help_text="A very short description of this building (maximum two lines)",)
    description = PlaceholderField('body', related_name="building_description",
        help_text="A fuller description",)
    getting_here = PlaceholderField('simple', 
        related_name="getting_here",
        help_text="How to get here",)
    access_and_parking = PlaceholderField('simple', 
        related_name="building_access_and_parking",
        help_text="Where to park, how to get in, etc")
    map = models.BooleanField("Show map", default=False, help_text = "Use Google Maps to <a target='_blank' style='text-decoration: underline;'  href='http://universimmedia.pagesperso-orange.fr/geo/loc.htm'>look up Latitude & Longitude</a>")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    zoom = models.IntegerField(blank=True, null=True, default=17)
    
    class Meta:
        ordering = ('site', 'street', 'number', 'name',)
    
    # def natural_key(self):
    #     return (self.slug)

    def __unicode__(self):
        if self.name:
            building_identifier = unicode(self.site) + ": " + self.name
        elif self.street:
            building_identifier = unicode(self.site) + ": " + self.number + " " + self.street
        else:
            building_identifier = unicode(self.site) + ": " + self.postcode
        return building_identifier
    
    def get_absolute_url(self):
        return "/place/%s/" % self.slug
    
    def save(self):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.__unicode__())
        super(Building, self).save()
    
    def get_name(self):
        """
        Assembles a half-decent name for a building
        """
        if self.name:
            building_identifier = self.name
        elif self.street:
            building_identifier = self.number + " " + self.street
        else:
            building_identifier = unicode(self.site) + ": " + self.postcode
        return building_identifier
    
    @property
    def get_postal_address(self):
        """
        Assembles the postal (external) parts of an address
        """
        # print "getting postal address"
        address = []
        if self.name:
            address.append(self.name)
        if self.number:
            address.append(self.number + " " + self.street) # because building numbers and street names go on the same line
        elif self.street:
            address.append(self.street)
        if self.additional_street_address:
            address.append(self.additional_street_address)
        if self.site.post_town:
            address.append(" ".join((item for item in (self.site.post_town, self.postcode) if item)))
        elif self.postcode:
            address.append(self.postcode)
        return address

    @property
    def has_map(self):
        return self.map and self.latitude and self.longitude and self.zoom
    
    def events(self):
        # invoke the plugin to find out more
        instance = news_and_events.models.NewsAndEventsPlugin()
        instance.display = "events"
        instance.type = "for_place"
        instance.place = self
        instance.view = "current"
        instance.format = "details image"
        instance.order_by = "date"
        
        # create an instance of the plugin to see if the menu should have items
        plugin = news_and_events.cms_plugins.CMSNewsAndEventsPlugin()   
        plugin.get_items(instance)
        plugin.add_links_to_other_items(instance)    
        # plugin.set_image_format(instance)
        plugin.set_limits_and_indexes(instance)
        instance.lists = plugin.lists
        return instance

    @property
    def get_website(self):
        return None
        
class PhoneContact(models.Model):
    LABEL_CHOICES = ( ('','-----'),
                    ('Office', 'Office'),
                    ('Laboratory', 'Laboratory'),
                    ('Mobile','Mobile'),
                    ('Fax', 'Fax'),
                    ('Out of hours','Out of hours'),
                    ('Pager','Pager'),
                    )
    label = models.CharField(max_length=64, null=True, blank=True)
    country_code = models.CharField(max_length=5, default="44")
    area_code = models.CharField(max_length=5, default="029", help_text="Not 02920")
    number = models.CharField(max_length=12)
    internal_extension = models.CharField(max_length=6, null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(db_index=True)
    content_object = generic.GenericForeignKey()
    
    class Meta:
        ordering = ('label',)
        
    def __unicode__(self):
        return u"%s: %s" % (self.label, self.number)

        
class CommonFields(URLModelMixin):
    precise_location = models.CharField(help_text=u"Precise location <em>within</em> the building, for visitors",
        max_length=255, null=True, blank=True)
    access_note = models.CharField(help_text = u"Notes on access/visiting hours/etc",
        max_length=255, null=True, blank=True)
    email = models.EmailField(verbose_name="Email address", null=True, blank=True)
    phone_contacts = generic.GenericRelation(PhoneContact)
    image = FilerImageField(null=True, blank=True)
    
    class Meta:
        abstract = True
    

class EntityLite(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. Department of Haematology")
    
    def __unicode__(self):
        return unicode(self.name)


class EntityManager(TreeManager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def base_entity(self):
        try:
            # are Entities available at all?
            list(Entity.objects.all())
            # print "** Entity objects are available from the database"
        except:
            # no - the database isn't ready 
            # print "** Entity objects are not available from the database"
            pass      
        else:
            # we managed to get Entity.objects.all()
            # we don't use default_entity (or default_entity_id) in MULTIPLE_ENTITY_MODE
            try:
                entity = Entity.objects.get(id = base_entity_id)
            # it can't be found, maybe because of a misconfiguation or because we haven't added any Entities yet 
            except (Entity.DoesNotExist, DatabaseError), e:
                # print "** Either the Entity does not exist, or I got a DatabaseError:"
                # print "**", e
                pass
            else:
                # print "** I successfully found a default entity:", entity
                return entity

class Entity(MPTTModel, EntityLite, CommonFields):
    objects=EntityManager()
    short_name = models.CharField(blank=True, help_text="e.g. Haematology",
        max_length=100, null=True, verbose_name="Short name for menus")
    abstract_entity = models.BooleanField("Abstract entity", default=False,
        help_text=u"Select if this <em>group</em> of entities, but not an entity itself, or if it's just a grouping of people",)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    display_parent = models.BooleanField(u"Include parent entity's name in address", default=True, help_text=u"Deselect if this entity recapitulates its parent's name")
    building_recapitulates_entity_name = models.BooleanField(default=False, 
        help_text=u"Removes the first line of the address - use to avoid, for example:<br /><em>Department of Haematology<br />Haematology Building<br />...</em>")
    building = models.ForeignKey(Building, null=True, blank=True, on_delete=models.SET_NULL,
        help_text=u"Select the place where this Entity is based",)                      
    website = models.ForeignKey(Page, verbose_name="Home page",
        related_name='entity', unique=True, null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text=u"Select the Page that is the home page of this Entity (leave blank if this is an external Entity)",)
    
    auto_news_page = models.BooleanField(u"Publish a news & events page for this entity automatcally",
        default=False,
        )
    news_page_menu_title = models.CharField(u"Title",
        max_length= 50,
        default = DEFAULT_NEWS_PAGE_TITLE
        )
    news_page_intro = PlaceholderField('body', 
        related_name="news_page_intro",
        )

    auto_contacts_page = models.BooleanField(u"Publish a contacts & people page for this entity automatcally",default=False,
        )
    contacts_page_menu_title = models.CharField(u"Title",
        max_length=50,
        default = DEFAULT_CONTACTS_PAGE_TITLE,
        )
    contacts_page_intro = PlaceholderField('body',
        related_name="contacts_page_intro",
        help_text = "Text for the Contacts & people page"
        )
    
    auto_vacancies_page = models.BooleanField(u"Publish a vacancies & studentships page for this entity automatcally",
        default=False,
        )
    vacancies_page_menu_title = models.CharField(u"Title",
        max_length=50,
        default = DEFAULT_VACANCIES_PAGE_TITLE,
        )
    vacancies_page_intro = PlaceholderField('body',
        related_name="vacancies_page_intro",
        )
        
    if 'publications' in settings.INSTALLED_APPS:
        auto_publications_page = models.BooleanField(u"Publish a publications page for this entity automatcally",
            default=False)
        publications_page_menu_title = models.CharField(u"Title",
            max_length=50,
            default = DEFAULT_PUBLICATIONS_PAGE_TITLE,
            )
    
    class Meta:
        verbose_name_plural = "Entities"
        ordering = ['tree_id', 'lft']

    # def natural_key(self):
    #     return (self.slug)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        elif self.get_website:
            return "/contact/%s/" % self.slug
        else:
            return "/contact/"

    @property
    def _get_real_ancestor(self):
        """
        Find the nearest non-abstract Entity amongst this Entity's ancestors
        """
        for ancestor in self.get_ancestors(ascending = True):
            if not ancestor.abstract_entity:
                return ancestor
                
    @property
    def get_building(self):
        """
        Return the Building for this Entity (or its nearest parent) 
        """   
        if self.abstract_entity:
            return
        elif self.building:
            return self.building
        else:
            try: 
                return self._get_real_ancestor.get_building
            except AttributeError: 
                return None

    @property
    def _get_institutional_address(self):
        """
        Lists the parts of an address within the institution (Section of YYY, Department of XXX and YYY, School of ZZZ)
        """ 
        if self.abstract_entity:
            return
        else:
            ancestors = []
            showparent = self.display_parent
            for entity in self.get_ancestors(ascending = True).exclude(abstract_entity = True):
                if showparent:
                    ancestors.append(entity)
                showparent = entity.display_parent
            return ancestors

    @property
    def get_full_address(self):
        """
        Returns the full address of the entity
        """
        if self.abstract_entity:
            return []
        else:
            address = self._get_institutional_address
            building = self.get_building
            if building:
                if self.building_recapitulates_entity_name: 
                    address.extend(building.get_postal_address[1:])
                else:
                    address.extend(building.get_postal_address)
                return address
                

    @property
    def get_website(self):
        """
        Return the Django CMS page that this Entity has attached to it (or to its nearest parent)
        """
        if self.website:
            return self.website
        else:
            try:
                return self.parent.get_website
            except AttributeError: # I think this is right                
                return None

    def get_website_url(self):
        """
        Return the Django CMS page's url that this Entity has attached to it (or to its nearest parent)
        """
        if self.website:
            return self.website.get_absolute_url()
        elif self.external_url:
            return self.external_url.url
        elif self.parent:
            # try
            return self.parent.get_website_url()
        else:    # except
            return default_entity.get_website

    def get_related_info_page_url(self, kind):
        """
        Returns a URL not for the entity, but for its /contact page, /news-and-events, or whatever.
        
        If the entity is the base entity, doesn't add the entity slug to the URL
        """
        if self.external_url:
            return ""
        elif self == default_entity:
            return "/%s/" % kind
        else:
            return "/%s/%s/" % (kind, self.slug)

    def get_template(self):
        """
        Returns a template for any pages that need to render based on this entity
        """
        if self.get_website:
            return self.get_website.get_template()
        else:
            return default_entity.get_website.get_template()


    def get_contacts(self):
        """
        Return designated contacts for the entity
        """
        contacts = Membership.objects.filter(entity = self, key_contact = True).order_by('importance_to_entity')
        return contacts

    def get_people_with_roles(self, key_members_only = False):   
        """
        Publishes an ordered list of key members grouped by their most significant roles in the entity
        
        Ranks roles by importance to entity, then gathers people under that role
        
        Optionally, will return *all* members with roles
        """
        memberships = Membership.objects.filter(entity = self).exclude(role ="").order_by('-importance_to_entity','person__surname',) 
        if key_members_only:
            memberships = memberships.filter(importance_to_entity__gte = 3)
        # create a set with which to check for duplicates
        duplicates = set()
        membership_list = []
        for membership in memberships:
            # if this is the first time we've seen this role...
            if membership.role not in duplicates:
                # put this role on the duplicates list for future reference, and add everyone with that role to the membership_list
                duplicates.add(membership.role)
                membership_list.extend(memberships.filter(role = membership.role))
        # returns a list of memberships, in the right order - we use a regroup tag to group them by person in the template    
        return membership_list

    def get_key_people(self):
        return self.get_people_with_roles(key_members_only = True)

    def get_roles_for_members(self, members):
        """
        Given a list of its members (as Persons), returns the best role for each.
    
        The roles returned are in alphabetical order by Person.
        """
        for member in members:
            ms = Membership.objects.filter(person = member)
            # get the best named membership in the entity
            named_memberships = list(ms.filter(entity=self).exclude(role ="").order_by('-importance_to_person'))
            if named_memberships:
                member.membership = named_memberships[0]
            else:            
                # see if there's a display_role membership - actually this one should go first
                display_role_memberships = list(ms.filter(entity=self).exclude(display_role = None).order_by('-importance_to_person',)) 
                if display_role_memberships:
                    member.membership = display_role_memberships[0].display_role
                else:                 
                    # find the best named membership anywhere we can
                    best_named_membership = list(ms.exclude(role = "").order_by('-importance_to_person',)) 
                    if best_named_membership:
                        member.membership = best_named_membership[0]
                    else:                        
                        # add the unnamed membership for this entity - it's all we have
                        unnamed_memberships = list(ms.order_by('-importance_to_person',)) 
                        member.membership = unnamed_memberships[0]
        return members

    def get_people(self, letter = None):
        """
        Publishes a list of every member, and of every member of all children
        """
        if letter:
            people = Person.objects.filter(member_of__entity__in = self.get_descendants(include_self = True), surname__istartswith = letter).distinct().order_by('surname', 'given_name', 'middle_names')
        else:    
            people = Person.objects.filter(member_of__entity__in = self.get_descendants(include_self = True)).distinct().order_by('surname', 'given_name', 'middle_names')
        return people

    def get_people_and_initials(self, letter = None):
        """
        Returns a list of people and/or their initials for use in people lists
        
        More than 20 people, or a letter was provided? Return initials
        Fewer than 20 people? Return the people
        """
        people = self.get_people(letter)
        # letter or long list? show initials
        if letter or len(people) > 20:
            initials = set(person.surname[0].upper() for person in people)
            initials = list(initials)
            initials.sort()
            # no letter but list is long? initials only
            if not letter:
                people = []
        # no letter, short list? don't show initials
        else:
            initials = None
        return (people, initials)



class Title(models.Model):
    title = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=20, unique=True)
    
    class Meta:
        ordering = ['title',]
    
    def __unicode__(self):
        return self.abbreviation


class PersonLite(models.Model):
    title = models.ForeignKey('contacts_and_people.Title', 
        to_field="abbreviation", blank=True, null=True, on_delete=models.SET_NULL)
    given_name = models.CharField(max_length=50, blank=True, null=True)
    middle_names = models.CharField(max_length=100, blank=True, null=True)
    surname = models.CharField(max_length=50)
    
    def __unicode__(self):
        # TODO: make it smarter, i.e. don't include empty/None strings
        return u"%s %s %s" % (self.given_name, self.middle_names, self.surname)
    
    def __getInitials(self):
        if self.given_name <> '' and self.middle_names <> '':
            return self.given_name[0] + '.' + self.middle_names[0] + '.'
        elif self.given_name <> '':
            return self.given_name[0] + '.'
        else:
            return ''
    initials = property(__getInitials,)     


class PersonManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Person(PersonLite, CommonFields):
    objects=PersonManager()
    user = models.ForeignKey(User, related_name='person_user', unique=True,
        blank=True, null=True, verbose_name='Arkestra User', on_delete=models.SET_NULL)
    institutional_username = models.CharField(max_length=10, blank=True, null=True)
    active = models.BooleanField(default=True,)
    description = PlaceholderField('body')
    entities = models.ManyToManyField(Entity, related_name='people',
        through='Membership', blank=True, null=True)
    building = models.ForeignKey(Building, verbose_name='Specify building',
        help_text=u"<strong>Only</strong> required if this Person's <strong>Home entity</strong> has a different address", 
        blank=True, null=True, on_delete=models.SET_NULL)
    override_entity = models.ForeignKey(Entity, verbose_name='Specify entity',
        help_text=u"<strong>Temporarily specify</strong> an entity for contact information - over-rides entity and postal address",
        related_name='people_override', blank=True, null=True, on_delete=models.SET_NULL)
    please_contact = models.ForeignKey('self', help_text=u"Publish another person's details as contact information for this person",
        related_name='contact_for', blank=True, null=True, on_delete=models.SET_NULL)
    staff_id = models.CharField(null=True, blank=True, max_length=20)
    data_feed_locked = models.BooleanField(default=False)
    
    # def natural_key(self):
    #     return (self.slug)

    class Meta:
        ordering = ['surname', 'given_name', 'user',]
        verbose_name_plural = "People"

    def __unicode__(self):
        title = self.title or ""
        return u" ".join(name_part for name_part in [unicode(title), self.given_name, self.surname] if name_part)

    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/person/%s/" % self.slug

    @property
    def get_role(self):
        """
        Returns a Membership object.
        
        Works the Membership object representing a Person's best role, which
        has to be in a real, not abstract, entity, and it must be at least 
        Significant (gte = 2) to the person
        
        If it can't find any role, it returns None.
        """
        memberships = Membership.objects.filter(
            person = self, 
            entity__abstract_entity = False, 
            importance_to_person__gte = 2).order_by('-importance_to_person'
            )
        if memberships:
            return memberships[0]
        else: # the poor person had no memberships
            return None
            
    @property
    def get_entity(self):
        """
        Works out a person's best entity, based on get_role
        
        A person needs at least a named role to have an entity.
        """
        if self.override_entity and not self.override_entity.abstract_entity:
            return self.override_entity
        elif self.get_role:
            return self.get_role.entity
        return None
                
    @property
    def get_building(self):
        """
        Returns a Person's Building, if possible
        """
        if self.building:
            return self.building
        elif self.get_entity:
            return self.get_entity.get_building

    @property
    def get_full_address(self):
        """
        Works out a person's address, based on their home/best entity or information that overrides this
        """
        if self.get_entity: # needs an entity to work
            if self.building:
                address = self.get_entity._get_institutional_address
                address.extend(self.building.get_postal_address)
                return address
            else:
                return self.get_entity.get_full_address
        else:
            return []


    def get_please_contact(self):
        """
        Works out whether to display someone else's contact details
        """
        if self.please_contact:
            return self.please_contact.get_please_contact()
        else:
            return self

    @property
    def real_entities(self):
        # returns non-abstract entities the person belongs to
        return Membership.objects.filter(person=self, entity__abstract_entity = False)
    
    
    def gather_entities(self):
        """
        Returns all the entities that a person belongs to, including implicit membership
        """
        entitylist = set()
        for entity in self.entities.all():
            entitylist.add(entity)
            entitylist.update(entity.get_ancestors())
        return entitylist #set(entity for entity in entitylist if not entity.abstract_entity)
    
    def check_please_contact_has_loop(self, compare_to, person_list=None):
        if person_list==None:
            person_list=[compare_to]
        if not self==compare_to:
            person_list.append(self)
        if self.please_contact:
            if compare_to==self.please_contact:
                person_list.append(compare_to)
                return True, person_list
            else:
                return self.please_contact.check_please_contact_has_loop(compare_to, person_list)
        else:
            return False, person_list  
    def save(self, *args, **kwargs):
        do_check_please_contact_loop = kwargs.pop('do_check_please_contact_loop', True)
        if do_check_please_contact_loop and self.check_please_contact_has_loop(compare_to=self)==True:
            raise Exception # TODO: raise a more appropriate exception
        return super(Person, self).save(*args, **kwargs)


class Teacher(models.Model):
    person = models.ForeignKey(Person, related_name = 'teacher', unique=True, blank = True, null = True)
    dummy_field_one = models.CharField(max_length=100, blank = True, null = True)
    dummy_field_two = models.CharField(max_length=100, blank = True, null = True)

class Membership(models.Model):
    PERSON_DISPLAY_PRIORITY = (
        (1, 'No role'),
        (2, 'Significant'),
        (3, 'More significant'),
        (4, 'Very significant'),
        (5, 'Home'),
        )
    ENTITY_DISPLAY_PRIORITY = (
        (1, 'No role'),
        (2, 'Has a role'),
        (3, 'Key member'),
        (4, 'Keyer member'),
        (5, 'Keyest member'),
        )
    person = models.ForeignKey(Person, related_name='member_of')
    entity = models.ForeignKey(Entity, related_name='members')
    # this is currently too complex to manage - in this version it remains unused
    display_role = models.ForeignKey('self', related_name="display_roles",
        null=True, blank=True) 
    key_contact = models.BooleanField(default=False)
    role = models.CharField(max_length=50, null=True, blank=True)
    # how important the role is to the person
    importance_to_person = models.IntegerField(blank=True, null=True,
        choices=PERSON_DISPLAY_PRIORITY, default=1) 
    # how important the role is to the entity
    importance_to_entity = models.IntegerField(blank=True, null=True,
        choices=ENTITY_DISPLAY_PRIORITY, default=1) 
    
    class Meta:
        ordering = ('-importance_to_entity', 'person__surname')
    
    def __unicode__(self):
        if self.display_role:
            return unicode(self.entity.short_name) + "-" + unicode(self.display_role)
        else:
            return unicode(self.role)
    
    def save(self, *args, **kwargs):
        """
        The rules:
                order                 importance_to_entity
        ---------------------       ---------------------
        has no role:    1           has no role:    1
        has a role:     2-4         has a role:     2
        home:           5           key member:     3-5
        """
        # if there's just one membership, make it home; if this one is home, make home on all the others false
        memberships = Membership.objects.filter(person = self.person)
        if self.importance_to_person == 5:
            for membership in memberships: 
        
                if membership.importance_to_person == 5: 
                    
                    membership.importance_to_person = 4
                super(Membership, membership).save()
            self.importance_to_person = 5
        # if no role is set, then it can't be home or a key membership, and orders must be the lowest
        if not self.role: 
            self.importance_to_person = 1
        # if there is a role set, orders must be > 1
        else:
            if self.importance_to_person < 2: # with a role, order must be at least 2
                self.importance_to_person = 2
            if self.importance_to_entity < 2:  
                self.importance_to_entity = 2 # and importance_to_entity must be 2
        super(Membership, self).save(*args, **kwargs)


class EntityAutoPageLinkPluginEditor(CMSPlugin):
    AUTO_PAGES = {
        'contacts-and-people':
            (u'Contacts & people', 'contact', 'contacts_page_menu_title', 'auto_contacts_page'),
        'news-and-events':
            (u'News & events', 'news-and-events', 'news_page_menu_title', 'auto_news_page'),
        'vacancies-and-studentships':
            (u'Vacancies & studentships', 'vacancies-and-studentships', 'vacancies_page_menu_title',  'auto_vacancies_page'),
        'publications':
            (u'Publications', 'publications', 'publications_page_menu_title',  'auto_publications_page'),
        }
    link_to = models.CharField(max_length=50, choices=[(x, y[0]) for x, y in sorted(AUTO_PAGES.items())])
    entity = models.ForeignKey(Entity, null=True, blank=True, 
        help_text="Leave blank for autoselect", 
        related_name="auto_page_plugin", on_delete=models.SET_NULL)
    text_override = models.CharField(max_length=256, null=True, blank=True, 
        help_text="Override the default link text")


class EntityDirectoryPluginEditor(CMSPlugin):
    DIRECTORY_TYPE = (
        ('children', u'Immediate children only'),
        ('descendants', u'All descendants'),
        )
    entity = models.ForeignKey(Entity, null=True, blank=True, 
        help_text="Leave blank for autoselect", related_name="directory_plugin",
        on_delete=models.SET_NULL)
    #display = models.CharField(max_length=50, choices = DIRECTORY_TYPE, default = 'children',)
    levels = models.PositiveSmallIntegerField(help_text=u'Leave blank/set to 0 if all sub-levels are to be displayed',
        null=True, blank=True)
    display_descriptions_to_level = models.PositiveSmallIntegerField(default=0,
        help_text=u'Blank for all levels, 0 for none, 1 for first', null=True,
        blank=True)
    link_icons = models.BooleanField(help_text=u"Display link icons (first level only)",
        default=True)
    use_short_names = models.BooleanField(default=True)


class EntityMembersPluginEditor(CMSPlugin):
    entity = models.ForeignKey(Entity, null=True, blank=True, 
        help_text="Leave blank for autoselect", 
        related_name="entity_members_plugin", on_delete=models.SET_NULL)

# try:
#     mptt.register(Entity)
# except mptt.AlreadyRegistered:
#     pass

# default_entity_id is used to autofill the default entity where required, when MULTIPLE_ENTITY_MODE = False
# default_entity is used throughout the system
# make default_entity and default_entity_id available
default_entity = Entity.objects.base_entity() # get it from the Entity custom manager method
if default_entity and not MULTIPLE_ENTITY_MODE:
    default_entity_id = base_entity_id
else:
    default_entity_id = None


# crazymaniac's wild monkeypatch# 
# """
# THE FOLLOWING CODE IS A LOADED GUN AND MAY VERY WELL BACKFIRE.
# 
# I STRONGLY ADVICE AGAINST USING THIS CODE AND IF YOU STILL WANT TO USE IT, YOU ARE
# DOING SO AT YOUR OWN RISK.
# """
# 
# from cms.admin.forms import PageForm
# from cms.admin.pageadmin import PageAdmin

# set up the attributes of the the meta_description in the PageForm
# PageForm.base_fields['meta_description'].required = True
# PageForm.base_fields['meta_description'].label = "Summary"
# PageForm.base_fields['meta_description'].help_text = \
# "A <em>brief</em> (25-30 words maximum) summary of the page's message or contents in the clearest, simplest language possible."

# get the SEO settings fields
# tmp = list(PageAdmin.fieldsets[4][1]['fields'])

# we can't amend the fieldsets tuple itself, so we'll just leave the SEO fieldset blank
# this is in fact a good metaphor for the empty nature of SEO
# tmp.remove('meta_keywords')
# tmp.remove('meta_description')
# tmp.remove('page_title')
# PageAdmin.fieldsets[4][1]['fields'] = tmp

# rescue the meta_description field from its undeserved obscurity
# and put it in the first fieldset on the page
# PageAdmin.fieldsets[0][1]['fields'].insert(1, 'meta_description')

# page_title really belongs in the Advanced settings fieldset
# PageAdmin.fieldsets[03][1]['fields'].insert(1, 'page_title')
