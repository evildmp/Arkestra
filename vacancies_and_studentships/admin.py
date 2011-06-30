import models
from django import forms
from django.contrib import admin

# for the WYMeditor fields
from arkestra_utilities.widgets.wym_editor import WYMEditor

# for tabbed interface
from arkestra_utilities import admin_tabs_extension
from django.db.models import ForeignKey
# for autocomplete search
#from arkestra_utilities.widgets.widgets import ForeignKeySearchInput
#from arkestra_utilities.views import search

from widgetry import fk_lookup
from links.admin import ObjectLinkInline

# for the plugin system
from cms.admin.placeholderadmin import PlaceholderAdmin

COMMON_SEARCH_FIELDS = ['short_title','title','summary','description','slug','url']

class StudentshipForm(forms.ModelForm):
    class Meta:
        model = models.Studentship        
    def clean(self):
        if not self.cleaned_data["short_title"] or self.cleaned_data["short_title"] == '':
            self.cleaned_data["short_title"] = self.cleaned_data["title"]
        #must have hosted-by or url
        if not self.cleaned_data["hosted_by"] and not self.cleaned_data["url"]:
            raise forms.ValidationError("A Host is required except for Studentships on external websites - please provide either a Host or a URL")                              
        return self.cleaned_data    

# class StudentshipAdmin(admin_tabs_extension.ModelAdminWithTabs):
class StudentshipAdmin(PlaceholderAdmin):
    search_fields = COMMON_SEARCH_FIELDS
    form = StudentshipForm
    list_display = ('short_title', 'hosted_by', 'closing_date',)
    filter_horizontal = (
        'publish_to', 
        'supervisors', 
    )
    inlines = (ObjectLinkInline,)
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
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(StudentshipAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    class Media:
        js = (
            '/static/cms/js/lib/jquery.js', # we already load jquery for the tabs
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra/js/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra/js/jquery/themes/base/ui.all.css',)
        }    
    
admin.site.register(models.Studentship,StudentshipAdmin)




class VacancyForm(forms.ModelForm):
    class Meta:
        model = models.Vacancy
    def clean(self):
        if not self.cleaned_data["short_title"] or self.cleaned_data["short_title"] == '':
            self.cleaned_data["short_title"] = self.cleaned_data["title"]
        #must have hosted-by or url
        if not self.cleaned_data["hosted_by"] and not self.cleaned_data["url"]:
            raise forms.ValidationError("A Host is required except for Vacancies on external websites - please provide either a Host or a URL")                  
        return self.cleaned_data    
    
# class VacancyAdmin(admin_tabs_extension.ModelAdminWithTabs):
class VacancyAdmin(PlaceholderAdmin):
    search_fields = COMMON_SEARCH_FIELDS + ['job_number']
    form = VacancyForm
    list_display = ('short_title', 'hosted_by', 'closing_date',)
    filter_horizontal = (
        'publish_to', 
    )
    inlines = (ObjectLinkInline,)
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
    # autocomplete fields
    related_search_fields = [
        'hosted_by',
        'please_contact',
        ]
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(VacancyAdmin, self).formfield_for_dbfield(db_field, **kwargs)     
    class Media:
        js = (
            '/static/cms/js/lib/jquery.js', # we already load jquery for the tabs
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra/js/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra/js/jquery/themes/base/ui.all.css',)
        }          
admin.site.register(models.Vacancy,VacancyAdmin)