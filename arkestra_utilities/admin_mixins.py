from django.db.models import ForeignKey
from django.conf import settings
from django import forms
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from cms.utils import cms_static_url

from widgetry import fk_lookup
from widgetry.tabs.placeholderadmin import ModelAdminWithTabsAndCMSPlaceholder

from contacts_and_people.models import Entity
from links.models import ExternalLink
from links.utils import get_or_create_external_link
    
class AutocompleteMixin(object):
    class Media:
        js = [
            cms_static_url('js/libs/jquery.ui.core.js'),
        ]
        css = {
            'all': ('/static/jquery/themes/base/ui.all.css',)
        }    

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if (isinstance(db_field, ForeignKey) and 
                db_field.name in self.related_search_fields):
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)          
        return super(AutocompleteMixin, self).formfield_for_dbfield(db_field, **kwargs)


class SupplyRequestMixin(object):
    def get_form(self, request, obj=None, **kwargs):
        form_class = super(SupplyRequestMixin, self).get_form(request, obj, **kwargs)
        form_class.request = request
        return form_class


class HostedByFilter(SimpleListFilter):
    title = _('hosting Entity')
    parameter_name = 'entity'

    def lookups(self, request, model_admin):
        return (
            ('my', _('My entities')),
            ('nobody', _('None')),
        )

    def queryset(self, request, queryset):
        entities = Entity.objects.all()
        myentities = entities.filter(people__in=request.user.person_user.all())
        if self.value() == 'my':
            return queryset.filter(hosted_by__in=myentities)
        if self.value() == 'nobody':
            return queryset.exclude(hosted_by__in=entities)

class GenericModelAdmin(AutocompleteMixin, SupplyRequestMixin, ModelAdminWithTabsAndCMSPlaceholder):

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "publish_to": 
            kwargs["queryset"] = Entity.objects.filter(website__published = True)
        return super(AutocompleteMixin, self).formfield_for_manytomany(db_field, request, **kwargs)


class InputURLMixin(forms.ModelForm): 
    # really this is simply acting as a base admin form for various models
    # but not just GenericModels:
    #
    #   PersonForm(InputURLMixin):
    #   EntityForm(InputURLMixin)
    #   LinkItemForm(InputURLMixin)
    #   GenericModelForm(InputURLMixin)
    #       NewsAndEventsForm(GenericModelForm)
    #           NewsArticleForm(NewsAndEventsForm)
    #           Event(NewsAndEventsForm)
    #       VacancyStudentshipForm(GenericModelForm)
    #           VacancyForm(VacancyStudentshipForm)
    #           StudentshipForm(VacancyStudentshipForm)
    #
    # when https://code.djangoproject.com/ticket/19617 is fixed 
    # probably by https://github.com/linovia/django/compare/master...forms_metaclasses_rationalization
    # we can do something nicer
    
    input_url = forms.CharField(max_length=255, required = False,
        help_text=u"<strong>External URL</strong> not found above? Enter a new one.", 
        )

class GenericModelForm(InputURLMixin):
    class Meta:
        widgets = {'summary': forms.Textarea(
              attrs={'cols':80, 'rows':2,},
            ),  
        }

    def clean(self):
        super(GenericModelForm, self).clean()

        # create the short_title automatically if necessary
        if not self.cleaned_data["short_title"] and self.cleaned_data.get("title"):
            if len(self.cleaned_data["title"]) > 70:
                raise forms.ValidationError("Please provide a short (less than 70 characters) version of the Title for the Short title field.")     
            else:
                self.cleaned_data["short_title"] = self.cleaned_data["title"]
                
        # check ExternalLink-related issues
        self.cleaned_data["external_url"] = get_or_create_external_link(self.request,
            self.cleaned_data.get("input_url", None), # a manually entered url
            self.cleaned_data.get("external_url", None), # a url chosen with autocomplete
            self.cleaned_data.get("title"), # link title
            self.cleaned_data.get("summary"), # link description
            )          

        # misc checks
        if not self.cleaned_data["external_url"]:
            if not self.cleaned_data["hosted_by"]:
                raise forms.ValidationError("A Host is required except for items on external websites - please provide either a Host or an External URL")      
            # must have body or url in order to be published
            if not self.instance and self.instance.body.cmsplugin_set.all():
            # if not self.cleaned_data["body"]:          
                message = u"This will not be published until either an external URL or Plugin has been added. Perhaps you ought to do that now."
                messages.add_message(self.request, messages.WARNING, message)

        return self.cleaned_data


fieldsets = {
    'basic': ('', {'fields': ('title',  'short_title', 'summary')}),
    'host': ('', {'fields': ('hosted_by',)}),
    'image': ('', {'fields': ('image',)}),
    'body':  ('', {
        'fields': ('body',),
        'classes': ('plugin-holder', 'plugin-holder-nopage',)
        }),
    'where_to_publish': ('', {'fields': ('publish_to',)}),
    'people': ('People to contact about this item', {'fields': ('please_contact',)}),
    'publishing_control': ('Publishing control', {'fields': ('published', 'in_lists')}),
    'date': ('', {'fields': ('date',)}),
    'date': ('', {'fields': ('date',)}),
    'importance': ('', {'fields': ('importance',)}),
    'url': ('If this is an external item', {'fields': ('external_url', 'input_url',)}),         
    'slug': ('If this is an internal item', {'fields': ('slug',)}),
    'location': ('', {'fields': ('precise_location', 'access_note',)}),
    'address_report': ('', {'fields': ('address_report',)}),
    'email': ('', {'fields': ('email',)}),
    }