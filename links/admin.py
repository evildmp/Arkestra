from urlparse import urlparse 
from urllib import urlopen

from django import forms
from django.db.models import ForeignKey
from django.contrib import admin, messages
from django.contrib.contenttypes import generic

from widgetry import fk_lookup
from widgetry.views import search 

from arkestra_utilities.admin_mixins import AutocompleteMixin, SupplyRequestMixin

from links.models import ObjectLink, ExternalLink, ExternalSite, LinkType
from links import schema

#LINK_SCHEMA = getattr(settings, 'LINK_SCHEMA', {})

class LinkAdmin(admin.ModelAdmin, AutocompleteMixin):        
    related_search_fields = ['destination_content_type']


class ObjectLinkInlineForm(forms.ModelForm):
    class Meta:
        model=ObjectLink
        
    def __init__(self, *args, **kwargs):
        super(ObjectLinkInlineForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            if self.instance.destination_content_type:
                destination_content_type = self.instance.destination_content_type.model_class()
        else:
            destination_content_type = None
        #self.fields['destination_object_id'].widget = GenericForeignKeySearchInput(LINK_SCHEMA, 'id_%s-destination_content_type' % self.prefix, destination_content_type)
        self.fields['destination_object_id'].widget = fk_lookup.GenericFkLookup('id_%s-destination_content_type' % self.prefix, destination_content_type)
        self.fields['destination_content_type'].widget.choices = schema.content_type_choices()


class ObjectLinkAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('destination_content_type', 'destination_object_id',),
            }),
        ('Additional options', {
            'fields': ('text_override', 'description_override', 'html_title_attribute',), 
            'classes': ('collapse',),
            }),
        )


class ObjectLinkInline(generic.GenericStackedInline):
    model = ObjectLink
    form = ObjectLinkInlineForm
    extra = 3
    fieldsets = (
        (None, {
            'fields': (
                'destination_content_type', 'destination_object_id',
                ('include_description'),
            ),
        }),
        ('Overrides', {
            'fields': ('metadata_override', 'heading_override', 'text_override','description_override', 'html_title_attribute',
            ),
            'classes': ('collapse',),
        })
    )


def get_or_create_external_link(request, input_url, external_url, title, description=""):
    """
    When provided with candidate attributes for an ExternalLink object, will:
    * return the URL of an ExternalLink that matches
    * create an ExternalLink if there's no match, then return its URL
    """
    if input_url or external_url:
        # run checks - doesn't return anything 
        check_urls(request, input_url or external_url.url, ["https", "http"])

    if external_url:
        message = "This is an external item: %s." % external_url.url
        messages.add_message(request, messages.INFO, message)
        
        if input_url:
            message = "You can't have both External URL and Input URL fields, so I have ignored your Input URL."
            messages.add_message(request, messages.WARNING, message)


    elif input_url:
        # get or create the external_link based on the url
        external_url, created = ExternalLink.objects.get_or_create(url=input_url, defaults = {
            "url": input_url,
            "title": title,
            "description": description,
        })

        if created:
            message = "A link for this item has been added to the External Links database: %s." % external_url.url
            messages.add_message(request, messages.INFO, message)
        else:
            message = "Using existing External Link: %s." % external_url.url
            messages.add_message(request, messages.INFO, message)


    return external_url

def check_urls(request, url, allowed_schemes = None):
    """
    Checks and reports on a URL that might end up in the database
    """
    allowed_schemes = allowed_schemes or [kind.scheme for kind in LinkType.objects.all()]
    # parse the url and get some attributes
    purl = urlparse(url)
    scheme = purl.scheme
    
    # make sure it's a kind we allow before anything else
    if not scheme in allowed_schemes:
        permitted_schemes = (", ".join(allowed_schemes[:-1]) + " and " + allowed_schemes[-1]) if len(allowed_schemes) > 1 else allowed_schemes[0]
        if scheme:
            message = "Sorry, link type %s is not permitted. Permitted types are %s." % (scheme, permitted_schemes)
        else:
            message = 'Please provide a complete URL, such as "http://example.com/" or "mailto:example@example.com". Permitted schemes are %s.' % permitted_schemes

        raise forms.ValidationError(message)
    
    # for hypertext types only
    if str(scheme) == "http" or scheme == "https":
        # can we reach the domain?
        try:
            url_test = urlopen(url)
        except IOError:
            message = "Hostname " + purl.netloc + " not found. Please check that it is correct."
            raise forms.ValidationError(message)

        # check for a 404 (needs python 2.6)
        try:
            code = url_test.getcode()
        except AttributeError:
            message = "Warning: I couldn't check your link %s. Please check that it works." %url
            messages.add_message(request, messages.WARNING, message)            
        else:
            if code == 404:
                message = "Warning: the link %s appears not to work. Please check that it is correct." %url
                messages.add_message(request, messages.WARNING, message)            
        
        # check for a redirect
        if url_test.geturl() != url:
            message = "Warning: your URL " + url + " doesn't match the site's, which is: " + url_test.geturl()
            messages.add_message(request, messages.WARNING, message)            
        
    # for mailto types only
    elif str(scheme) == "mailto":
        message = "Warning: this email address hasn't been checked. I hope it's correct."
        messages.add_message(request, messages.WARNING, message)

class ExternalLinkForm(forms.ModelForm):
    class Meta:
        model = ExternalLink

    def clean(self):
        super(ExternalLinkForm, self).clean() # now that this is here, do we need all the checks Arkestra does?
        url = self.cleaned_data.get('url', "")
        title = self.cleaned_data.get('title', "")

        check_urls(self.request, url)
        
        # check if the url is a duplicate
        # if the url exists, and this would be a new instance in the database, it's a duplicate
        if self.Meta.model.objects.filter(url=url) and not self.instance.pk:
            message = "Sorry, this link appears to exist already"
            raise forms.ValidationError(message)

        # warn if the title is a duplicate
        # if the title exists, and this would be a new instance in the database, it's a duplicate        
        if self.Meta.model.objects.filter(title=title) and not self.instance.pk:
            message = "Warning: the link title %s already exists in the database - consider changing it." %title
            messages.add_message(self.request, messages.WARNING, message)

        return self.cleaned_data    


class ExternalLinkAdmin(SupplyRequestMixin, admin.ModelAdmin):
    readonly_fields = ('external_site', 'kind',)
    search_fields = ('title', 'external_site__site','description', 'url')
    list_display = ('title', 'url', )
    form = ExternalLinkForm

    def save_model(self, request, obj, form, change):
        return super(ExternalLinkAdmin, self).save_model(request, obj, form, change)


class LinkTypeAdmin(admin.ModelAdmin):
    pass


class ExternalSiteForm(forms.ModelForm):
    class Meta:
        model = ExternalSite
        
    def clean(self):
        super(ExternalSiteForm, self).clean()        # if the site isn't named, use the domain name
        site = self.cleaned_data.get("site", None)
        domain = self.cleaned_data.get("domain", None)
        if not site:
            self.cleaned_data["site"] = domain
        return self.cleaned_data    


class ExternalSiteAdmin(admin.ModelAdmin):
    readonly_fields = ('parent',)
    form = ExternalSiteForm
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
                'root_domains': ExternalSite.objects.filter(level = 0),
                # 'has_add_permission': request.user.has_perm('links.add_link'),
                # 'has_change_permission': request.user.has_perm('links.change_link'),
                # 'has_delete_permission': request.user.has_perm('links.delete_link'),
        })
        return super(ExternalSiteAdmin, self).changelist_view(request, extra_context)

    
#admin.site.register(ObjectLink, ObjectLinkAdmin)
admin.site.register(ExternalLink, ExternalLinkAdmin)
admin.site.register(ExternalSite, ExternalSiteAdmin)
admin.site.register(LinkType, LinkTypeAdmin)

"""
# patch the cms page admin to show generic links
if getattr(settings,'SHOW_GENERIC_LINKS_INLINE_FOR_CMS_PAGE_ADMIN', False):
    from cms.admin.pageadmin import PageAdmin
    from cms.models import Page
    admin.site.unregister(Page)
    print dir(admin.site)
    if not hasattr(PageAdmin,'inlines'):
        PageAdmin.inlines = []
    else:
        PageAdmin.inlines = list(PageAdmin.inlines)
    PageAdmin.inlines = PageAdmin.inlines + [ObjectLinkInline]
    admin.site.register(Page, PageAdmin)
"""
