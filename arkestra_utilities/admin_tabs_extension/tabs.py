from django import forms, template
from django.contrib.admin import helpers
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.forms.formsets import all_valid
from django.http import Http404
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

try:
    set11
except NameError:
    from sets import Set as set     # Python 2.3 fallback

"""

tabs = (
    ('Tab name', {'classes': ('specialCssClass',),
                  'fieldsets': (
                      ('Fieldset Name', {
                                      'fields': ('user', 'name', 'title',),
                                      'classes': ('collapse',)
                                  }),
                      ('Fieldset Name 2', {
                                      'fields': ('user', 'name', 'title',),
                                      'classes': ('collapse',)
                                  }),
                        ),
                 'inlines': (InlineThingy, OtherInlineThingy,)
                 }),
                    
    ('Other Tab Name', {'classes'
)

"""



class Tabset(object):
    '''
    Like AdminForm in a normal setup, but provides Tab instances instead of formsets.
   
    '''
    has_tabs = True
    def __init__(self, form, tabs, prepopulated_fields):
        self.form = form
        self.tabs = []
        for name, options in tabs:
            self.tabs.append(Tab(self.form, name, **options))
        
        self.prepopulated_fields = [{
            'field': form[field_name],
            'dependencies': [form[f] for f in dependencies]
        } for field_name, dependencies in prepopulated_fields.items()]

    def __iter__(self):
        for tab in self.tabs:
            yield tab
    
    def first_field(self):
        return None
    
    def _media(self):
        media = self.form.media
        for tab in self:
            media = media + tab.media
        return media
    media = property(_media)
    
    def get_tab_that_has_inline(self, inline_class_name):
        for tab in self:
            if inline_class_name in tab.inline_names:
                return tab
        return None
        
class Tab(helpers.AdminForm):
    '''
    A subclass of AdminForm. It adds a name and a description and additionally
    also contains the InlineFormsets
    '''
    def __init__(self, form, name=None, fieldsets=(), inlines=(), classes=(), description=None):
        self.form = form
        self.name = name
        # TODO: fieldsets should also be able to contain InlineFormsets
        self.fieldsets = helpers.normalize_fieldsets(fieldsets)
        self.inline_names = inlines
        self.inlines = []
        
        self.classes = u' '.join(classes)
        self.description = description
    
    def has_errors(self):
        if not hasattr(self,'_has_errors'):
            self._has_errors = False
            for inline in self.inlines:
                if inline.formset.is_bound and not inline.formset.is_valid():
                    self._has_errors = True
                    break
            for fieldset in self:
                for fieldline in fieldset:
                    for field in fieldline.fields:
                        if self.form[field].errors:
                            self._has_errors = True
                            break
        return self._has_errors
            
    def _media(self):
        # formset media is already handled in the view
        return super(Tab, self)._media()
    media = property(_media)
            
                      
        

class ModelAdminWithTabs(ModelAdmin):
    tabs = []
    def add_view(self, request, form_url='', extra_context=None):
        """
        Like the original add_view from ModelAdmin. Alterations are marked
        with 
        # ----start
        # ----end
        """
        
        "The 'add' admin view for this model."
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=False)
            else:
                form_validated = False
                new_object = self.model()
            prefixes = {}
            for FormSet in self.get_formsets(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new=request.POST.has_key("_saveasnew"),
                                  prefix=prefix)
                formsets.append(formset)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=False)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=False)

                self.log_addition(request, new_object)
                return self.response_add(request, new_object)
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")
            form = ModelForm(initial=initial)
            prefixes = {}
            for FormSet in self.get_formsets(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=self.model(), prefix=prefix)
                formsets.append(formset)
        
        # --start--
        adminForm = Tabset(form, self.tabs, self.prepopulated_fields)
        # --original--
        # adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)), self.prepopulated_fields)
        # --end--
        media = self.media + adminForm.media
        
        # --start-- (identical to the one in change_view, except for not passing obj in get_fieldsets)
        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            
            tab = adminForm.get_tab_that_has_inline(inline.__class__.__name__)
            if not tab==None:
                tab.inlines.append(inline_admin_formset)
            else:
                inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media
        # --original--
        '''
        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media
        '''
        # --end--
        
        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)
    add_view = transaction.commit_on_success(add_view)
    
    def change_view(self, request, object_id, extra_context=None):
        """
        Like the original change_view from ModelAdmin. Alterations are marked
        with 
        # ----start
        # ----end
        """
        
        "The 'change' admin view for this model."
        model = self.model
        opts = model._meta

        try:
            obj = self.queryset(request).get(pk=unquote(object_id))
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and request.POST.has_key("_saveasnew"):
            return self.add_view(request, form_url='../add/')

        ModelForm = self.get_form(request, obj)
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet in self.get_formsets(request, new_object):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix)
                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=obj)
            prefixes = {}
            for FormSet in self.get_formsets(request, obj):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix)
                formsets.append(formset)
        # --start--
        adminForm = Tabset(form, self.tabs, self.prepopulated_fields)
        # --original--
        # adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj), self.prepopulated_fields)
        # --end--
        media = self.media + adminForm.media
        
        # --start--
        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            
            tab = adminForm.get_tab_that_has_inline(inline.__class__.__name__)
            if not tab==None:
                tab.inlines.append(inline_admin_formset)
            else:
                inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media
        # --original--
        '''
        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            
            media = media + inline_admin_formset.media
        '''
        # --end--   
        
        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj)
    change_view = transaction.commit_on_success(change_view)
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'ordered_objects': ordered_objects,
            'form_url': mark_safe(form_url),
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'root_path': self.admin_site.root_path,
        })
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.change_form_template or [
            "admin/%s/%s/tabbed_change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/tabbed_change_form.html" % app_label,
            "admin/tabbed_change_form.html"
        ], context, context_instance=context_instance)
    
    def _declared_fieldsets(self):
        if self.tabs:
            fieldsets = []
            for name, tab in self.tabs:
                fieldsets += list(tab.get('fieldsets', []))
            return fieldsets
        elif self.fieldsets:
            return self.fieldsets
        elif self.fields:
            return [(None, {'fields': self.fields})]
        return None
    declared_fieldsets = property(_declared_fieldsets)
