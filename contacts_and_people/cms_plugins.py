from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import EntityAutoPageLinkPluginEditor, EntityDirectoryPluginEditor, EntityMembersPluginEditor
from django.utils.translation import ugettext as _

from contacts_and_people.templatetags.entity_tags import work_out_entity
from contacts_and_people.models import Membership

# for autocomplete search
from widgetry import fk_lookup
from django.db.models import ForeignKey
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse

class EntityAutoPageLinkPluginPublisher(CMSPluginBase):
    model = EntityAutoPageLinkPluginEditor
    name = _("Entity auto page link")
    render_template = "entity-auto-page-link.html"
    text_enabled = True
 
     # autocomplete fields
    related_search_fields = ['entity',]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(EntityAutoPageLinkPluginPublisher, self).formfield_for_dbfield(db_field, **kwargs)
    class Media:
        js = (
            '/media/cms/js/lib/jquery.js', # we already load jquery for the tabs
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra//static/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra//static/jquery/themes/base/ui.all.css',)
        }
   
    
    def render(self, context, instance, placeholder):
        LINK_ATTRIBUTES = {
            "news-and-events": "news_page_menu_title",
            "contacts-and-people": "contacts_page_menu_title",
            "publications": "publications_page_menu_title",
            "vacancies-and-studentships": "vacancies_page_menu_title",
            }
        EntityAutoPageLinkPluginEditor.AUTO_PAGES
        print "-- in render of CMSContactsAndPeoplePlugin --"
        # find out what kind of information we're linking to
        LINK_TUPLE = EntityAutoPageLinkPluginEditor.AUTO_PAGES[instance.link_to]
        print "LINK_TUPLE", LINK_TUPLE
        entity = work_out_entity(context, None)
        if instance.entity and instance.entity != entity:
            link = instance.entity.get_absolute_url() + LINK_TUPLE[1]
            link_title = instance.entity.short_name + ': ' + getattr(entity,LINK_TUPLE[2])
        else:
            link_title = getattr(entity,LINK_TUPLE[2])
            link = entity.get_absolute_url() + LINK_TUPLE[1]
        if instance.text_override:
            link_title = instance.text_override
        print EntityAutoPageLinkPluginEditor.AUTO_PAGES[instance.link_to][2]
        context.update({ 
            'link': link,
            'link_title': link_title,
            })
        return context
    def icon_src(self, instance):
        return "/media/arkestra/entity_auto_page_link.png"

class EntityDirectoryPluginPublisher(CMSPluginBase):
    model = EntityDirectoryPluginEditor
    name = _("Directory")
    render_template = "directory.html"
    text_enabled = True
 
     # autocomplete fields
    related_search_fields = ['entity',]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(EntityDirectoryPluginPublisher, self).formfield_for_dbfield(db_field, **kwargs)
    class Media:
        js = (
            '/media/cms/js/lib/jquery.js', # we already load jquery for the tabs
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra//static/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra//static/jquery/themes/base/ui.all.css',)
        }
   
    def render(self, context, instance, placeholder):
        print "in EntityDirectoryPluginPublisher"
        if instance.entity:
            entity = instance.entity
        else:
            entity = work_out_entity(context, None)
        root_entity = entity
        descendants = entity.get_descendants()
        if descendants:
            # find our base level
            first_level = descendants[0].level
            # filter to maximum sub-level depth    
            if instance.levels:
                maximum_level = first_level + instance.levels
                descendants = descendants.filter(level__lt = maximum_level)
            # apply all the attributes we need to our descendant entities
            for descendant in descendants:
                # reset the level, so that first_level is 0
                descendant.level = descendant.level - first_level
                if descendant.website and (descendant.level < instance.display_descriptions_to_level or instance.display_descriptions_to_level == None):                    
                    descendant.description = descendant.website.get_meta_description()

        context.update({
            'entities': descendants,
            'directory': instance,
            })
        return context

class EntityMembersPluginPublisher(CMSPluginBase):
    """
    Returns all the memberships in the entity and its descendants; the template groups them by entity"""
    model = EntityMembersPluginEditor
    name = _("Member list")
    render_template = "entity_members_plugin.html"
    text_enabled = True
 
     # autocomplete fields
    related_search_fields = ['entity',]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = fk_lookup.FkLookup(db_field.rel.to)
        return super(EntityMembersPluginPublisher, self).formfield_for_dbfield(db_field, **kwargs)
    class Media:
        js = (
            '/media/cms/js/lib/jquery.js', # we already load jquery for the tabs
            '/media/cms/js/lib/ui.core.js',
            '/media/arkestra//static/jquery/ui/ui.tabs.js',
        )
        css = {
            'all': ('/media/arkestra//static/jquery/themes/base/ui.all.css',)
        }
   
    def render(self, context, instance, placeholder):
        if instance.entity:
            entity = instance.entity
        else:
            entity = work_out_entity(context, None)
        print "ok so far"

        entities = entity.get_descendants(include_self = True)
        
        memberships = Membership.objects.filter(entity__in = entities).order_by('entity', '-importance_to_entity')

        nest = memberships.values('entity',).distinct().count() > 1 or False
        print nest

        print "returning context"
        context.update({
            'entity': entity,
            'memberships': memberships,
            'nest': nest,
            })
        return context

plugin_pool.register_plugin(EntityDirectoryPluginPublisher)
plugin_pool.register_plugin(EntityMembersPluginPublisher)
plugin_pool.register_plugin(EntityAutoPageLinkPluginPublisher)
