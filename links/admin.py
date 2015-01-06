from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes import generic

from widgetry import fk_lookup

from treeadmin.admin import TreeAdmin

from chained_selectbox.forms import ChainedChoicesForm
from chained_selectbox.form_fields import ChainedChoiceField

from arkestra_utilities.admin_mixins import (
    AutocompleteMixin, SupplyRequestMixin,
    )

from links import schema
from links.models import (
    ObjectLink, ExternalLink, ExternalSite, LinkType
    )
from links.utils import check_urls
from links.views import DEFAULT_CHOICES


class LinkAdmin(admin.ModelAdmin, AutocompleteMixin):
    related_search_fields = ['destination_content_type']


class LinkItemForm(ChainedChoicesForm):

    # different destination_content_types need different link formatting options
    format = ChainedChoiceField(
        parent_field='destination_content_type',
        ajax_url='/chainedselectchoices'
        )

    def __init__(self, *args, **kwargs):
        super(LinkItemForm, self).__init__(*args, **kwargs)

        # if an object has already been saved for this LinkItem, get the correct link_format_choices
        if "instance" in kwargs:
            instance = kwargs['instance']

            destination_content_type = self.instance.destination_content_type.model_class()

            # get the appropriate choices from the wrapper
            choices = getattr(
                schema.get_wrapper(instance.destination_content_type.model_class()),
                "link_format_choices",
                DEFAULT_CHOICES
                )

            # find the field that we apply the choices to
            for field_name, field in self.fields.items():
                if hasattr(field, 'parent_field'):
                    field.choices = choices

        else:

            destination_content_type = None

        # look up the correct widget from the content type
        widget = fk_lookup.GenericFkLookup(
            'id_%s-destination_content_type' % self.prefix,
            destination_content_type,
            )
        self.fields['destination_object_id'].widget = widget
        self.fields['destination_content_type'].widget.choices = schema.content_type_choices()


class ObjectLinkInline(generic.GenericStackedInline):
    model = ObjectLink
    form = LinkItemForm
    extra = 3
    fieldsets = (
        (None, {
            'fields': (
                'destination_content_type', 'destination_object_id',
                # 'external_link_input_url',
                'text_override',
                ('format', 'key_link',),
            ),
        }),
        ('Overrides', {
            'fields': (
                'metadata_override',
                'heading_override',
                'summary_override',
                'html_title_attribute',
            ),
            'classes': ('collapse',),
        })
    )


class ExternalLinkForm(forms.ModelForm):
    class Meta:
        model = ExternalLink

    def clean(self):
        #  now that this is here, do we need all the checks Arkestra does?
        super(ExternalLinkForm, self).clean()
        url = self.cleaned_data.get('url', "")
        title = self.cleaned_data.get('title', "")

        check_urls(url)

        # check if the url is a duplicate
        # if the url exists, and this would be a new instance in the database,
        # it's a duplicate
        if self.Meta.model.objects.filter(url=url) and not self.instance.pk:
            message = "Sorry, this link appears to exist already"
            raise forms.ValidationError(message)

        # warn if the title is a duplicate
        # if the title exists, and this would be a new instance in the
        # database, it's a duplicate
        if self.Meta.model.objects.filter(title=title) and not self.instance.pk:
            message = """
                Warning: the link title %s already exists in the database -
                consider changing it.
                """ % title
            messages.add_message(self.request, messages.WARNING, message)

        return self.cleaned_data


class ExternalLinkAdmin(SupplyRequestMixin, admin.ModelAdmin):
    readonly_fields = ('external_site', 'kind',)
    search_fields = ('title', 'external_site__site', 'description', 'url')
    list_display = ('title', 'url', )
    form = ExternalLinkForm

    def save_model(self, request, obj, form, change):
        return super(ExternalLinkAdmin, self).save_model(
            request,
            obj,
            form,
            change
            )


class LinkTypeAdmin(admin.ModelAdmin):
    pass


class ExternalSiteForm(forms.ModelForm):
    class Meta:
        model = ExternalSite

    def clean(self):
        #  if the site isn't named, use the domain name
        super(ExternalSiteForm, self).clean()
        site = self.cleaned_data.get("site", None)
        domain = self.cleaned_data.get("domain", None)
        if not site:
            self.cleaned_data["site"] = domain
        return self.cleaned_data


class ExternalSiteAdmin(TreeAdmin):
    readonly_fields = ('parent',)
    form = ExternalSiteForm
    list_display = ('domain', 'site',)
    filter_include_ancestors = True


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
