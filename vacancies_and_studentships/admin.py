from django import forms
from django.contrib import admin, messages
from django.db.models import ForeignKey

from cms.admin.placeholderadmin import PlaceholderAdmin

from widgetry import fk_lookup

from arkestra_utilities.widgets.wym_editor import WYMEditor
from arkestra_utilities import admin_tabs_extension
from arkestra_utilities.mixins import SupplyRequestMixin, AutocompleteMixin

from links.admin import ExternalLinkForm, get_or_create_external_link
from links.admin import ObjectLinkInline

from models import Vacancy, Studentship

class VacancyStudentshipForm(forms.ModelForm):
    # a shared form for vacancies & studentships
    class Meta:
        widgets = {'summary': forms.Textarea(
              attrs={'cols':80, 'rows':2,},
            ),  
        }

    input_url = forms.CharField(max_length=255, required = False)
    
    def clean(self):
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
                message = "This vacancy is not Hosted by and Entity and has no External URL. Are you sure you want to do that?"
                messages.add_message(self.request, messages.WARNING, message)
            # must have content or url in order to be published
            # not currently working, because self.cleaned_data["body"] = None
            # if not self.cleaned_data["body"]:          
            #     message = "This will not be published until either an external URL or Plugin has been added. Perhaps you ought to do that now."
            #     messages.add_message(self.request, messages.WARNING, message)
        return self.cleaned_data

class VacancyStudentshipAdmin(AutocompleteMixin, SupplyRequestMixin, PlaceholderAdmin):
    inlines = (ObjectLinkInline,)
    exclude = ('description', 'url',)
    search_fields = ['short_title','title','summary', 'slug','url']
    list_display = ('short_title', 'hosted_by', 'closing_date',)
    list_display = ('short_title', 'closing_date', 'hosted_by',)
    related_search_fields = [
        'hosted_by',
        'please_contact',
        'external_url',
        ]
    filter_horizontal = (
        'enquiries',
        'publish_to', 
        )
    prepopulated_fields = {
        'slug': ('title',)
            }

class VacancyForm(VacancyStudentshipForm):
    class Meta(VacancyStudentshipForm.Meta):
        model = Vacancy
    
class VacancyAdmin(VacancyStudentshipAdmin):
    # def __init__(self):
    #     super(VacancyAdmin, self).__init__(self)
    #     search_fields.append('job_number')

    form = VacancyForm
    fieldset_basic = (
        ('', {
            'fields': (('title', 'short_title',), 'closing_date', 'salary', 'job_number',),
        }),
        ('', {
            'fields': ('summary',),
        }),
        ('', {
            'fields': ('description',),
        }),
    )
    fieldset_institution = (
        ('Institutional details', {
            'fields': ('hosted_by',)
        }), 
    )
    fieldset_furtherinfo = (
        ('', {
            'fields': ('please_contact', 'also_advertise_on',)
        }),
    )
    fieldset_advanced = (
        ('', {
            'fields': ('url', 'slug',),
        }),
    )
    tabs = (
        ('Basic', {'fieldsets': fieldset_basic,}),
        ('Institution', {'fieldsets': fieldset_institution,}),
        ('Further Information', {'fieldsets': fieldset_furtherinfo,}),
        ('Links', {'inlines': ('ObjectLinkInline',),}),
        ('Advanced Options', {'fieldsets': fieldset_advanced,}),        
    ) 
         

class StudentshipForm(VacancyStudentshipForm):
    class Meta(VacancyStudentshipForm.Meta):
        model = Studentship        


# class StudentshipAdmin(admin_tabs_extension.ModelAdminWithTabs):
class StudentshipAdmin(VacancyStudentshipAdmin):
    form = StudentshipForm
    filter_horizontal = (
        'publish_to', 
        'supervisors', 
        'enquiries',
    )
    fieldset_basic = (
        ('', {
            'fields': (('title', 'short_title',),  'closing_date',),
        }),
        ('', {
            'fields': ('summary',),
        }),
        ('', {
            'fields': ('description',),
        }),
    )
    fieldset_supervision = (
        ('', {
            'fields': ('supervisors','hosted_by',)
        }), 
    )
    fieldset_where_to_publish = (
        ('', {
            'fields': ('please_contact', 'also_advertise_on',)
        }),
    )
    fieldset_advanced = (
        ('', {
            'fields': ('url', 'slug',),
        }),
    )
    tabs = (
        ('Basic', {'fieldsets': fieldset_basic,}),
        ('Where to Publish', {'fieldsets': fieldset_where_to_publish,}),
        ('Supervision', {'fieldsets': fieldset_supervision,}),
        ('Links', {'inlines': ('ObjectLinkInline',),}),
        ('Advanced Options', {'fieldsets': fieldset_advanced,}),        
    )    
    # autocomplete fields
    related_search_fields = [
        'hosted_by',
        'please_contact',
        ]

admin.site.register(Vacancy,VacancyAdmin)
admin.site.register(Studentship,StudentshipAdmin)
