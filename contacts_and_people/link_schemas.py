# register all interesting models for search
#print "LOADING link_schemas.py for %s" % __name__

from contacts_and_people import models, admin
from links import schema, LinkWrapper
from django.utils.encoding import smart_unicode

# from sorl.thumbnail.main import DjangoThumbnail, build_thumbnail_name
# from sorl.thumbnail.fields import ALL_ARGS
# from easy_thumbnail.files.thumbnailer import get_thumbnail_name
from easy_thumbnails.files import get_thumbnailer
from widgetry.views import search

class PersonWrapper(LinkWrapper):
    search_fields = admin.PersonAdmin.search_fields
    def title(self):
        if self.obj.user:
            return u"%s %s (%s)" % (self.obj.surname, self.obj.given_name, self.obj.user.username) 
        else:
            title = self.obj.title or ""
            return u"%s %s %s" % (title, self.obj.given_name, self.obj.surname)
    def short_text(self):
        return u"%s %s" % (self.obj.given_name, self.obj.surname)
    def description(self):
        data = []
        data.append(smart_unicode(self.obj.get_role()))
        data.append(smart_unicode(self.obj.get_entity()))
#        for membership in self.obj.member_of.all():
#            data.append(smart_unicode(membership.entity))
        return ', '.join(data)
    def thumbnail_url(self):
        print "================== in thumbnail_url of PersonWrapper"
        try:
            size = self.THUMBNAIL_SIZE # which is defined in widgetry, and can be overridden in settings
            # args = {'size': (int(size),int(size)), 'options': ['crop','upscale'], 'quality': 85}
            # print "args:", args
            # # Build the DjangoThumbnail kwargs.
            # kwargs = {}
            # for k, v in args.items():
            #     kwargs[ALL_ARGS[k]] = v
            # # Build the destination filename and return the thumbnail.
            # name_kwargs = {}
            # for key in ['size', 'quality', 'basedir', 'subdir',
            #             'prefix', 'extension']:
            #     name_kwargs[key] = args.get(key)
            #     
            source = self.obj.image.file # was self.obj.image.file - no longer works, because it adds the absolute filepath into the url - why?
            # print "type", type(source)
            # print "------> source", source.name
            # print "attempting to get thumbnail name:"
            return get_thumbnailer(source).get_thumbnail({'subject_location': u'', 'upscale': True, 'crop': True, 'size': (size, size)}
).url
            # print "        done"
            # # get_thumbnailer(source).get_thumbnail(kwargs).url, "done"
            # dest = get_thumbnail_name(source.name, **name_kwargs)
            # print "------> dest", dest
            # url = unicode(DjangoThumbnail(source, relative_dest=dest, **kwargs))
            # print "------> url", url
    
        except Exception,e:
            print e
            url = None
        return url
    def heading(self):
        return "Related people"
schema.register_wrapper(models.Person,PersonWrapper)

class EntityWrapper(LinkWrapper):
    search_fields = admin.EntityAdmin.search_fields
    link_attributes = models.EntityAutoPageLinkPluginEditor.AUTO_PAGES["contacts-and-people"]
    def description(self):
        if self.obj.url:
            return "External entity"
        else:
            return self.obj.get_website().get_meta_description()
#        r = []
#        if self.obj.building: r.append(smart_unicode(self.obj.building))
#        return "\n".join(r)
    def heading(self):
        return "Related pages"
    def url(self):
        return self.obj.get_website_url()
        # this old way would take us to the Contacts & People page - not necessary, really
        #return self.obj.get_absolute_url() + self.link_attributes[1] + "/" # adds "contacts" (or whatever) to URL
    def text(self):
        return str(self.obj)# + ": " + self.link_attributes[0]
    def short_text(self):
        return str(self.obj.short_name)        
schema.register_wrapper([models.Entity],EntityWrapper)

class BuildingWrapper(LinkWrapper):
    search_fields = admin.BuildingAdmin.search_fields
    # link_attributes = models.EntityAutoPageLinkPluginEditor.AUTO_PAGES["contacts-and-people"]
    def description(self):
        description = lambda obj: ", ".join(obj.get_postal_address())
        return "this doesn't work yet"
#        r = []
#        if self.obj.building: r.append(smart_unicode(self.obj.building))
#        return "\n".join(r)
    def heading(self):
        return "Places"
    # def url(self):
    #     return self.obj.get_website_url()
        # this old way would take us to the Contacts & People page - not necessary, really
        #return self.obj.get_absolute_url() + self.link_attributes[1] + "/" # adds "contacts" (or whatever) to URL
    def text(self):
        return self.obj.get_name()
    # def short_text(self):
    #     return str(self.obj.short_name)        
schema.register_wrapper([models.Building],BuildingWrapper)
# search.register(models.Building, search_fields=admin.BuildingAdmin.search_fields, 
#                 description=lambda obj: ", ".join(obj.get_postal_address())
#                )

