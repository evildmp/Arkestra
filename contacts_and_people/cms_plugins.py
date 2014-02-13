from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import EntityAutoPageLinkPluginEditor, EntityDirectoryPluginEditor, EntityMembersPluginEditor

from arkestra_utilities import admin_tabs_extension
from arkestra_utilities.admin_mixins import AutocompleteMixin

from templatetags.entity_tags import work_out_entity
from models import Membership


class EntityAutoPageLinkPluginPublisher(AutocompleteMixin, CMSPluginBase):
    model = EntityAutoPageLinkPluginEditor
    name = _("Entity auto page link")
    render_template = "entity-auto-page-link.html"
    text_enabled = True
 
    # autocomplete fields
    related_search_fields = ['entity',]
    
    def render(self, context, instance, placeholder):

        # get a tuple containing for example:
        #    Kind                 slug       title_field                 flag for auto page
        # (u'Contacts & people', 'contact', 'contacts_page_menu_title', 'auto_contacts_page')
        LINK_TUPLE = EntityAutoPageLinkPluginEditor.AUTO_PAGES[instance.link_to]
        kind = LINK_TUPLE[1]
        field_name = LINK_TUPLE[2]
        auto_page_flag = LINK_TUPLE[3]
        
        entity = work_out_entity(context, None)
        link_entity = instance.entity or entity
        if link_entity:
            #  instance.entity not set, or instance.entity = entity
            if entity == link_entity:
                link_title = getattr(entity, field_name)
            #  instance.entity set and instance.entity != entity (so we provide its name)
            else:
                link_title = instance.entity.short_name + ': ' + getattr(instance.entity,field_name)
                entity = instance.entity

            if getattr(entity, auto_page_flag):
                link = entity.get_auto_page_url(kind)               
                link_title = instance.text_override or link_title
            
                context.update({ 
                    'link': link,
                    'link_title': link_title,
                })
            return context
    
    def icon_src(self, instance):
        return "/static/plugin_icons/entity_auto_page_link.png"

class EntityDirectoryPluginPublisher(AutocompleteMixin, CMSPluginBase):
    model = EntityDirectoryPluginEditor
    name = _("Directory")
    render_template = "directory.html"
    text_enabled = True
 
    # autocomplete fields
    related_search_fields = ['entity',]

    def icon_src(self, instance):
        return "/static/plugin_icons/entity_directory.png"
        
    def render(self, context, instance, placeholder):
        if instance.entity:
            entity = instance.entity
        else:
            entity = work_out_entity(context, None)
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


class EntityMembersPluginPublisher(AutocompleteMixin, CMSPluginBase):
    """
    Returns all the memberships in the entity and its descendants; the template groups them by entity"""
    model = EntityMembersPluginEditor
    name = _("Member list")
    render_template = "entity_members_plugin.html"
    text_enabled = True
 
    # autocomplete fields
    related_search_fields = ['entity',]

    def icon_src(self, instance):
        return "/static/plugin_icons/entity_members.png"
           
    def render(self, context, instance, placeholder):
        if instance.entity:
            entity = instance.entity
        else:
            entity = work_out_entity(context, None)

        entities = entity.get_descendants(include_self = True)
        
        memberships = Membership.objects.filter(entity__in = entities).order_by('entity', '-importance_to_entity')

        nest = memberships.values('entity',).distinct().count() > 1 or False

        context.update({
            'entity': entity,
            'memberships': memberships,
            'nest': nest,
            })
        return context

plugin_pool.register_plugin(EntityDirectoryPluginPublisher)
plugin_pool.register_plugin(EntityMembersPluginPublisher)
plugin_pool.register_plugin(EntityAutoPageLinkPluginPublisher)
