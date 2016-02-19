#app = contacts_and_people
from django.db import models
from django.db.utils import DatabaseError
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.functional import cached_property
from django.conf import settings
from django.core.urlresolvers import reverse

from cms.models import Page, CMSPlugin
from cms.models.fields import PlaceholderField

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from filer.fields.image import FilerImageField

from arkestra_utilities.mixins import URLModelMixin
from arkestra_utilities.text import concatenate
from arkestra_utilities.settings import (
    MULTIPLE_ENTITY_MODE, ARKESTRA_BASE_ENTITY, DEFAULT_NEWS_PAGE_TITLE,
    DEFAULT_CONTACTS_PAGE_TITLE, DEFAULT_VACANCIES_PAGE_TITLE,
    DEFAULT_PUBLICATIONS_PAGE_TITLE
    )
from arkestra_utilities.utilities import get_fallback_template

import news_and_events


class Site(models.Model):
    """Maintains a list of an institution's geographical sites"""
    site_name = models.CharField(max_length=50, unique=True)
    post_town = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ('country', 'site_name', 'post_town')

    def __unicode__(self):
        return self.site_name

    def buildings(self):
        return self.place.all().count()

    @property
    def maps(self):
        return [
            building for building in self.place.all() if building.has_map()
            ]


class BuildingManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Building(models.Model):
    # the Building model should really be named Place
    objects = BuildingManager()
    name = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=10, blank=True)
    street = models.CharField(
        "Street name", max_length=100,
        blank=True
        )
    additional_street_address = models.CharField(
        help_text=u"If required",
        max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=9, null=True, blank=True)
    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, related_name="place"
        )
    slug = models.SlugField(
        blank=True,
        help_text=u"Leave blank to regenerate; amend only if required",
        max_length=255, null=True, unique=True
        )
    image = FilerImageField(
        on_delete=models.SET_NULL,
        null=True, blank=True
        )
    # for the place page
    summary = models.TextField(
        verbose_name="Summary",
        max_length=256,
        default="",
        help_text="A very short description (maximum two lines)",
        )
    description = PlaceholderField(
        'body', related_name="building_description",
        help_text="A fuller description"
        )
    getting_here = PlaceholderField(
        'simple',
        related_name="getting_here",
        help_text="How to get here"
        )
    access_and_parking = PlaceholderField(
        'simple',
        related_name="building_access_and_parking",
        help_text="Where to park, how to get in, etc"
        )
    map = models.BooleanField(
        "Show map", default=False,
        help_text="Use Google Maps to <a target='_blank' \
        style='text-decoration: underline;' \
        href='http://universimmedia.pagesperso-orange.fr/geo/loc.htm'>look up\
        Latitude & Longitude</a>")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    zoom = models.IntegerField(blank=True, null=True, default=17)

    class Meta:
        ordering = ('site', 'street', 'number', 'name',)

    def __unicode__(self):
        """
        A text-friendly way of referring to a building
        """
        if self.name:
            return self.name
        elif self.street:
            return concatenate([self.number, self.street], " ")
        else:
            return self.postcode

    @property
    def admin_identifier(self):
        return u"%s (%s)" % (self.__unicode__(), unicode(self.site))

    def get_absolute_url(self):
        return reverse("contact-place", kwargs={"slug": self.slug})

    def save(self):
        # if the slug is blank, regenerate it
        if not self.slug:
            self.slug = slugify(self.__unicode__())
        super(Building, self).save()

    @property
    def get_postal_address(self):
        """
        Assembles the postal (external) parts of an address
        """
        # print "getting postal address"
        address = []
        if self.name:
            address.append(self.name)
        if self.number or self.street:
            address.append(
                concatenate(
                    strings=[self.number, self.street],
                    with_string=" "
                    )
                )
        if self.additional_street_address:
            address.append(self.additional_street_address)
        # there will always be a site.post_town; no need to check
        fragments = concatenate(
            strings=[self.site.post_town, self.postcode],
            with_string=" "
            )
        address.append(fragments)
        return address

    def has_map(self):
        return (
            self.latitude is not None and self.longitude is not None
            and self.zoom and self.map
            )
    has_map.boolean = True

    @cached_property
    def events(self):
        # invoke the lister to find out more
        lister = news_and_events.lister.EventsPlaceLister(
            place=self,
            entity=None,
            display="events",
            order_by="date",
            item_format="details image",
            # request=instance.request
            )
        return lister

    @property
    def get_website(self):
        return None


class PhoneContact(models.Model):
    LABEL_CHOICES = (
        ('', '-----'),
        ('Office', 'Office'),
        ('Laboratory', 'Laboratory'),
        ('Mobile', 'Mobile'),
        ('Fax', 'Fax'),
        ('Out of hours', 'Out of hours'),
        ('Pager', 'Pager'),
        )
    label = models.CharField(max_length=64, null=True, blank=True)
    country_code = models.CharField(max_length=5, default="44")
    area_code = models.CharField(
        max_length=5, default="029", help_text="Not 02920"
        )
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
    precise_location = models.CharField(
        help_text=u"Precise location <em>within</em> the building, \
        for visitors",
        max_length=255, null=True, blank=True
        )
    access_note = models.CharField(
        help_text=u"Notes on access/visiting hours/etc",
        max_length=255, null=True, blank=True
        )
    email = models.EmailField(
        verbose_name="Email address", null=True, blank=True
        )
    phone_contacts = generic.GenericRelation(PhoneContact)
    image = FilerImageField(on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True


class EntityLite(models.Model):
    name = models.CharField(
        max_length=100, help_text="e.g. Department of Haematology"
        )

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
            # we don't use default_entity (or default_entity_id) in
            # MULTIPLE_ENTITY_MODE
            try:
                # print "trying to match", ARKESTRA_BASE_ENTITY
                entity = self.model.objects.get(id=ARKESTRA_BASE_ENTITY)
            # it can't be found, maybe because of a misconfiguation or because
            # we haven't added any Entities yet
            except (Entity.DoesNotExist, DatabaseError):
                # print "** Either the Entity does not exist, or I got a
                # DatabaseError:"
                # print "**", e
                pass
            else:
                # print "** I successfully found a default entity:", entity
                return entity

    # only used in single-entity mode
    def default_entity_id(self):
        if self.base_entity and not MULTIPLE_ENTITY_MODE:
            return ARKESTRA_BASE_ENTITY


class Entity(MPTTModel, EntityLite, CommonFields):
    objects = EntityManager()

    # URLModelMixin's get_absolute_url() requires a view_name
    view_name = "contact-entity"

    short_name = models.CharField(
        blank=True, help_text="e.g. Haematology",
        max_length=100, null=True, verbose_name="Short name for menus"
        )
    abstract_entity = models.BooleanField(
        "abstract", default=False,
        help_text=u"Select if this <em>group</em> of entities, but not an \
            entity itself, or if it's just a grouping of people",)
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children'
        )
    display_parent = models.BooleanField(
        u"Include parent entity's name in address", default=True,
        help_text=u"Deselect if this entity recapitulates its parent's name"
        )
    building_recapitulates_entity_name = models.BooleanField(
        default=False,
        help_text=u"""
        Removes the first line of the address - use to avoid, for
        example:<br /><em>Department of Haematology<br />Haematology
        Building<br />...</em>
        """
        )
    building = models.ForeignKey(
        Building,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text=u"Select the place where this Entity is based"
        )
    website = models.ForeignKey(
        Page, verbose_name="Home page",
        related_name='entity', unique=True, null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text=u"Select the Page that is the home page of this Entity \
        (leave blank if this is an external Entity)",)

    auto_news_page = models.BooleanField(
        u"Publish an automatic news & events page",
        default=False,
        )
    news_page_menu_title = models.CharField(
        u"Title",
        max_length=50,
        default=DEFAULT_NEWS_PAGE_TITLE
        )
    news_page_intro = PlaceholderField(
        'body',
        related_name="news_page_intro",
        )

    auto_contacts_page = models.BooleanField(
        u"Publish an automatic contacts & people page", default=False,
        )
    contacts_page_menu_title = models.CharField(
        u"Title",
        max_length=50,
        default=DEFAULT_CONTACTS_PAGE_TITLE,
        )
    contacts_page_intro = PlaceholderField(
        'body',
        related_name="contacts_page_intro",
        help_text="Text for the Contacts & people page"
        )

    auto_vacancies_page = models.BooleanField(
        u"Publish an automatic vacancies & studentships page",
        default=False,
        )
    vacancies_page_menu_title = models.CharField(
        u"Title",
        max_length=50,
        default=DEFAULT_VACANCIES_PAGE_TITLE,
        )
    vacancies_page_intro = PlaceholderField(
        'body',
        related_name="vacancies_page_intro",
        )

    if 'publications' in settings.INSTALLED_APPS:
        auto_publications_page = models.BooleanField(
            u"Publish a publications page for this entity automatcally",
            default=False
            )
        publications_page_menu_title = models.CharField(
            u"Title",
            max_length=50,
            default=DEFAULT_PUBLICATIONS_PAGE_TITLE,
            )

    class Meta:
        verbose_name_plural = "Entities"
        ordering = ['tree_id', 'lft']

    # def natural_key(self):
    #     return (self.slug)

    def __unicode__(self):
        return self.name

    @property
    def get_real_ancestor(self):
        """
        Find the nearest non-abstract Entity amongst this Entity's ancestors
        """
        for ancestor in self.get_ancestors(ascending=True):
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
                return self.get_real_ancestor.get_building
            except AttributeError:
                return None

    @property
    def _get_institutional_address(self):
        """
        Lists the parts of an address within the institution (Section of YYY,
        Department of XXX and YYY, School of ZZZ)
        """
        if self.abstract_entity:
            return
        else:
            ancestors = []
            showparent = self.display_parent
            for entity in self.get_ancestors(ascending=True) \
                    .exclude(abstract_entity=True):

                if showparent:
                    ancestors.append(entity.name)
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
        Return the Django CMS page that this Entity has attached to it (or to
        its nearest parent)
        """
        if self.website:
            return self.website
        else:
            try:
                return self.parent.get_website
            except AttributeError:
                return None

    def get_website_url(self):
        """
        Return the Django CMS page's url that this Entity has attached to it
        (or to its nearest parent)
        """
        if self.website:
            return self.website.get_absolute_url()
        elif self.external_url:
            return self.external_url.url
        elif self.parent:
            # try
            return self.parent.get_website_url()
        else:  # except
            return None

    def get_auto_page_url(self, view_name):
        """
        Returns a URL not for the entity, but for its /contact page,
        /news-and-events, or whatever.

        If the entity is the base entity, doesn't add the entity slug to
        the URL
        """
        if not view_name:
            return ""
        # external entities don't have info pages
        elif self.external_url:
            return ""
        # info pages for base entity
        elif self == Entity.objects.base_entity():
            return reverse(view_name)
        # info pages for other entities
        else:
            return reverse(view_name, kwargs={"slug": self.slug})

    def get_template(self):
        """
        Returns a template for any pages that need to render based on this
        entity
        """
        if self.get_website:
            return self.get_website.get_template()
        else:
            return get_fallback_template()

    def get_contacts(self):
        """
        Return designated contacts for the entity
        """
        return self.members.filter(
            person__active=True,
            key_contact=True
            ).order_by('importance_to_entity')

    def get_people_with_roles(self, key_members_only=False):
        """
        Publishes an ordered list of key members grouped by their most
        significant roles in the entity

        Ranks roles by importance to entity, then gathers people under that
        role

        Optionally, will return *all* members with roles
        """
        memberships = self.members.\
            filter(person__active=True).\
            exclude(role="").\
            order_by(
                '-importance_to_entity',
                'person__surname',
                'person__given_name'
                )

        if key_members_only:
            memberships = memberships.filter(importance_to_entity__gte=3)
        # create a set with which to check for duplicates
        duplicates = set()
        membership_list = []
        for membership in memberships:
            # if this is the first time we've seen this role...
            if membership.role not in duplicates:
                # put this role on the duplicates list for future reference,
                # and add everyone with that role to the membership_list
                duplicates.add(membership.role)
                membership_list.extend(
                    memberships.filter(role=membership.role)
                )
        # returns a list of memberships, in the right order - we use a regroup
        # tag to group them by person in the template
        return membership_list

    def get_key_people(self):
        return self.get_people_with_roles(key_members_only=True)

    def get_roles_for_members(self, members):
        """
        Given a list of its members (as Persons), returns the best role for
        each.

        The roles returned are in alphabetical order by Person.
        """
        for m in members:
            ms = m.member_of
            # get the best named membership in the entity
            named_memberships = ms.filter(entity=self) \
                .exclude(role="").order_by('-importance_to_person')
            if named_memberships:
                m.membership = named_memberships[0]
            else:
                # see if there's a display_role membership - actually this one
                # should go first
                display_role_memberships = ms.filter(entity=self) \
                    .exclude(display_role=None). \
                    order_by('-importance_to_person',)
                if display_role_memberships:
                    m.membership = display_role_memberships[0].display_role
                else:
                    # find the best named membership anywhere we can
                    best_named_ms = ms.exclude(role="") \
                        .order_by('-importance_to_person',)
                    if best_named_ms:
                        m.membership = best_named_ms[0]
                    else:
                        # add the unnamed membership for this entity - it's
                        # all we have
                        unnamed_mss = ms.order_by('-importance_to_person',)
                        m.membership = unnamed_mss[0]
        return members

    def get_people(self, letter=None):
        """
        Publishes a list of every member, and of every member of all children
        """
        people = Person.objects.filter(
            active=True,
            member_of__entity__in=self.get_descendants(include_self=True)). \
            order_by('surname', 'given_name', 'middle_names').distinct()

        if letter:
            people = people.filter(surname__istartswith=letter)

        return people

    def get_people_and_initials(self, letter=None):
        """
        Returns a list of people and/or their initials for use in people lists

        More than 20 people, or a letter was provided? Return initials
        Fewer than 20 people? Return the people
        """
        people = self.get_people(letter)
        # letter or long list? show initials
        if letter or people.count() > 20:
            initials = set(person.surname[0].upper() for person in people)
            initials = list(initials)
            initials.sort()
            # no letter but list is long? initials only
            if not letter:
                people = people[:0]
        # no letter, short list? don't show initials
        else:
            initials = None
        return (people, initials)


class Title(models.Model):
    title = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.abbreviation


class PersonLite(models.Model):
    title = models.ForeignKey(
        'contacts_and_people.Title',
        blank=True, null=True,
        on_delete=models.SET_NULL)
    given_name = models.CharField(max_length=50, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    surname = models.CharField(max_length=50)

    def __unicode__(self):
        # to-do: make it smarter, i.e. don't include empty/None strings
        return u"%s %s %s" % (self.given_name, self.middle_names, self.surname)

    def __getInitials(self):
        if self.given_name != '' and self.middle_names != '':
            return self.given_name[0] + '.' + self.middle_names[0] + '.'
        elif self.given_name != '':
            return self.given_name[0] + '.'
        else:
            return ''
    initials = property(__getInitials,)


class PersonManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Person(PersonLite, CommonFields):
    objects = PersonManager()

    # URLModelMixin's get_absolute_url() requires a view_name
    view_name = "contact-person"

    user = models.ForeignKey(
        User,
        related_name='person_user',
        unique=True,
        blank=True, null=True,
        verbose_name='Arkestra User',
        on_delete=models.PROTECT
        )
    institutional_username = models.CharField(
        max_length=10, blank=True, null=True
        )
    active = models.BooleanField(default=True,)
    description = PlaceholderField('body')
    entities = models.ManyToManyField(
        Entity, related_name='people',
        through='Membership', blank=True, null=True
        )
    building = models.ForeignKey(
        Building,
        verbose_name='Specify building',
        help_text=u"""
            <strong>Only</strong> required if this Person's <strong>Home
            entity</strong> has a different address
        """,
        blank=True, null=True,
        on_delete=models.SET_NULL
        )
    override_entity = models.ForeignKey(
        Entity, verbose_name='Specify entity',
        help_text=u"""
            <strong>Temporarily specify</strong> an entity for contact
            information - over-rides entity and postal address
            """,
        related_name='people_override',
        blank=True, null=True,
        on_delete=models.SET_NULL
        )
    please_contact = models.ForeignKey(
        'self',
        help_text=u"""
            Publish another person's details as contact information for this
            person
        """,
        related_name='contact_for',
        blank=True, null=True,
        on_delete=models.SET_NULL)
    staff_id = models.CharField(null=True, blank=True, max_length=20)
    data_feed_locked = models.BooleanField(default=False)

    # def natural_key(self):
    #     return (self.slug)

    class Meta:
        ordering = ['surname', 'given_name', 'user']
        verbose_name_plural = "People"

    def __unicode__(self):
        title = self.title or ""
        return u" ".join(
            name_part for name_part in (
                unicode(title),
                self.given_name,
                self.surname
            ) if name_part
        )

    @property
    def get_role(self):
        """
        Returns a Membership object.

        Works the Membership object representing a Person's best role, which
        has to be in a real, not abstract, entity, and it must be at least
        Significant (gte = 2) to the person

        If it can't find any role, it returns None.
        """
        memberships = self.member_of.filter(
            entity__abstract_entity=False,
            importance_to_person__gte=2).order_by('-importance_to_person')
        if memberships:
            return memberships[0]
        else:  # the poor person had no memberships
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

    def get_entity_short_name(self):
        if self.get_entity:
            return self.get_entity.short_name
        else:
            return u""
    get_entity_short_name.short_description = "Entity"

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
        Works out a person's address, based on their home/best entity or
        information that overrides this
        """
        if self.get_entity:  # needs an entity to work
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

    def get_phone_contacts(self):
        return self.get_please_contact().phone_contacts.all()

    def get_email(self):
        return self.get_please_contact().email

    @property
    def real_entity_memberships(self):
        # returns Memberships of non-abstract entities the person belongs to
        return self.member_of.filter(entity__abstract_entity=False)

    def gather_entities(self):
        """
        Returns all the entities that a person belongs to, including implicit
        membership
        """
        entitylist = set()
        for entity in self.entities.all():
            entitylist.add(entity)
            entitylist.update(entity.get_ancestors())
        #set(entity for entity in entitylist if not entity.abstract_entity)
        return entitylist

    def check_please_contact_has_loop(self, compare_to, person_list=None):
        if person_list is None:
            person_list = [compare_to]
        if not self == compare_to:
            person_list.append(self)
        if self.please_contact:
            if compare_to == self.please_contact:
                person_list.append(compare_to)
                return True, person_list
            else:
                return self.please_contact.check_please_contact_has_loop(
                    compare_to, person_list
                    )
        else:
            return False, person_list

    def save(self, *args, **kwargs):
        do_check_please_contact_loop = kwargs.pop(
            'do_check_please_contact_loop', True
            )
        if do_check_please_contact_loop and self.check_please_contact_has_loop(
                compare_to=self) is True:
            raise Exception  # TODO: raise a more appropriate exception
        return super(Person, self).save(*args, **kwargs)


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
    # this is currently too complex to manage - in this version it remains
    # unused
    display_role = models.ForeignKey(
        'self',
        related_name="display_roles",
        null=True, blank=True,
        on_delete=models.SET_NULL)
    key_contact = models.BooleanField(default=False)
    role = models.CharField(max_length=50, null=True, blank=True)
    # how important the role is to the person
    importance_to_person = models.IntegerField(
        blank=True, null=True,
        choices=PERSON_DISPLAY_PRIORITY, default=1
        )
    # how important the role is to the entity
    importance_to_entity = models.IntegerField(
        blank=True, null=True,
        choices=ENTITY_DISPLAY_PRIORITY, default=1
        )

    class Meta:
        ordering = ('-importance_to_entity', 'person__surname')

    def __unicode__(self):
        if self.display_role:
            return "%s-%s" % (
                unicode(self.entity.short_name), unicode(self.display_role)
                )
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
        # if there's just one membership, make it home; if this one is home,
        # make home on all the others false
        memberships = self.person.member_of.all()
        if self.importance_to_person == 5:
            for membership in memberships:

                if membership.importance_to_person == 5:
                    membership.importance_to_person = 4
                super(Membership, membership).save()
            self.importance_to_person = 5
        # if no role is set, then it can't be home or a key membership, and
        # orders must be the lowest
        if not self.role:
            self.importance_to_person = 1
        # if there is a role set, orders must be > 1
        else:
            # with a role, order must be at least 2
            if self.importance_to_person < 2:
                self.importance_to_person = 2
            # and importance_to_entity must be 2
            if self.importance_to_entity < 2:
                self.importance_to_entity = 2
        super(Membership, self).save(*args, **kwargs)


class EntityAutoPageLinkPluginEditor(CMSPlugin):
    AUTO_PAGES = {
        'contacts-and-people': (
            u'Contacts & people',
            'contact-entity',
            'contacts_page_menu_title',
            'auto_contacts_page'
            ),
        'news-and-events': (
            u'News & events',
            'news-and-events',
            'news_page_menu_title',
            'auto_news_page'
            ),
        'vacancies-and-studentships': (
            u'Vacancies & studentships',
            'vacancies-and-studentships',
            'vacancies_page_menu_title',
            'auto_vacancies_page'
            ),
        'publications': (
            u'Publications',
            'publications',
            'publications_page_menu_title',
            'auto_publications_page'),
        }
    link_to = models.CharField(
        max_length=50,
        choices=[(x, y[0]) for x, y in sorted(AUTO_PAGES.items())]
        )
    entity = models.ForeignKey(
        Entity, null=True, blank=True,
        help_text="Leave blank for autoselect",
        related_name="auto_page_plugin",
        on_delete=models.SET_NULL)
    text_override = models.CharField(
        max_length=256, null=True, blank=True,
        help_text="Override the default link text"
        )


class EntityDirectoryPluginEditor(CMSPlugin):
    DIRECTORY_TYPE = (
        ('children', u'Immediate children only'),
        ('descendants', u'All descendants'),
        )
    entity = models.ForeignKey(
        Entity, null=True, blank=True,
        help_text="Leave blank for autoselect",
        related_name="directory_plugin",
        on_delete=models.SET_NULL
        )

    levels = models.PositiveSmallIntegerField(
        help_text=u'Leave blank/set to 0 to display all sub-levels',
        null=True, blank=True
        )
    display_descriptions_to_level = models.PositiveSmallIntegerField(
        default=0,
        help_text=u'Blank for all levels, 0 for none, 1 for first', null=True,
        blank=True
        )
    link_icons = models.BooleanField(
        help_text=u"Display link icons (first level only)",
        default=True
        )
    use_short_names = models.BooleanField(default=True)


class EntityMembersPluginEditor(CMSPlugin):
    entity = models.ForeignKey(
        Entity, null=True, blank=True,
        help_text="Leave blank for autoselect",
        related_name="entity_members_plugin",
        on_delete=models.SET_NULL
        )

# try:
#     mptt.register(Entity)
# except mptt.AlreadyRegistered:
#     pass

# default_entity_id is used to autofill the default entity where required,
# when MULTIPLE_ENTITY_MODE = False
# default_entity is used throughout the system
# make default_entity and default_entity_id available
# default_entity = Entity.objects.base_entity() # get it from the Entity
# custom manager method
# if default_entity and not MULTIPLE_ENTITY_MODE:
#     default_entity_id = ARKESTRA_BASE_ENTITY
# else:
#     default_entity_id = None


# crazymaniac's wild monkeypatch#
# """
# THE FOLLOWING CODE IS A LOADED GUN AND MAY VERY WELL BACKFIRE.
#
# I STRONGLY ADVICE AGAINST USING THIS CODE AND IF YOU STILL WANT TO USE IT,
# YOU ARE
# DOING SO AT YOUR OWN RISK.
# """
#
# from cms.admin.forms import PageForm
# from cms.admin.pageadmin import PageAdmin

# set up the attributes of the the meta_description in the PageForm
# PageForm.base_fields['meta_description'].required = True
# PageForm.base_fields['meta_description'].label = "Summary"
# PageForm.base_fields['meta_description'].help_text = \
# "A <em>brief</em> (25-30 words maximum) summary of the page's message or
# contents in the clearest, simplest language possible."

# get the SEO settings fields
# tmp = list(PageAdmin.fieldsets[4][1]['fields'])

# we can't amend the fieldsets tuple itself, so we'll just leave the SEO
# fieldset blank
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
