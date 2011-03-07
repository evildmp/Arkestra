from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib import messages

from links.models import Link, ObjectLink, ExternalLink, GenericLinkListPluginItem, ExternalSite, LinkType


# imports for FK search box
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseNotFound
from django.db.models import ForeignKey
#from arkestra_utilities.widgets.widgets import ForeignKeySearchInput, GenericForeignKeySearchInput
#from arkestra_utilities.views import search
from widgetry import fk_lookup
from widgetry.views import search 

from django import forms

from django.conf import settings
#LINK_SCHEMA = getattr(settings, 'LINK_SCHEMA', {})

from links import schema
from urlparse import urlparse 
from urllib import urlopen
from django.core.exceptions import ObjectDoesNotExist

class LinkAdmin(admin.ModelAdmin):        
    related_search_fields = ['destination_content_type']
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(LinkAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class ObjectLinkInlineForm(forms.ModelForm):
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
    class Meta:
        model=ObjectLink
    
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

def validate_and_get_messages(url, external_url, title, description="", info=[], warnings=[]):
    if url:
        try:
            ExternalLink.objects.get(url=url)
            known_to_exist = True
        except ExternalLink.DoesNotExist:
            known_to_exist = False
        # set up some cleaned_data based on this instance
        external_link_form = ExternalLinkForm()
        external_link_form.cleaned_data = {}
        external_link_form.cleaned_data["url"]=url
        external_link_form.cleaned_data["title"]=title
        external_link_form.cleaned_data["description"]=description
        # go ahead and run the clean() 
        external_link_form.clean(allowed_schemes=["http"], known_to_exist = known_to_exist)
        # get the messages
        info.extend(external_link_form.info)
        warnings.extend(external_link_form.warnings)
        # if the link exists, get it, otherwise create it then get it
        external_url, created = ExternalLink.objects.get_or_create(url=url,
              defaults={'title': title, 'description': description})
        if created:
            info.append("A link to %s has been added to the External Links database." %url)
        else:
            info.append("A link to %s already existed in External Links database, so I've used that." %url)
    if external_url:
        info.append("This is an external item at %s" %external_url.url)
    else:
        external_url = None
    return info, warnings, external_url

class ExternalLinkForm(forms.ModelForm):
    class Meta:
        model = ExternalLink
    allowed_schemes = [kind.scheme for kind in LinkType.objects.all()]
    # sometimes other forms use this clean method, so we let them choose their own schemes
    def clean(self, allowed_schemes=allowed_schemes, known_to_exist = False):
        ExternalLinkForm.warnings = []
        ExternalLinkForm.info = []
        url = self.cleaned_data.get('url', "")
        title = self.cleaned_data.get('title', "")
        
        # check if the ul is a duplicate - we don't enforce this in models with unique = True because it makes it too hard to migrate from databases with duplicates
        print "ExternalLinkForm self.instance.pk", self.instance
        if self.Meta.model.objects.filter(url=url) and not known_to_exist and not self.instance.pk:
            message = "Sorry, this link appears to exist already"
            raise forms.ValidationError(message)

        # warn if the title is a duplicate
        if self.Meta.model.objects.filter(title=title) and not known_to_exist and not self.instance.pk:
            self.warnings.append("Warning: the link title %s already exists in the database - consider changing it." %title)
        # parse the url and get some attributes
        purl = urlparse(url)
        scheme = purl.scheme
        
        # make sure it's a kind we allow before anything else
        if not scheme in allowed_schemes:
            message = "Sorry, this link type is not permitted. Permitted types are: " + ", ".join(allowed_schemes)
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
            # if url_test.getcode() == 404:
            #     self.warnings.append("Warning: the link %s appears not to work. Please check that it is correct." %url)
            # check for a redirect
            if url_test.geturl() != url:
                self.warnings.append("Warning: your URL " + url + " doesn't match the site's, which is: " + url_test.geturl())
        
        # for mailto types only
        if str(scheme) == "mailto":
            self.warnings.append("Warning: this email address hasn't been checked. I hope it's correct.")

        return self.cleaned_data    

class ExternalLinkAdmin(admin.ModelAdmin):
    readonly_fields = ('external_site', 'kind',)
    search_fields = ('title', 'external_site__site','description', 'url')
    list_display = ('title', 'url', )
    form = ExternalLinkForm
    
    def response_change(self, request, obj):
        for message in ExternalLinkForm.warnings:
            messages.warning(request, message)
        for message in self.form.info:
            messages.info(request, message)
        return super(ExternalLinkAdmin, self).response_change(request, obj)


class LinkTypeAdmin(admin.ModelAdmin):
    pass

class ExternalSiteForm(forms.ModelForm):
    class Meta:
        model = ExternalSite
    def clean(self):
        # if the site isn't named, use the domain name
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
