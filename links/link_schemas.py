from django.conf import settings

from cms.models import Page

from filer.models import File, Image

from arkestra_utilities.settings import PERMITTED_FILETYPES

from links import models, admin, schema, LinkWrapper


schema.register(
    models.ExternalLink,
    search_fields=admin.ExternalLinkAdmin.search_fields,
    url='url',
    summary='description',
    heading='"External links"',
    )


class PageLinkWrapper(LinkWrapper):
    search_fields = ['title_set__title']
    link_format_choices = (
        (u"title", u"Name only"),
        (u"details", u"Name & summary (description)"),
        )

    def title(self):
        return self.obj.get_title()

    def short_text(self):
        return self.obj.get_menu_title()

    def summary(self):
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


class FileLinkWrapper(LinkWrapper):
    search_fields = ['name', 'original_filename', 'sha1', 'description']

    # methods used by the Wrapper attributes
    def filetype(self):
        return PERMITTED_FILETYPES[self.obj.extension]

    def folder_path(self):
        # find the item's folder_path
        if self.obj.folder:
            folder = self.obj.folder
            path = [unicode(folder)]
            while folder.parent:
                path.insert(0, unicode(folder.parent))
                folder = folder.parent
            folder_path = u" &rsaquo; ".join(path)
        else:
            folder_path = file.logical_folder.name
        return folder_path

    def errors(self):
        file = self.obj
        # an empty list for errors to report
        errors = []

        # improperly filed? warn
        if self.folder_path == "unfiled files":
            errors.append(
                "This file is unfiled, and may be deleted without warning"
                )

        # no file name? warn
        if not file.name:
            errors.append("Name field is missing")

        # errors? list them all together
        if errors:
            error_items = "<br />".join(
                ["<em class='item_description'>%s</em>" % e for e in errors]
                )
            error_message = """
                <span class='errornote'>Is this your file?<br />%s</span>
                """ % error_items
        else:
            error_message = ""
        return error_message

    # Wrapper attributes
    def summary(self):
        return self.obj.description or ""

    def admin_metadata(self):
        # the following functionality will have to be restored in such a
        # way that we don't return admin messages to the frontend - later

        return u"%s<br /><em>Folder:</em> %s<br />%s" % (
            self.filetype() or "",
            self.folder_path(),
            self.errors()
            )

    def heading(self):
        return u"Files"

    def url(self):
        return self.obj.url


schema.register_wrapper(File, FileLinkWrapper)


class ImageLinkWrapper(FileLinkWrapper):
    def image(self):
        return self.obj

    def admin_metadata(self):
        return u"<em>Folder:</em> %s<br />%s" % (
            self.folder_path(),
            self.errors()
            )

schema.register_wrapper(Image, ImageLinkWrapper)


if 'form_designer' in settings.INSTALLED_APPS:
    from form_designer.models import FormDefinition

    schema.register(
        FormDefinition,
        search_fields=['title'],
        summary='body',
        )
