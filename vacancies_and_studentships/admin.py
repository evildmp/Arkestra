import models
from django import forms
from django.contrib import admin

from widgetry import fk_lookup
from links.admin import ObjectLinkInline

# for the plugin system
from cms.admin.placeholderadmin import PlaceholderAdmin

from arkestra_utilities.admin import SupplyRequestMixin, AutocompleteMixin

COMMON_SEARCH_FIELDS = ['short_title','title','summary','description','slug','url']


class VacancyStudentshipForm(forms.ModelForm):
    input_url = forms.CharField(max_length=255, required=False)
    
    class Meta:
        widgets = {'summary': forms.Textarea(
              attrs={'cols':80, 'rows':2,},
            ),  
        }
    
    def clean(self):
        if not self.cleaned_data["short_title"] or self.cleaned_data["short_title"] == '':
            self.cleaned_data["short_title"] = self.cleaned_data["title"]
        #must have hosted-by or url
        if not self.cleaned_data["hosted_by"] and not self.cleaned_data["url"]:
            raise forms.ValidationError("A Host is required except for items on external websites - please provide either a Host or a URL")                              
        return self.cleaned_data    


class VacancyStudentshipAdmin(AutocompleteMixin, SupplyRequestMixin, admin.ModelAdmin):
    exclude = ('description', 'url',)
    search_fields = COMMON_SEARCH_FIELDS
    list_display = ('short_title', 'hosted_by', 'closing_date',)
    inlines = (ObjectLinkInline,)
    related_search_fields = [
        'hosted_by',
        'please_contact',
        'external_url',
        ]
    filter_horizontal = (
        'publish_to', 
        'enquiries',
    )


class VacancyForm(VacancyStudentshipForm):
    class Meta(VacancyStudentshipForm.Meta):
        model = models.Vacancy
    

# class VacancyAdmin(admin_tabs_extension.ModelAdminWithTabs):
class VacancyAdmin(PlaceholderAdmin, VacancyStudentshipAdmin):
    search_fields = COMMON_SEARCH_FIELDS + ['job_number']
    form = VacancyForm
    prepopulated_fields = {
        'slug': ('title',)
            }
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
         

admin.site.register(models.Vacancy,VacancyAdmin)


class StudentshipForm(VacancyStudentshipForm):
    class Meta(VacancyStudentshipForm.Meta):
        model = models.Studentship        


# class StudentshipAdmin(admin_tabs_extension.ModelAdminWithTabs):
class StudentshipAdmin(PlaceholderAdmin, VacancyStudentshipAdmin):
    form = StudentshipForm
    filter_horizontal = (
        'publish_to', 
        'supervisors', 
        'enquiries',
    )
    prepopulated_fields = {
        'slug': ('title',)
            }
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
    
admin.site.register(models.Studentship,StudentshipAdmin)
