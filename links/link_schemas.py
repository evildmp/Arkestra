# register all interesting models for search
#print "LOADING link_schemas.py for %s" % __name__

from links import models, admin
from links import schema, LinkWrapper
from django.conf import settings

permitted_filetypes = getattr(settings, "PERMITTED_FILETYPES", ["pdf",])

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
            # the following functionality will have to be restored in such a way that we don't return admin messages to the frontend - later

            # if not self.obj.get_meta_description():
            #     return "<span class='errornote'>The Page <em>" + unicode(self.obj) + "</em> has no <strong>Description metadata</strong>. If you are responsible for this Page, please address this problem <strong>immediately.</strong></span>"

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
    

    class FileLinkWrapper(LinkWrapper):
        search_fields = ['name', 'original_filename', 'sha1', 'description']
        def title(self):
            return self.obj.label
            
            # warn the user if the item lacks a Name field
            if not self.obj.name:
                item = self.obj.label
                return "%s <span class='errornote'>This Filer item has an empty <strong>Name</strong> field. If you are responsible for this item, please provide a proper name for it."  % item
            # otherwise, return its name
            else:
                return self.obj.name
 
        def url(self):
            return self.obj.url

        def description(self):
            return self.obj.description

            # the following functionality will have to be restored in such a way that we don't return admin messages to the frontend - later

            file = self.obj
            # an empty list for errors to report
            errors = []

            # find the item's folder_path
            if file.folder:
                folder = file.folder
                path = [unicode(folder)]
                while folder.parent:
                    path.insert(0, unicode(folder.parent))
                    folder = folder.parent
                folder_path = u" &rsaquo; ".join(path)
            else:
                folder_path = file.logical_folder.name
                
            # improperly filed? warn
            if folder_path == "unfiled files":
                errors.append("unfiled, and may be deleted")

            # no file name? warn
            if not file.name:
                errors.append("missing Name field")
                            
            # errors? list them all together
            if errors:
                error_message = "<span class='errornote'>Is this your file?<br />" + "<br />".join(["<em class='item_description'>%s</em>" %e for e in errors]) + "</span>"
            else:
                error_message = ""
                        
            # if not in allowed types, raises an exception and prevents item from being returned
            filetype = permitted_filetypes[file.extension]
            
            
            # build the description
            description = u"%s<br /><em>Folder:</em> %s<br />%s %s" % (
                 filetype, folder_path, file.description or "No description available", error_message
                )
            
            return description
                    
        def heading(self):
            return u"Files"    
            
    schema.register_wrapper(File, FileLinkWrapper)