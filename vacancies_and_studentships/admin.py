from django import forms
from django.contrib import admin, messages
from django.db.models import ForeignKey

from cms.admin.placeholderadmin import PlaceholderAdmin

from widgetry import fk_lookup
from widgetry.tabs.placeholderadmin import ModelAdminWithTabsAndCMSPlaceholder

from arkestra_utilities.widgets.wym_editor import WYMEditor
from arkestra_utilities import admin_tabs_extension
from arkestra_utilities.admin_mixins import GenericModelAdminMixin, InputURLMixin, fieldsets

from links.admin import ExternalLinkForm, get_or_create_external_link
from links.admin import ObjectLinkInline

from models import Vacancy, Studentship

class VacancyStudentshipForm(InputURLMixin):
    # a shared form for vacancies & studentships
    class Meta:
        widgets = {'summary': forms.Textarea(
              attrs={'cols':80, 'rows':2,},
            ),  
        }

    input_url = forms.CharField(max_length=255, required = False)
    
    def clean(self):
        super(VacancyStudentshipForm, self).clean()
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

class VacancyStudentshipAdmin(GenericModelAdminMixin, ModelAdminWithTabsAndCMSPlaceholder):
    # inlines = (ObjectLinkInline,)
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
        'please_contact',
        'publish_to', 
        )
    prepopulated_fields = {
        'slug': ('title',)
            }

    def _media(self):
        return super(AutocompleteMixin, self).media + super(ModelAdminWithTabsAndCMSPlaceholder, self).media
    media = property(_media)

        
class VacancyForm(VacancyStudentshipForm):
    class Meta(VacancyStudentshipForm.Meta):
        model = Vacancy
    
class VacancyAdmin(VacancyStudentshipAdmin):
    # def __init__(self):
    #     super(VacancyAdmin, self).__init__(self)
    #     search_fields.append('job_number')

    form = VacancyForm
    fieldset_vacancy = ('', {'fields': ('salary', 'job_number')})
        
    tabs = (
            ('Basic', {'fieldsets': (fieldsets["basic"], fieldsets["host"], fieldset_vacancy, fieldsets["image"], fieldsets["publishing_control"],)}),
            ('Date & significance', {'fieldsets': (fieldsets["closing_date"], fieldsets["importance"])}),
            ('Body', {'fieldsets': (fieldsets["body"],)}),
            ('Where to Publish', {'fieldsets': (fieldsets["where_to_publish"],),}),
            ('Please contact', {'fieldsets': (fieldsets["people"],)}),
            ('Links', {'inlines': (ObjectLinkInline,),}),
            ('Advanced Options', {'fieldsets': (fieldsets["url"], fieldsets["slug"],)}),        
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
        'please_contact',
    )

    fieldset_supervision = ('', {'fields': ('supervisors',)})
    tabs = (
            ('Basic', {'fieldsets': (fieldsets["basic"], fieldsets["host"], fieldsets["image"], fieldsets["publishing_control"],)}),
            ('Date & significance', {'fieldsets': (fieldsets["closing_date"], fieldsets["importance"])}),
            ('Body', {'fieldsets': (fieldsets["body"],)}),
            ('Where to Publish', {'fieldsets': (fieldsets["where_to_publish"],),}),
            ('Supervisors', {'fieldsets': (fieldset_supervision,)}),
            ('Please contact', {'fieldsets': (fieldsets["people"],)}),
            ('Links', {'inlines': (ObjectLinkInline,),}),
            ('Advanced Options', {'fieldsets': (fieldsets["url"], fieldsets["slug"],)}),        
        ) 

    # autocomplete fields
    related_search_fields = [
        'hosted_by',
        'please_contact',
        ]

admin.site.register(Vacancy,VacancyAdmin)
admin.site.register(Studentship,StudentshipAdmin)
