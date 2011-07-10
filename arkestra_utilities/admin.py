from django.db.models import ForeignKey
from widgetry import fk_lookup

from django.contrib import admin
from django import forms

from models import Insert

class AutocompleteMixin(object):
    class Media:
        js = (
            '/static/jquery/jquery.js', # we already load jquery for the tabs
            '/static/jquery/ui/ui.core.js',
            '/static/jquery/ui/ui.tabs.js',
        )
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


class InsertForm(forms.ModelForm):
    class Meta:
        model = Insert
        widgets = {'description': forms.Textarea(
              attrs={'cols':80, 'rows':5,},
            ),  
        }

from cms.admin.placeholderadmin import PlaceholderAdmin # if it's at the start of the file, it breaks imports somehow

class InsertAdmin(PlaceholderAdmin):
    pass
    
admin.site.register(Insert, InsertAdmin)
