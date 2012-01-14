from django.utils.safestring import mark_safe 
from django.template import RequestContext
from django.conf import settings
from django.core.cache import cache

from cms.models import Page

from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from menus.base import Modifier, Menu

from datetime import datetime

main_news_events_page_list_length = settings.MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
arkestra_menus = settings.ARKESTRA_MENUS

    
for menu in arkestra_menus:
    if menu["cms_plugin_model_name"]:
        plugin = __import__(menu["plugins_module"], globals(), locals(), [menu["cms_plugin_model_name"],], -1)
        menu["cms_plugin_model"] = getattr(plugin, menu["cms_plugin_model_name"])

# ArkestraPages(Modifier) checks whether there are Entities that have automatic pages 
# (contacts & people, news & events, etc) that should be featured in the menu.
#
# These menu might have this structure:
#
#   Department of Witchcraft    [the home page of the Entity]
#       About witchcraft        [an ordinary CMS Page]
#       Cats & hats             [an ordinary CMS Page]
#       News & Events           [an Arkestra automatic page]
#           Previous Events     [an Arkestra automatic page - won't appear in menu unless News & Events is selected]
#           News Archive        [an Arkestra automatic page - won't appear in menu unless News & Events is selected] 
#       Contacts & People       [an Arkestra automatic page]   

# class ArkestraPages(Modifier):
#     def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
#         # this currently relies on the pre-cut nodes. It *will* hammer the database
#         if arkestra_menus and not post_cut:              
#             
#             self.auto_page_url = getattr(request, "auto_page_url", None)
#             self.request = request
#             self.nodes = nodes
# 
#             # loop over all the nodes returned by the nodes in the Menu classes
#             for node in self.nodes: 
#                 # for each node, try to find a matching Page that is an Entity's home page
#                 try:
#                     page = Page.objects.get(id=node.id, entity__isnull=False)
#                 except Page.DoesNotExist:
#                     pass
#                 else:            
#                     entity = page.entity.all()[0]  
#                     # we have found a node for a Page with an Entity, so check it against arkestra_menus
#                     for menu in arkestra_menus:
#                         self.do_menu(node, menu, entity)
#                                                                                
#             return self.nodes
#         else:
#             return nodes

class ArkestraPages(Modifier):
    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        start_time = datetime.now()
        # this currently relies on the pre-cut nodes. It *will* hammer the database
        self.nodes = nodes                                                            
        self.auto_page_url = getattr(request, "auto_page_url", None)
        self.request = request
        

        if arkestra_menus and not post_cut:
            key = "ArkestraPages.modify()" + request.path + "pre_cut"
            cached_pre_cut_nodes = cache.get(key, None)
            if cached_pre_cut_nodes: 
                print "    ++ got cache", key, settings.CMS_CACHE_DURATIONS['menus']
                return cached_pre_cut_nodes

            # loop over all the nodes returned by the nodes in the Menu classes
            for node in self.nodes: 
                # for each node, try to find a matching Page that is an Entity's home page
                try:
                    page = Page.objects.get(id=node.id, entity__isnull=False)
                except Page.DoesNotExist:
                    node.entity = False
                else:            
                    node.entity = page.entity.all()[0]  
                    for menu in arkestra_menus:
                        self.do_menu(node, menu, node.entity)

                    # self.create_new_node(
                    #     title = "Publications",
                    #     url = node.entity.get_related_info_page_url("publications"), 
                    #     parent = node, 
                    #     )                 
                                                                               
            print "    ++ saving cache", key
            cache.set(key, self.nodes, settings.CMS_CACHE_DURATIONS['menus'])
            print "    **", len(self.nodes), "nodes in", datetime.now() - start_time, "for ArkestraPages.modify()"
            return self.nodes
        else:
            print "** post_cut"
            # for node in self.nodes:
            #     # we have found a node for a Page with an Entity, so check it against arkestra_menus
            #     for menu in arkestra_menus:
            #         # self.do_menu(node, menu, node.entity) 
            #         pass
            return self.nodes      

    def do_menu(self, node, menu, entity):
        # does this entity have this kind of auto-page in the menu?
        if getattr(entity, menu["auto_page_attribute"]):
            cms_plugin_model = menu.get("cms_plugin_model")
            new_nodes = []
            
            if cms_plugin_model:
                # create an instance of the plugin class editor with appropriate attributes
                instance = cms_plugin_model.model(
                    entity = entity, 
                    limit_to = main_news_events_page_list_length
                    )
                instance.type = "menu"
                instance.view = "current"
                
                # use the instance to create an instance of the plugin publisher
                plugin = cms_plugin_model()   
                # use its get_items method to place publishable items in plugin.lists
                plugin.get_items(instance)
                if plugin.lists:
                    new_node = self.create_new_node(
                        title = getattr(entity, menu["title_attribute"]),
                        url = entity.get_related_info_page_url(menu["url_attribute"]), 
                        parent = node
                        )
                    # does this menu call for sub-menu items?
                    if menu.get("sub_menus", None):
                        plugin.add_links_to_other_items(instance)
                        for item in plugin.lists:
                            # and go through the other_items lists for each, creating a node for each
                            for other_item in item["other_items"]:

                                self.create_new_node(
                                    title = other_item["title"], 
                                    url = other_item["link"], 
                                    parent = new_node, 
                                )

            else:
                new_node = self.create_new_node(
                    title = getattr(entity, menu["title_attribute"]),
                    url = entity.get_related_info_page_url(menu["url_attribute"]), 
                    parent = node, 
                    )
            # if new_node:
            #     for sub_menu in menu["sub_menus"]:
            #         self.do_menu(node, sub_menu, entity)

        # return new_nodes

    def create_new_node(self, title, url, parent):
        # create a new node for the menu
        new_node = NavigationNode(
            title=mark_safe(title), 
            url= url, 
            id=None,                           
            )

        new_node.parent = parent
        parent.children.append(new_node)
        self.nodes.append(new_node) 
    
        # is this node selected?
        if new_node.get_absolute_url() == self.auto_page_url:
    
            new_node.selected = True
            node_to_mark = new_node
            while node_to_mark.parent:
                node_to_mark.parent.selected = False
                node_to_mark.parent.ancestor = True
                node_to_mark = node_to_mark.parent
        else:
            new_node.selected = False
        return new_node                        

menu_pool.register_modifier(ArkestraPages)