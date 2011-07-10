# register all interesting models for search
#print "LOADING link_schemas.py for %s" % __name__

from links import models, admin
from links import schema, LinkWrapper
from django.conf import settings

schema.register(models.ExternalLink, search_fields=admin.ExternalLinkAdmin.search_fields, 
                #url='url', description=lambda obj: u"%s<br />%s" % (obj.url, obj.description), metadata='description', heading='"External links"'
                url='url', description = 'description', 
                #short_text = 'title', 
                heading='"External links"'
                )

if 'cms' in settings.INSTALLED_APPS:
    from cms.models import Page
    from cms.admin.pageadmin import PageAdmin
    class PageLinkWrapper(LinkWrapper):
        #search_fields = PageAdmin.search_fields
        search_fields = ['title_set__title',]
        def text(self):
            return self.obj.get_title()
        def short_text(self):
            return self.obj.get_menu_title()
        def description(self):
            return self.obj.get_meta_description()
        def metadata(self):
            ancestors = self.obj.get_cached_ancestors()
            r = []
            for ancestor in ancestors:
                r.append(u"%s" % ancestor.get_menu_title())
            r.append(self.obj.get_menu_title())
            return u" &raquo; ".join(r)
        def heading(self):
            return "Related pages"
    schema.register_wrapper(Page, PageLinkWrapper)

if 'filer' in settings.INSTALLED_APPS:
    from filer.models import File
    from filer.admin import FileAdmin
    def the_path(obj, items=[]):
        items[0:0] = [obj.name]
        if obj.parent:
            items = the_path(obj.parent, items)
        return items
    def file_description(obj):
        if obj.folder:
            s = u" &raquo; ".join(the_path(obj.folder))
        else:
            s = obj.logical_folder.name
        #return u"Folder: %s" % s
        return obj.description
    
    schema.register(File, FileAdmin.search_fields, title="label", description=file_description, heading="'Files'", url="url", #short_text = 'name'
     )
    
    
