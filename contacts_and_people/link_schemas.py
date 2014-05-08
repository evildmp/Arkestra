# register all interesting models for search

from contacts_and_people import models, admin
from links import schema, LinkWrapper
from django.utils.encoding import smart_unicode
from django.contrib.auth.admin import UserAdmin
from easy_thumbnails.files import get_thumbnailer


class PersonWrapper(LinkWrapper):
    search_fields = admin.PersonAdmin.search_fields
    special_attributes = ["phone", "email", "get_full_address", "get_building"]
    block_level_item_template = "contacts_and_people/person_block_level_list_item.html"
    link_format_choices = (
        (u"title", u"Name only"),
        (u"details", u"Name & summary (role)"),
        (u"details image", u"Name, summary (role) & image"),
        (u"details contact image", u"Name, summary (role), contact information & image"),
        (u"details contact", u"Name, summary (role) & contact information"),
        )

    def summary(self):
        data = []
        data.append(smart_unicode(self.obj.get_role))
        data.append(smart_unicode(self.obj.get_entity))
        return ', '.join(data)

    def thumbnail_url(self):
        try:
            size = self.THUMBNAIL_SIZE
            source = self.obj.image.file
            return get_thumbnailer(source).get_thumbnail({
                'subject_location': u'',
                'upscale': True,
                'crop': True,
                'size': (size, size)
            }).url
        except Exception, e:
            print "Error in personwrapper", e
            url = None
        return url

    def image(self):
        return self.obj.image

    def heading(self):
        return "Related people"

    def phone(self):
        return self.obj.get_phone_contacts()

    def email(self):
        return self.obj.get_email()

    def get_full_address(self):
        return self.obj.get_full_address

    def get_building(self):
        return self.obj.get_building

schema.register_wrapper(models.Person, PersonWrapper)


class UserWrapper(LinkWrapper):
    search_fields = UserAdmin.search_fields

    def title(self):
        return "%s: %s" % (self.obj.get_full_name(), self.obj.__unicode__())

    def short_text(self):
        return u"%s %s" % (self.obj.first_name, self.obj.last_name)

    def summary(self):
        data = [group.__unicode__() for group in self.obj.groups.all()]
        if self.obj.is_staff:
            data.append(u"Admin user")
        if self.obj.is_superuser:
            data.append(u"Super user")
        data.append(u"Last login: %s" % unicode(self.obj.last_login))
        return '<br /> '.join(data)

schema.register_wrapper(models.User, UserWrapper)


class EntityWrapper(LinkWrapper):
    search_fields = admin.EntityAdmin.search_fields
    special_attributes = ["phone", "email", "get_full_address", "get_building"]
    block_level_item_template = "contacts_and_people/entity_block_level_list_item.html"
    link_format_choices = (
        (u"title", u"Name only"),
        (u"details", u"Name & summary (description)"),
        (u"details image", u"Name, summary (description) & image"),
        (u"details contact image", u"Name, summary (description), contact information & image"),
        (u"details contact", u"Name, summary (description) & contact information"),
        )

    def summary(self):
        if self.obj.abstract_entity:
            return "Abstract entity - description unavailable"
        if self.obj.external_url:
            return "External entity at " + self.obj.external_url.url
        if self.obj.get_website and self.obj.get_website.get_meta_description():
            return self.obj.get_website.get_meta_description()
        else:
            return ""

    def image(self):
        return self.obj.image

    def heading(self):
        return "Related pages"

    def url(self):
        return self.obj.get_website_url() or "This entity can't be linked to"

    def short_text(self):
        return unicode(self.obj.short_name)

    def admin_metadata(self):
        entity_path = "<strong>Path:</strong> %s" % u" &rsaquo; ".join(
            entity.short_name for entity in self.obj.get_ancestors(
                include_self=True
                )
            )
        if self.summary():
            return entity_path
        elif self.obj.get_website:
            return u"""
            %s<br /><span class='errornote'>The page <em>%s</em> has no
            description metadata. If you are responsible for this page, please
            address this problem <strong>immediately.</strong></span>
            """ % (entity_path, unicode(self.obj.get_website))
        else:
            return u"""
            %s<br /><span class='errornote'>This entity has neither a home page
            nor an External URL.</span>
            """ % entity_path

    def phone(self):
        return self.obj.phone_contacts.all()

    def email(self):
        return self.obj.email

    def get_full_address(self):
        return self.obj.get_full_address

    def get_building(self):
        return self.obj.get_building

schema.register_wrapper([models.Entity], EntityWrapper)


class BuildingWrapper(LinkWrapper):
    search_fields = admin.BuildingAdmin.search_fields
    block_level_item_template = "contacts_and_people/building_block_level_list_item.html"
    special_attributes = ["map"]
    link_format_choices = (
        (u"title", u"Name only"),
        (u"details", u"Name & summary (address)"),
        (u"details image", u"Name, summary (address) & image"),
        )

    def summary(self):
        return ", ".join(self.obj.get_postal_address[1:])

    def heading(self):
        return "Places"

    def image(self):
        return self.obj.image

    def map(self):
        return self.obj.has_map()

    def thumbnail_url(self):
        try:
            size = self.THUMBNAIL_SIZE
            source = self.obj.image.file
            return get_thumbnailer(source).get_thumbnail({
                'subject_location': u'',
                'upscale': True,
                'crop': True,
                'size': (size, size)
            }).url
        except Exception, e:
            print e
            url = None
        return url

schema.register_wrapper([models.Building], BuildingWrapper)
