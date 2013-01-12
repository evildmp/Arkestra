from django.db.models import ForeignKey
from django.conf import settings
from django import forms

from cms.utils import cms_static_url

from widgetry import fk_lookup

from contacts_and_people.models import Entity
    
    


class AutocompleteMixin(object):
    class Media:
        js = [
            # '/static/jquery/jquery.min.js',
            settings.ADMIN_MEDIA_PREFIX + 'js/jquery.min.js',
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


class GenericModelAdminMixin(AutocompleteMixin, SupplyRequestMixin):
    # this doesn't work - it doesn't feed the Autocomplete with the desired items

    # def formfield_for_foreignkey(self, db_field, request, **kwargs): 
    #     """
    #     Filters the list of Entities so that the user only sees those that
    #     have published websites
    #     """
    #     if db_field.name == "hosted_by":
    #         print "checking hosted_bys", kwargs
    #         kwargs["queryset"] = Entity.objects.filter(website__published = True)
    #         print "***", kwargs["queryset"].count()
    #     return super(GenericModelAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "publish_to": 
            # print "&&&&", Entity.objects.filter().count()
            kwargs["queryset"] = Entity.objects.filter(website__published = True)
        return super(AutocompleteMixin, self).formfield_for_manytomany(db_field, request, **kwargs)



class InputURLMixin(forms.ModelForm):
    input_url = forms.CharField(max_length=255, required = False,
        help_text=u"<strong>External URL</strong> not found above? Enter a new one.", 
        )



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
    'closing_date': ('', {'fields': ('closing_date',)}),
    'importance': ('', {'fields': ('importance',)}),
    'url': ('If this is an external item', {'fields': ('external_url', 'input_url',)}),         
    'slug': ('If this is an internal item', {'fields': ('slug',)}),
    'location': ('', {'fields': ('precise_location', 'access_note',)}),
    'address_report': ('', {'fields': ('address_report',)}),
    'email': ('', {'fields': ('email',)}),
    }