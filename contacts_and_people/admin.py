from django.conf.urls.defaults import patterns, url

from django.db.models import Q

from django.conf import settings

from django.contrib import admin, messages
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from django import forms

from django.utils.safestring import mark_safe 

from django.http import HttpResponseRedirect, HttpResponse

# from arkestra_utilities import admin_tabs_extension
from arkestra_utilities.widgets.combobox import ComboboxField
# from widgetry.tabs.admin import ModelAdminWithTabs

from contacts_and_people import models

from links.admin import get_or_create_external_link
from links.admin import ObjectLinkInline

from cms.admin.placeholderadmin import PlaceholderAdmin

from arkestra_utilities.mixins import AutocompleteMixin, SupplyRequestMixin

HAS_PUBLICATIONS = 'publications' in settings.INSTALLED_APPS

if HAS_PUBLICATIONS:
    from publications.admin import ResearcherInline


# ------------------------- Membership admin -------------------------
class MembershipForm(forms.ModelForm):
    # cleans up membership & role information
    class Meta:
        model = models.Membership

class MembershipInline(AutocompleteMixin, admin.TabularInline):
    # for all membership inline admin
    form = MembershipForm    
    model = models.Membership
    extra = 1
    related_search_fields = {
        'person': ('surname',),
        'entity': ('name',),
    }
    editable_search_fields = ('person', 'entity',)


class MembershipForEntityInline(MembershipInline): # for Entity admin
    exclude = ('display_role',)
    extra = 3


class MembershipForPersonInline(MembershipInline): # for Person admin
    exclude = ('display_role',)


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('person', 'entity', 'importance_to_person', 'importance_to_entity',)
    ordering = ['person',]
    form = MembershipForm
    related_search_fields = [
        'person',
        'entity',
    ]

# ------------------------- Phone contact admin -------------------------

class PhoneContactInlineForm(forms.ModelForm):
    label = ComboboxField(label = "label", choices=models.PhoneContact.LABEL_CHOICES, required=False)
    country_code = forms.CharField(label="Country code", initial = "44", widget=forms.TextInput(attrs={'size':'4'}))
    area_code = forms.CharField(label="Area code", initial = "29", widget=forms.TextInput(attrs={'size':'5'}))
    number = forms.CharField(label="Number", widget=forms.TextInput(attrs={'size':'10'}))
    internal_extension = forms.CharField(label="Internal extension", widget=forms.TextInput(attrs={'size':'6'}), required=False)

    class Meta:
        model = models.PhoneContact


class PhoneContactInline(generic.GenericTabularInline):
    extra = 3
    model = models.PhoneContact
    form = PhoneContactInlineForm


class PhoneContactAdmin(admin.ModelAdmin):
    pass

# ------------------------- PersonLite admin -------------------------

class PersonLiteForm(forms.ModelForm):
    class Meta:
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
          
# admin.site.register(models.PersonLite, PersonLiteAdmin)     

# ------------------------- Person admin -------------------------

"""
Not for v1.0
class TeacherInline(admin.StackedInline):
    model = models.Teacher
"""

class PersonForm(forms.ModelForm):
    class Meta:
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

    def clean(self):

        # set the title
        print self.cleaned_data
        title = self.cleaned_data["title"] or ""
        link_title = " ".join(name_part for name_part in [str(title), self.cleaned_data["given_name"], self.cleaned_data["surname"]] if name_part)

        # check ExternalLink-related issues
        self.cleaned_data["external_url"] = get_or_create_external_link(self.request,
            self.cleaned_data.get("input_url", None), # a manually entered url
            self.cleaned_data.get("external_url", None), # a url chosen with autocomplete
            self.cleaned_data.get("link_title"), # link title
            "", # link description
            )          

        return self.cleaned_data


class PersonAdmin(SupplyRequestMixin, AutocompleteMixin, PlaceholderAdmin):
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
            'fields': ('active', 'user', 'institutional_username', 'slug',),
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
    related_search_fields = ('external_url', 'please_contact', 'override_entity', 'user', 'building')


class TitleAdmin(admin.ModelAdmin):
    pass


class DisplayUsernameWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        user = User.objects.get(pk=value)
        default = super(DisplayUsernameWidget,self).render(name, value, attrs)
        return mark_safe(u'<span>Assigned user: <strong>%s</strong></span><div style="display: none;">%s</div>' % (user,default))

# ------------------------- EntityLite admin -------------------------

class EntityLiteForm(forms.ModelForm):
    class Meta:
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


# admin.site.register(models.EntityLite, EntityLiteAdmin)          
        
# ------------------------- Entity admin -------------------------

class EntityForm(forms.ModelForm):
    class Meta:
        model = models.Entity
    
    input_url = forms.CharField(max_length=255, required = False)
            
    def clean(self):
        try:
            # does an instance exist in the database with the same website?
            entity = models.Entity.objects.get(website=self.cleaned_data["website"]) 
        except:
            # nothing matched, so we can safely go ahead with this one
            pass
        else:
            # one existed already - if it's this one that's OK
            if not self.instance.pk == entity.pk:
                raise forms.ValidationError('Another entity (%s) already has the same home page (%s).' % (entity, self.cleaned_data["website"]))    
        
        
        # check ExternalLink-related issues
        self.cleaned_data["external_url"] = get_or_create_external_link(self.request,
            self.cleaned_data.get("input_url", None), # a manually entered url
            self.cleaned_data.get("external_url", None), # a url chosen with autocomplete
            self.cleaned_data.get("name"), # link title
            "", # link description
        )

        if not self.cleaned_data["website"] and not self.cleaned_data["external_url"]:
            message = "This entity has neither a home page nor an External URL. Are you sure you want to do that?"
            messages.add_message(self.request, messages.WARNING, message)
        if not self.cleaned_data["short_name"]:
            self.cleaned_data["short_name"] = self.cleaned_data["name"]
        return self.cleaned_data 


class EntityAdmin(PlaceholderAdmin, SupplyRequestMixin, AutocompleteMixin, admin.ModelAdmin): 
    search_fields = ['name']
    inlines = (MembershipForEntityInline,PhoneContactInline)
    form = EntityForm
    list_display = ('name', 'parent', 'building', 'abstract_entity','website', )
    list_editable = ('website', )
    change_list_template = "admin/contacts_and_people/entity/change_list.html"
    related_search_fields = ['parent', 'building', 'website', 'external_url',]    
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
                'fields': ('slug',)
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
            }),
        )
    if "vacancies_and_studentships" in settings.INSTALLED_APPS:
        tab_automatic_pages.append(  
            ('Vacancies', {
                'fields': (('auto_vacancies_page', 'vacancies_page_menu_title',),)
            }),
        )
    if 'publications' in settings.INSTALLED_APPS:
        tab_automatic_pages.append(  
            ('Publications', {
                    'fields': (('auto_publications_page', 'publications_page_menu_title',),)
                }
            ),
        )
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

# ------------------------- Building and site admin -------------------------

class BuildingAdminForm(forms.ModelForm):
    # getting_here = forms.CharField(widget=WYMEditor, required = False)
    # access_and_parking = forms.CharField(widget=WYMEditor, required = False)
    
    class Meta:
        model = models.Building

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


class SiteAdmin(AutocompleteMixin, admin.ModelAdmin):
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


class BuildingAdmin(PlaceholderAdmin):
    search_fields = ['name','number','street','postcode','site__site_name']
    form = BuildingAdminForm

admin.site.register(models.Person,PersonAdmin)
admin.site.register(models.Building,BuildingAdmin)
admin.site.register(models.Entity,EntityAdmin)
admin.site.register(models.Site,SiteAdmin)
admin.site.register(models.Title,TitleAdmin)
# admin.site.register(models.Membership,MembershipAdmin)
# admin.site.register(models.PhoneContact,PhoneContactAdmin)

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
