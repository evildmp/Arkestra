#app = contacts_and_people
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify, join
from django.conf import settings
from cms.models.fields import PlaceholderField
from filer.fields.image import FilerImageField
from links.models import ExternalLink
import mptt

Page = models.get_model('cms', 'Page')
CMSPlugin = models.get_model('cms', 'CMSPlugin')

class Site(models.Model):
    """Maintains a list of an institution's geographical sites"""
    class Meta:
        ordering = ('country','site_name', 'post_town',)
    site_name = models.CharField(max_length=50, unique=True)
    post_town = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    description = models.TextField(max_length = 500, null = True, blank=True)
    def __unicode__(self):
        return self.site_name

class Building(models.Model):
    """Each Building is on a Site."""
    class Meta:
        ordering = ('site', 'street', 'number', 'name',)
    name = models.CharField(max_length=100, null = True, blank=True)
    number = models.CharField(max_length=10, null = True, blank=True)
    street = models.CharField("Street name", max_length=100, null = True, blank=True)
    additional_street_address = models.CharField(help_text=u"If required", max_length=100, null = True, blank=True)
    postcode = models.CharField(max_length=9, null = True, blank=True)
    site = models.ForeignKey(Site)
    slug = models.SlugField(blank=True, help_text=u"Please leave blank/amend only if required", max_length=255, null=True, unique=True,)
    image = FilerImageField(null=True, blank=True)
    # for the place page
    summary =  models.TextField(
        verbose_name = "Summary",
        max_length=256, 
        help_text = "A very short description of this building (maximum two lines)",)
    description = PlaceholderField('body', 
        related_name = "building_description",
        help_text = "A fuller description",)
    getting_here = PlaceholderField('simple', 
        related_name = "getting_here",
        help_text = "How to get here",)
    access_and_parking = PlaceholderField('simple', 
        related_name = "building_access_and_parking",
        help_text = "Where to park, how to get in, etc",)
    map = models.BooleanField(
        "Show map",
        default=False)
    latitude = models.FloatField(null = True, blank = True,)
    longitude = models.FloatField(null = True, blank = True,)
    zoom = models.IntegerField(blank = True, null = True, default = 17)
    def get_name(self):
        """
        Assembles a half-decent name for a building
        """
        if self.name:
            building_identifier = self.name
        elif self.street:
            building_identifier = self.number + " " + self.street
        else:
            building_identifier = str(self.site) + ": " + self.postcode
        return building_identifier
    def get_postal_address(self):
        """
        Assembles the postal (external) parts of an address
        """
        print "getting postal address"
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
            address.append(self.site.post_town + " " + self.postcode)
        elif self.postcode:
            address.append(self.postcode)
        return address
    def show_map(self):
        return
    def __unicode__(self):
        if self.name:
            building_identifier = str(self.site) + ": " + self.name
        elif self.street:
            building_identifier = str(self.site) + ": " + self.number + " " + self.street
        else:
            building_identifier = str(self.site) + ": " + self.postcode
        return building_identifier
    def forthcoming_events(self):
        return self.event_set.all()
    def save(self):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.__unicode__())
        print "Building slug:", self.slug
        super(Building, self).save()
    def get_absolute_url(self):
        return "/place/%s/" % self.slug

class PhoneContact(models.Model):
    class Meta:
        ordering = ('label',)
    LABEL_CHOICES = ( ('','-----'),
                    ('Office', 'Office'),
                    ('Laboratory', 'Laboratory'),
                    ('Mobile','Mobile'),
                    ('Fax', 'Fax'),
                    ('Out of hours','Out of hours'),
                    ('Pager','Pager'),
                    )
    label = models.CharField(max_length=64, choices=LABEL_CHOICES, default=LABEL_CHOICES[0][0], null=True, blank=True)
    country_code = models.CharField(max_length=5, default = "44")
    area_code = models.CharField(max_length=5, default = "029", help_text = "Not 02920")
    number = models.CharField(max_length=12)
    internal_extension = models.CharField(max_length=6, null = True, blank = True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField(db_index=True)
    content_object = generic.GenericForeignKey()
    def __unicode__(self):
        return u"%s: %s" % (self.label, self.number)
        
class CommonFields(models.Model):
    class Meta:
        abstract = True
    precise_location = models.CharField(help_text=u"Precise location <em>within</em> the building, for visitors",
        max_length=255, null = True, blank=True
        )
    access_note = models.CharField(help_text = u"Notes on access/visiting hours/etc",
        max_length=255, null = True, blank=True
        )
    email = models.EmailField(verbose_name="Email address", null = True, blank=True)
    phone_contacts = generic.GenericRelation(PhoneContact)
    url = models.URLField(null = True, blank = True, 
        verify_exists=True, 
        help_text = u"To be used <strong>only</strong> for external items. Use with caution!")
    external_url = models.ForeignKey(ExternalLink, related_name = "%(class)s_item", blank = True, null = True,)
    image = FilerImageField(null=True, blank=True)
    slug=models.SlugField(unique= True, help_text=u"Do not meddle with this unless you know exactly what you're doing!")
    
class EntityLite(models.Model):
    name = models.CharField(max_length= 100, help_text = "e.g. Section of Haematology")
    def __unicode__(self):
        return str(self.name)

class Entity(EntityLite, CommonFields):
    class Meta:
        verbose_name_plural = "Entities"
        ordering = ['tree_id', 'lft']
    CONTACT_TEMPLATES = (
        (None, 'No automatic page'),
        ('entity_information.html', 'Default contacts and people'),
        ('basic_contact_information.html', 'Basic contact information only'),
        ('all_contact_information.html', 'All contact information'),
        ('key_roles.html', 'Key roles'),
        ('named_roles.html', 'Named roles'),
        ('key_people.html', 'Key people'),
        ('all_people_with_roles.html', 'All people (with roles)'),
        ('all_people_with_contact_info.html', 'All people (with contact information)'),
        ('entity_information.html', 'All info - testing only')
        )
    short_name = models.CharField(blank=True, help_text = "e.g. Haematology", max_length= 100, null=True, verbose_name = "Short name for menus",)
    abstract_entity = models.BooleanField(
        "Group",
        help_text =u"A <em>group</em> of entities, not an entity itself",
        default=False)
    parent = models.ForeignKey('self', blank=True, null = True, related_name='children')
    display_parent = models.BooleanField(default=True, help_text=u"Include parent entity's name in address")
    building = models.ForeignKey(Building, null = True, blank=True)
    website = models.ForeignKey(Page, verbose_name = "Home page", related_name = 'entity', unique = True, null = True, blank=True)
    if 'news_and_events' in settings.INSTALLED_APPS:
        auto_news_page = models.BooleanField(default = False)
        news_page_menu_title = models.CharField(max_length= 50, default = getattr(settings, "DEFAULT_NEWS_PAGE_TITLE", "News & events"),)
    if 'contacts_and_people' in settings.INSTALLED_APPS:
        auto_contacts_page = models.BooleanField(default = False)
        contacts_page_menu_title = models.CharField(max_length= 50, default = getattr(settings, "DEFAULT_CONTACTS_PAGE_TITLE", "Contacts & people"),)
    if 'vacancies_and_studentships' in settings.INSTALLED_APPS:
        auto_vacancies_page = models.BooleanField(default = False)
        vacancies_page_menu_title = models.CharField(max_length= 50, default = getattr(settings, "DEFAULT_VACANCIES_PAGE_TITLE", "Vacancies & studentships"),)
    if 'publications' in settings.INSTALLED_APPS:
        auto_publications_page = models.BooleanField(default = False)
        publications_page_menu_title = models.CharField(max_length= 50, default = getattr(settings, "DEFAULT_CONTACTS_PAGE_TITLE", "Publications"),)
    def real(self):
        if self.parent and self.abstract_entity:
            for ancestor in self.get_ancestors(ascending = True):
                print ancestor
                if not ancestor.abstract_entity:
                    entity = ancestor
                    break
            return entity
        else:
            return self
    def get_real_ancestor(self):
        """
        Find a non-abstract Entity amongst this Entity's ancestors
        """
        for ancestor in self.get_ancestors(ascending = True):
            if not ancestor.abstract_entity:
                entity = ancestor
                break
        return entity
    def get_address(self):
        """
        Returns the full address of an entity
        """
        entity = self
        if entity.abstract_entity:
            entity = self.get_real_ancestor()
        address = entity.get_institutional_address()
        building = entity.get_building()
        if building:
            address.extend(building.get_postal_address())
        return address
    def get_institutional_address(self):
        """
        Lists the parts of an address within the institution (Section of YYY, Department of XXX and YYY, School of ZZZ)
        """ 
        ancestors = []
        showparent = self.display_parent
        for entity in self.get_ancestors(ascending = True).exclude(abstract_entity = True):
            if showparent:
                ancestors.append(entity)
            showparent = entity.display_parent
        return ancestors
    def get_website(self):
        """
        Return the Django CMS page that this Entity has attached to it (or to its nearest parent)
        """
        print "get_website", self
        if self.website:
            return self.website
        else:
            try:
                return self.parent.get_website()
            except AttributeError: # I think this is right                
                print "couldn't find a website, so returning None"
                return None
    def get_website_url(self):
        """
        Return the Django CMS page that this Entity has attached to it (or to its nearest parent)
        """
        print "------ get_website_url -------"
        if self.website:
            return self.website.get_absolute_url()
        elif self.external_url.url:
            return self.external_url.url
        else:
            try:
                return self.parent.get_website_url()
            except:
                return Entity.objects.get(id=1).get_website()
    def get_template(self):
        """
        Returns a template for any pages that need to render based on this entity
        """
        print "------ get_template -------"
        if self.get_website():
            return self.get_website().get_template()
        else:
            return settings.CMS_DEFAULT_TEMPLATE
    def get_building(self):
        """
        Return the Building for this Entity (or its nearest parent) 
        """
        if self.building:
            return self.building
        else:
            try:
                return self.parent.get_building()
            except AttributeError:
                return None
    def get_contacts(self):
        """
        Return designated contacts for the entity
        """
        contacts = Membership.objects.filter(entity = self, key_contact = True).order_by('importance_to_entity')
        return contacts
    def get_roles(self, key_members_only = True):   
        """
        Publishes an ordered list of key members grouped by their most significant roles in the entity
        Ranks roles by importance to entity, then gathers people under that role
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
        """
        people = self.get_people(letter)
        # letter or long list? show initials
        if letter or len(people) > 25:
            initials = set(person.surname[0].upper() for person in people)
            initials = list(initials)
            initials.sort()
            # no letter but list is long? initials only
            if not letter:
                people = None
        # no letter, short list? don't show initials
        else:
            initials = None
        return (people, initials)
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/entity/%s/" % self.slug

class Title(models.Model):
    class Meta:
        ordering = ['title',]
    title = models.CharField (max_length = 50, unique = True)
    abbreviation = models.CharField (max_length = 20, unique = True)
    def __unicode__(self):
        return self.abbreviation

class PersonLite(models.Model):
    title = models.ForeignKey(
        'contacts_and_people.Title', 
        to_field = "abbreviation", 
        blank = True, 
        null = True,
        )
    given_name = models.CharField(max_length=50, blank = True, null = True)
    middle_names = models.CharField(max_length=100, blank = True, null = True)
    surname = models.CharField(max_length=50)
    def __getInitials(self):
        if self.given_name <> '' and self.middle_names <> '':
            return self.given_name[0] + '.' + self.middle_names[0] + '.'
        elif self.given_name <> '':
            return self.given_name[0] + '.'
        else:
            return ''
    initials = property(__getInitials,)  
    def __unicode__(self):
        return str(self.given_name + " " + self.middle_names + " " + self.surname)        

class Person(PersonLite, CommonFields):
    class Meta:
        ordering = ['surname', 'given_name', 'user',]
        verbose_name_plural = "People"
    user = models.ForeignKey(User, related_name = 'person_user', unique=True, blank = True, null = True, verbose_name='Arkestra User')
    institutional_username = models.CharField(max_length = 10, blank = True, null = True,)
    active = models.BooleanField(
        default=True,)
    description = PlaceholderField('body',)
    entities = models.ManyToManyField(Entity, related_name = 'people', through ='Membership', blank = True, null = True)
    building = models.ForeignKey(Building, verbose_name = 'Specify building', help_text = u"Specify a building for contact information - over-rides postal address",blank = True, null = True)
    override_entity = models.ForeignKey(Entity, verbose_name = 'Specify entity', help_text= u"Specify an entity for contact information - over-rides entity and postal address", related_name = 'people_override', blank = True, null = True)
    please_contact = models.ForeignKey('self', help_text=u"Publish alternative contact details for this person", related_name='contact_for', blank = True, null = True)
    staff_id = models.CharField(null=True, blank = True, max_length=20)
    data_feed_locked = models.BooleanField(default=False)
    def get_role(self):
        """
        Works out a person's best role. If it can't find any role, it returns None
        """
        memberships = Membership.objects.filter(person = self)
        try:
            role = memberships.order_by('-importance_to_person')[0] # we could just .exclude(importance_to_person__lt = 2) I think
            if role.role:
                return role
            else:
                return None
        except IndexError:
            print "person has no memberships"
            return None
    def get_entity(self):
        """
        Works out a person's entity, based on get_role
        """
        if self.override_entity:
            return self.override_entity
        else:    
            try:
                return self.get_role().entity
            except AttributeError:
                return None
    def get_address(self):
        """
        Works out a person's address, based on their home/best entity or information that overrides this
        """
        if self.building:
            address = self.get_entity().get_institutional_address()
            address.extend(self.building.get_postal_address())
            return address
        else:
            return self.get_entity().get_address()
    def get_please_contact(self):
        """
        Works out whether to display someone else's contact details
        """
        if self.please_contact:
            return self.please_contact.get_please_contact()
        else:
            return self
    def gather_entities(self):
        """
        Returns all the entities that a person belongs to, including implicit membership
        """
        entitylist = set()
        for entity in self.entities.all():
            entitylist.add(entity)
            entitylist.update(entity.get_ancestors())
        return entitylist #set(entity for entity in entitylist if not entity.abstract_entity)

    def __unicode__(self):
        title = self.title or ""
        return " ".join(name_part for name_part in [str(title), self.given_name, self.surname] if name_part)

    def get_absolute_url(self):
        if self.external_url:
            return self.external_url.url
        else:
            return "/person/%s/" % self.slug
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
#    def authoreds(self):
#        return self.researcher.authored.filter(visible = True).order_by('publication__type', 'reverse_sort_cue')

class Teacher(models.Model):
    person = models.ForeignKey(Person, related_name = 'teacher', unique=True, blank = True, null = True)
    dummy_field_one = models.CharField(max_length=100, blank = True, null = True)
    dummy_field_two = models.CharField(max_length=100, blank = True, null = True)

class Membership(models.Model):
    class Meta:
        ordering = ('-importance_to_entity', 'person__surname')
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
    person = models.ForeignKey(Person, related_name = 'member_of')
    entity = models.ForeignKey(Entity, related_name='members',)
    display_role = models.ForeignKey('self', related_name = "display_roles", null = True, blank = True) # this is currently too complex to manage - in this version it remains unused
    #home = models.BooleanField(default=False)
    #key_member = models.BooleanField(default=False)
    key_contact = models.BooleanField(default=False)
    role = models.CharField(max_length = 50, null = True, blank = True)
    importance_to_person = models.IntegerField(blank = True, null = True, choices = PERSON_DISPLAY_PRIORITY, default = 1) # how important the role is to the person
    importance_to_entity = models.IntegerField(blank = True, null = True, choices = ENTITY_DISPLAY_PRIORITY, default = 1) # how important the role is to the entity
    def save(self):
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
        print "I think that", self.person, "has", len(memberships), "memberships"
        if self.importance_to_person == 5:
            print "this one's home"
            for membership in memberships:
                if membership.importance_to_person == 5:
                    membership.importance_to_person = 4
                super(Membership, membership).save()
            print self
            self.importance_to_person = 5
        # if no role is set, then it can't be home or a key membership, and orders must be the lowest
        if not self.role: 
            self.importance_to_person = 1
        #     self.importance_to_entity = 1
        # if there is a role set, orders must be > 1
        else:
            print self, self.importance_to_entity
            if self.importance_to_person < 2: # with a role, order must be at least 2
                self.importance_to_person = 2
            if self.importance_to_entity < 2:  
                self.importance_to_entity = 2 # and importance_to_entity must be 2
        super(Membership, self).save()
    def __unicode__(self):
        if self.display_role:
            return str(self.entity.short_name) + "-" + str(self.display_role)
        else:
            return str(self.role)

class EntityAutoPageLinkPluginEditor(CMSPlugin):
    AUTO_PAGES = {
        'contacts-and-people':
            (u'Contacts & people', 'contact', 'contacts_page_menu_title',),
        'news-and-events':
            (u'News & events', 'news-and-events', 'news_page_menu_title',),
        'vacancies-and-studentships':
            (u'Vacancies & studentships', 'vacancies-and-studentships', 'vacancies_page_menu_title',),
        'publications':
            (u'Publications', 'publications', 'publications_page_menu_title'),
        }
    link_to = models.CharField(max_length=50, choices=[(x,y[0]) for x,y in sorted(AUTO_PAGES.items())])
    entity = models.ForeignKey(Entity, null = True, blank = True, 
        help_text = "Leave blank for autoselect", 
        related_name = "auto_page_plugin"
        )
    text_override = models.CharField(
        max_length=256, null = True, blank = True, 
        help_text = "Override the default link text"
        )

class EntityDirectoryPluginEditor(CMSPlugin):
    DIRECTORY_TYPE = (
        ('children', u'Immediate children only'),
        ('descendants', u'All descendants'),
        )
    entity = models.ForeignKey(Entity, null = True, blank = True, 
        help_text = "Leave blank for autoselect", 
        related_name = "directory_plugin"
        )
    #display = models.CharField(max_length=50, choices = DIRECTORY_TYPE, default = 'children',)
    levels = models.PositiveSmallIntegerField(help_text = u'Leave blank/set to 0 if all sub-levels are to be displayed', null = True, blank = True)
    display_descriptions_to_level = models.PositiveSmallIntegerField(default = 0, help_text = u'Blank for all levels, 0 for none, 1 for first', null = True, blank = True)
    link_icons = models.BooleanField(
        help_text =u"Display link icons (first level only)",
        default=True)
    use_short_names = models.BooleanField(
        default=True)

class EntityMembersPluginEditor(CMSPlugin):
    entity = models.ForeignKey(Entity, null = True, blank = True, 
        help_text = "Leave blank for autoselect", 
        related_name = "entity_members_plugin"
        )

try:
    mptt.register(Entity)
except mptt.AlreadyRegistered:
    pass