# register all interesting models for search

from contacts_and_people import models, admin
from links import schema, LinkWrapper
from django.utils.encoding import smart_unicode

from easy_thumbnails.files import get_thumbnailer
from widgetry.views import search


class PersonWrapper(LinkWrapper):
    search_fields = admin.PersonAdmin.search_fields

    def title(self):
        return self.obj.__unicode__()
        
    def short_text(self):
        return u"%s %s" % (self.obj.given_name, self.obj.surname)

    def description(self):
        data = []
        data.append(smart_unicode(self.obj.get_role))
        data.append(smart_unicode(self.obj.get_entity))
        return ', '.join(data)

    def thumbnail_url(self):
        try:
            size = self.THUMBNAIL_SIZE # which is defined in widgetry, and can be overridden in settings
            source = self.obj.image.file
            return get_thumbnailer(source).get_thumbnail({'subject_location': u'', 'upscale': True, 'crop': True, 'size': (size, size)}
).url
        except Exception,e:
            print "Error in personwrapper", e
            url = None
        return url

    def heading(self):
        return "Related people"
schema.register_wrapper(models.Person,PersonWrapper)


class EntityWrapper(LinkWrapper):
    search_fields = admin.EntityAdmin.search_fields
    # link_attributes = models.EntityAutoPageLinkPluginEditor.AUTO_PAGES["contacts-and-people"]

    def description(self):
        if self.obj.abstract_entity:
            return "Abstract entity - description unavailable"
        if self.obj.external_url:
            return "External entity at " + self.obj.external_url.url
        if self.obj.get_website and self.obj.get_website.get_meta_description():
            return self.obj.get_website.get_meta_description()
        # the following functionality will have to be restored in such a way that we don't return admin messages to the frontend - later
        # else:
        #     return u"<span class='errornote'>The page <em>" + unicode(self.obj.get_website) + "</em> has no description metadata. If you are responsible for this page, please address this problem <strong>immediately.</strong></span>"

    def heading(self):
        return "Related pages"

    def url(self):
        return self.obj.get_website_url()

    def text(self):
        return unicode(self.obj)# + ": " + self.link_attributes[0]

    def short_text(self):
        return unicode(self.obj.short_name)      
schema.register_wrapper([models.Entity],EntityWrapper)


class BuildingWrapper(LinkWrapper):
    search_fields = admin.BuildingAdmin.search_fields

    def description(self):
        return self.obj.get_postal_address

    def heading(self):
        return "Places"

    def text(self):
        return self.obj.get_name()

    def thumbnail_url(self):
        try:
            size = self.THUMBNAIL_SIZE # which is defined in widgetry, and can be overridden in settings
            source = self.obj.image.file
            return get_thumbnailer(source).get_thumbnail({'subject_location': u'', 'upscale': True, 'crop': True, 'size': (size, size)}
).url
        except Exception,e:
            print e
            url = None
        return url

schema.register_wrapper([models.Building],BuildingWrapper)
