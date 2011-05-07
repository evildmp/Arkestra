import operator
from django.conf.urls.defaults import patterns

from django.db.models.query import QuerySet
from django.db.models import get_model
from django.db.models import ForeignKey
from django.db.models import F
from django.db.models import Q

from django.conf import settings

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from django import forms
from django.forms import ValidationError

from django.utils.safestring import mark_safe 
from django.utils.encoding import smart_str
from django.utils.encoding import smart_unicode

from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseNotFound

# from arkestra_utilities import admin_tabs_extension
from arkestra_utilities.widgets.combobox import ComboboxField
from widgetry import fk_lookup
# from widgetry.tabs.admin import ModelAdminWithTabs

from contacts_and_people import models

from links.admin import ExternalLinkForm, validate_and_get_messages
from links.models import ExternalLink
from links.admin import ObjectLinkInline

from cms.admin.placeholderadmin import PlaceholderAdmin
# for the WYMeditor fields
from arkestra_utilities.widgets.wym_editor import WYMEditor


HAS_PUBLICATIONS = 'publications' in settings.INSTALLED_APPS
if HAS_PUBLICATIONS:
    from publications.admin import ResearcherInline

# ------------------------- Membership admin -------------------------
class MembershipForm(forms.ModelForm): # cleans up membership & role information
    class Meta:
        model = models.Membership

class MembershipInline(admin.TabularInline): # for all membership inline admin
    form = MembershipForm    
    model = models.Membership
    extra = 1
    #order = forms.IntegerField(widget=forms.RadioSelect)
    related_search_fields = {
        'person': ('surname',),
        'entity': ('name',),
    }
    editable_search_fields = (
        'person','entity',
        )
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey):
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(MembershipInline, self).formfield_for_dbfield(db_field, **kwargs)

class MembershipForEntityInline(MembershipInline): # for Entity admin
    exclude = ('importance_to_person', 'display_role')
    extra = 3

class MembershipForPersonInline(MembershipInline): # for Person admin
    exclude = ('importance_to_entity', 'display_role')
    
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('person', 'entity', 'importance_to_person', 'importance_to_entity',)
    ordering = ['person',]
    form = MembershipForm
    #radio_fields = {"order": admin.HORIZONTAL, }
    related_search_fields = [
        'person',
        'entity',
    ]
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(MembershipAdmin, self).formfield_for_dbfield(db_field, **kwargs)


# ------------------------- Phone contact admin -------------------------

class PhoneContactInlineForm(forms.ModelForm):
    class Meta:
        model = models.PhoneContact
    label = ComboboxField(label = "label", choices=models.PhoneContact.LABEL_CHOICES, required=False)
    country_code = forms.CharField(label="Country code", widget=forms.TextInput(attrs={'size':'4'}))
    area_code = forms.CharField(label="Area code", widget=forms.TextInput(attrs={'size':'5'}))
    number = forms.CharField(label="Number", widget=forms.TextInput(attrs={'size':'10'}))
    internal_extension = forms.CharField(label="Internal extension", widget=forms.TextInput(attrs={'size':'6'}), required=False)

class PhoneContactInline(generic.GenericTabularInline):
    extra = 3
    model = models.PhoneContact
    form = PhoneContactInlineForm

class PhoneContactAdmin(admin.ModelAdmin):
    pass

    
# ------------------------- PersonLite admin -------------------------

class PersonLiteForm(forms.ModelForm):
    model = models.PersonLite

    def clean(self):
        if hasattr(self.instance, "person"):
            raise forms.ValidationError(mark_safe(u"A PersonLite who is also a Person must be edited using the Person Admin Interface"))
        return self.cleaned_data    

        
class PersonLiteAdmin(admin.ModelAdmin):
    search_fields = ('surname', 'given_name',)
    form = PersonLiteForm

    def save_model(self, request, obj, form, change):
        """
          OVERRIDING
          If this PersonLite object is infact also a Person object, you cannot ammend it via PersonLiteAdmin
          If PersonLiteForm.clean() is doing its job, it shouldn't be possible to reach the else statement
        """
        if not hasattr(obj, "person"):         
            obj.save()
        else:
            print "***ERROR: See",type(self), ".save_model()"
          
admin.site.register(models.PersonLite, PersonLiteAdmin)     
    
    
    
# ------------------------- Person admin -------------------------

"""
Not for v1.0
class TeacherInline(admin.StackedInline):
    model = models.Teacher
"""

class PersonForm(forms.ModelForm):
    model = models.Person
    input_url = forms.CharField(max_length=255, required = False)

    def __init__(self, *args, **kwargs):
        # disable the user combo if a user aleady has been assigned
        super(PersonForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id and instance.user:
            self.fields['user'].widget = DisplayUsernameWidget()
            self.fields['user'].help_text = "Once a user has been assigned, it cannot be changed"       
    def clean_please_contact(self):
        data = self.cleaned_data['please_contact']
        # only do the check when in "change" mode. there can't be a loop if in "new" mode
        # because nobody can link to us if we did not exist yet before.
        if hasattr(self, 'instance') and type(self.instance) == type(data):
            self.instance.please_contact = data
            has_loop_error, person_list = self.instance.check_please_contact_has_loop(self.instance)
            if has_loop_error:
                r = []
                for p in person_list:
                    r.append(u'"%s"' % p)
                r = u' &rarr; '.join(r)    
                raise forms.ValidationError(mark_safe(u"Please prevent loops: %s" % r))
        return data
    class Media:
        js = (
            '/media/cms/js/lib/ui.sortable.js',
            '/media/jquery/menu-sort-people.js',
            )

    def clean(self):
        self.warnings = []
        self.info = []

        # if this person has an external url, we need to do all kinds of things with it
        title = self.cleaned_data["title"] or ""
        link_title = " ".join(name_part for name_part in [str(title), self.cleaned_data["given_name"], self.cleaned_data["surname"]] if name_part)
        self.info, self.warnings, self.cleaned_data["external_url"]= validate_and_get_messages(
            self.cleaned_data.get("input_url", None), # a manually entered url
            self.cleaned_data.get("external_url", None), # a url chosen with autocomplete
            link_title, # link title
            "", # link description
            self.info, 
            self.warnings,
            )          
        return self.cleaned_data
        
class PersonAdmin(PlaceholderAdmin):

    search_fields = ['given_name','surname','institutional_username',]
    inlines = [MembershipForPersonInline, PhoneContactInline, ObjectLinkInline,]
    if HAS_PUBLICATIONS:
        inlines.append(ResearcherInline)
    form = PersonForm
    list_display = ( 'surname', 'given_name', 'image', 'get_entity', 'slug')
    #list_editable = ('user',)
    filter_horizontal = ('entities',)
    prepopulated_fields = {'slug': ('title', 'given_name', 'middle_names', 'surname',)}
    personal_fieldsets = (
        ('Name and image', {
            'fields': (('title','image',), ('given_name', 'middle_names', 'surname',),),
        }),
        ('Contact information', {
            'fields': ('email',
                       ('precise_location','access_note',), 
                      ),
        }),
        ('Over-ride default output', {
            'fields': ('please_contact',
                       ('override_entity', 'building',),
                      ),
        }),
        (None, {
            'fields': ('about',)
        })
    )
    advanced_fieldsets = (
        ('Advanced options', {
            #'classes': ('collapse',),
            'fields': ('active', 'user', 'institutional_username', 'slug', 'url',),
        }),
    )
    tabs = (
        ('Personal', {
                      'fieldsets': personal_fieldsets,
                      'inlines': ('PhoneContactInline',),
                      }),
        ('Advanced Options', {
                      'fieldsets': advanced_fieldsets,
                      }),
        ('Memberships', {'inlines': ('MembershipForPersonInline',)}),
        ('Researcher', {'inlines': ('ResearcherInline',)}),
    )
    class Media:
        js = (
            '/media/cms/js/lib/jquery.js',
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra/js/jquery/ui/ui.tabs.js',
        )
        css = {
             'all': ('/media/arkestra/js/jquery/themes/base/ui.all.css',)
        }
    related_search_fields = {
            'please_contact': ('surname',),
            'override_entity': ('name',),
            'user': ('username','first_name','last_name',),
            'building': ('name', 'number', 'street', 'postcode', 'site__site_name',),
        }
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(PersonAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
class TitleAdmin(admin.ModelAdmin):
    pass

class DisplayUsernameWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        user = User.objects.get(pk=value)
        default = super(DisplayUsernameWidget,self).render(name, value, attrs)
        return mark_safe(u'<span>Assigned user: <strong>%s</strong></span><div style="display: none;">%s</div>' % (user,default))

        
        
# ------------------------- EntityLite admin -------------------------

class EntityLiteForm(forms.ModelForm):
    model = models.EntityLite

    def clean(self):
        if hasattr(self.instance, "entity"):
            raise forms.ValidationError(mark_safe(u"An EntityLite who is also a full Entity must be edited using the Entity Admin Interface"))
        return self.cleaned_data    

        
class EntityLiteAdmin(admin.ModelAdmin):
    form = EntityLiteForm

    def save_model(self, request, obj, form, change):
        """
          OVERRIDING
          If this EntityLite object is infact also an Entity object, you cannot ammend it via EntityLiteAdmin
          If EntityLiteForm.clean() is doing its job, it shouldn't be possible to reach the else statement
        """
        if not hasattr(obj, "entity"):         
            obj.save()
        else:
            print "***ERROR: See",type(self), ".save_model()"
          
admin.site.register(models.EntityLite, EntityLiteAdmin)          
        
# ------------------------- Entity admin -------------------------

class EntityForm(forms.ModelForm):
    model = models.Entity
    def clean(self):
        print "in clean of EntityForm(forms.ModelForm"
        EntityForm.messages = []
        if not self.cleaned_data["website"]:
            self.messages.append("This entity doesn't have a home page. Are you sure you want to do that?")
        if not self.cleaned_data["short_name"]:
            self.cleaned_data["short_name"] = self.cleaned_data["name"]
        return self.cleaned_data 

class EntityAdmin(admin.ModelAdmin): 
    search_fields = ['name']
    inlines = (MembershipForEntityInline,PhoneContactInline)
    form = EntityForm
    list_display = ('name', 'parent', 'building', 'abstract_entity','website', )
    list_editable = ('website', )
    change_list_template = "admin/contacts_and_people/entity/change_list.html"
    prepopulated_fields = {
            'slug': ('name',)
            }
    tab_basic = (
            ('', {
                'fields': (('name', 'short_name','image',), 'abstract_entity', ('parent', 'display_parent',), ),
            }),
        )
    tab_contact = (
            ('', {
                'fields': (('website', 'email',), ('building', 'precise_location',), 'access_note', )
            }),
        )
    tab_advanced = (
            ('', {
                'fields': ('slug', 'url',)
            }),
        )
    tab_automatic_pages = [
            ('Contacts', {
                'fields': (('auto_contacts_page', 'contacts_page_menu_title',),)
            }),
            ]
    if "news_and_events" in settings.INSTALLED_APPS:
          tab_automatic_pages.append(  
            ('News', {
                'fields': (('auto_news_page', 'news_page_menu_title',),),
            }),)
    if "vacancies_and_studentships" in settings.INSTALLED_APPS:
          tab_automatic_pages.append(  
            ('Vacancies', {
                'fields': (('auto_vacancies_page', 'vacancies_page_menu_title',),)
            }),)
    if 'publications' in settings.INSTALLED_APPS:
          tab_automatic_pages.append(  
                ('Publications', {
                    'fields': (('auto_publications_page', 'publications_page_menu_title',),)
                }),)
    tabs = (
            ('Basic information', {'fieldsets':tab_basic}),
            ('Contact information', {'fieldsets':tab_contact,'inlines':('PhoneContactInline',)}),
            ('Advanced options', {'fieldsets':tab_advanced}),
            ('Automatic pages', {'fieldsets':tab_automatic_pages}),
            ('Memberships', {'inlines':('MembershipForEntityInline',)}),
        )
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
                'root_entities':models.Entity.objects.filter(level=0),
                'has_add_permission': request.user.has_perm('contacts_and_people.add_entity'),
                'has_change_permission': request.user.has_perm('contacts_and_people.change_entity'),
                'has_delete_permission': request.user.has_perm('contacts_and_people.delete_entity'),
        })
        return super(EntityAdmin, self).changelist_view(request, extra_context)
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(EntityAdmin, self).get_urls()
        
        # helper for url pattern generation
        info = "%sadmin_%s_%s" % (self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name)
        #pat = lambda regex, fn: url(regex, self.admin_site.admin_view(fn), name='%s_%s' % (info, fn.__name__))
        
        url_patterns = patterns('',
            url(r'^([0-9]+)/move-page/$', self.admin_site.admin_view(self.move_entity), name='%s_%s' % (info, 'move_page') ),
            #pat(r'^([0-9]+)/move-page/$', self.move_entity),
        )
        url_patterns.extend(urls)
        return url_patterns
    def move_entity(self, request, entity_id, extra_context=None):
        target = request.POST.get('target', None)
        position = request.POST.get('position', None)
        if target is None or position is None:
            return HttpResponseRedirect('../../')            
        try:
            entity = self.model.objects.get(pk=entity_id)
            target = self.model.objects.get(pk=target)
        except self.model.DoesNotExist:
            return HttpResponse("error")
            
        # does he haves permissions to do this...?
        if not request.user.has_perm('contacts_and_people.change_entity'):
            return HttpResponse("Denied")
        # move page
        entity.move_to(target, position)
        entity.save()
        return HttpResponse("ok")
    class Media:
        js = (
            '/media/cms/js/lib/jquery.js',
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra/js/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra/js/jquery/themes/base/ui.all.css',)
        }        
    related_search_fields = ['parent', 'building', 'website',]
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(EntityAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    

# ------------------------- Building and site admin -------------------------

class BuildingAdminForm(forms.ModelForm):
    class Meta:
        model = models.Building
    # getting_here = forms.CharField(widget=WYMEditor, required = False)
    # access_and_parking = forms.CharField(widget=WYMEditor, required = False)
    def clean(self):
        if self.cleaned_data["number"] and not self.cleaned_data["street"]:
            raise forms.ValidationError("Silly. You can't have a street number but no street, can you?")
        if self.cleaned_data["additional_street_address"] and not self.cleaned_data["street"]:
            self.cleaned_data["street"] = self.cleaned_data["additional_street_address"]
            self.cleaned_data["additional_street_address"] = None
        if not (self.cleaned_data["postcode"] or self.cleaned_data["name"] or self.cleaned_data["street"]):
            raise forms.ValidationError("That's not much of an address, is it?")
        return self.cleaned_data

class BuildingInline(admin.StackedInline):
    model = models.Building
    extra = 1

class SiteAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'post_town', 'country',)
    # inlines = (BuildingInline,) # not working for some reason - can't render the inlines
    tabs = (
            ('General', {
                    'fieldsets': (
                        ('hello', {
                            'fields': ('site_name', ('post_town','country',),'description', 'image'),
                        }),
                    ),
            }),
            ('Buildings', {
                    'inlines': ('BuildingInline',),
            }),
    )
    class Media:
        js = (
            '/media/cms/js/lib/jquery.js',
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra/js/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra/js/jquery/themes/base/ui.all.css',)
        }

class BuildingAdmin(PlaceholderAdmin):
    search_fields = ['name','number','street','postcode','site__site_name']
    form = BuildingAdminForm
    class Media:
        js = (
            '/media/cms/js/lib/jquery.js', # we already load jquery for the tabs
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra/js/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra/js/jquery/themes/base/ui.all.css',)
        }

admin.site.register(models.Person,PersonAdmin)
admin.site.register(models.Building,BuildingAdmin)
admin.site.register(models.Entity,EntityAdmin)
admin.site.register(models.Site,SiteAdmin)
admin.site.register(models.Title,TitleAdmin)
admin.site.register(models.Membership,MembershipAdmin)
admin.site.register(models.PhoneContact,PhoneContactAdmin)

# ------------------------- admin hacks -------------------------
if getattr(settings,"ENABLE_CONTACTS_AND_PEOPLE_AUTH_ADMIN_INTEGRATION", False):
    admin.site.unregister(User)
    from django import template
    from django.conf import settings
    from django.contrib import admin
    from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
    from django.contrib.auth.models import User, Group
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponseRedirect, Http404
    from django.shortcuts import render_to_response, get_object_or_404
    from django.template import RequestContext
    from django.utils.html import escape
    from django.utils.translation import ugettext, ugettext_lazy as _
    
    from django.contrib.auth.admin import UserAdmin
    from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
    from django import forms
        
    class MyNoPasswordCapableUserCreationForm(UserCreationForm):
        has_password = forms.BooleanField(required=False, initial=True)
        def clean(self):
            data = self.cleaned_data
            if self.cleaned_data['has_password'] in (False, None,):
                if 'password1' in self.errors.keys():
                    del self.errors['password1']
                if 'password2' in self.errors.keys():
                    del self.errors['password2']
                # save() will remove this temp password again.
                self.cleaned_data['password1'] = self.cleaned_data['password2'] = 'xxxxxxxxxxxxxxx'
            return data
        def save(self, commit=True):
            instance = super(MyNoPasswordCapableUserCreationForm, self).save(commit=False)
            if self.cleaned_data['has_password'] in (False, None,):
                instance.set_unusable_password()
            if commit:
                instance.save()
                if hasattr(instance, 'save_m2m'):
                    instance.save_m2m()
                return instance
            else:
                return instance
        
    class MyNoPasswordCapableUserChangeForm(UserChangeForm):
        has_password = forms.BooleanField(label="has password", help_text="LDAP users don't need a password", required=False, initial=True)
        def __init__(self, *args, **kwargs):
            r = super(MyNoPasswordCapableUserChangeForm,self).__init__(*args, **kwargs)
            instance = kwargs.get('instance',None)
            if instance and instance.id:
                if instance.has_usable_password():
                    self.initial['has_password'] = True
                else:
                    self.initial['has_password'] = False     
            return r
        def save(self, commit=True):
            instance = super(MyNoPasswordCapableUserChangeForm, self).save(commit=False)
            if self.cleaned_data['has_password'] in (False, None,):
                instance.set_unusable_password()
            if commit:
                instance.save()
                if hasattr(instance, 'save_m2m'):
                    instance.save_m2m()
                return instance
            else:
                return instance
    
    user_admin_fieldsets = list(UserAdmin.fieldsets)
    user_admin_fieldsets[0] = (None, {'fields': ('username', ('password', 'has_password',),)})
    class MyUserAdmin(UserAdmin):
        fieldsets = user_admin_fieldsets
        form = MyNoPasswordCapableUserChangeForm
        add_form = MyNoPasswordCapableUserCreationForm
        list_display = ('username', 'email', 'is_staff')
        
        def add_view(self, request):
            # IT REALLY SUCKS THAT I NEED TO COPY THIS ENTIRE METHOD... it's the same as 
            # django.contrib.auth.admin.UserAdmin.add_view, just with a other template
            
            # It's an error for a user to have add permission but NOT change
            # permission for users. If we allowed such users to add users, they
            # could create superusers, which would mean they would essentially have
            # the permission to change users. To avoid the problem entirely, we
            # disallow users from adding users if they don't have change
            # permission.
            if not self.has_change_permission(request):
                if self.has_add_permission(request) and settings.DEBUG:
                    # Raise Http404 in debug mode so that the user gets a helpful
                    # error message.
                    raise Http404('Your user does not have the "Change user" permission. In order to add users, Django requires that your user account have both the "Add user" and "Change user" permissions set.')
                raise PermissionDenied
            if request.method == 'POST':
                form = self.add_form(request.POST)
                if form.is_valid():
                    new_user = form.save()
                    msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': 'user', 'obj': new_user}
                    self.log_addition(request, new_user)
                    if "_addanother" in request.POST:
                        request.user.message_set.create(message=msg)
                        return HttpResponseRedirect(request.path)
                    elif '_popup' in request.REQUEST:
                        return self.response_add(request, new_user)
                    else:
                        request.user.message_set.create(message=msg + ' ' + ugettext("You may edit it again below."))
                        return HttpResponseRedirect('../%s/' % new_user.id)
            else:
                form = self.add_form()
            return render_to_response('contacts_and_people/admin/auth/user/add_form.html', {
                'title': _('Add user'),
                'form': form,
                'is_popup': '_popup' in request.REQUEST,
                'add': True,
                'change': False,
                'has_add_permission': True,
                'has_delete_permission': False,
                'has_change_permission': True,
                'has_file_field': False,
                'has_absolute_url': False,
                'auto_populated_fields': (),
                'opts': self.model._meta,
                'save_as': False,
                'username_help_text': self.model._meta.get_field('username').help_text,
                'root_path': self.admin_site.root_path,
                'app_label': self.model._meta.app_label,            
            }, context_instance=template.RequestContext(request))
    admin.site.register(User, MyUserAdmin)
