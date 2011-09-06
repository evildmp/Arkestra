from django.utils.safestring import mark_safe 
from django.template import RequestContext
from django.conf import settings

from cms.models import Page

from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from menus.base import Modifier

from news_and_events.models import NewsAndEventsPlugin        
from news_and_events.cms_plugins import CMSNewsAndEventsPlugin

from vacancies_and_studentships.models import VacanciesPlugin        
from vacancies_and_studentships.cms_plugins import CMSVacanciesPlugin

MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH = settings.MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
EXPAND_ALL_MENU_BRANCHES = getattr(settings, "EXPAND_ALL_MENU_BRANCHES", False)



# we're expecting modifiers: contacts, news, news_archive, forthcoming_events, previous_events, vacancies, publications
menu_modifiers = getattr(settings, 'MENU_MODIFIERS', None)
if menu_modifiers:
    menu_tests = menu_modifiers.get("ArkestraPages")
else:
    menu_tests = []
    
class ArkestraPages(Modifier):
    post_cut = True

    def modify(self, request, navigation_tree, namespace, root_id, post_cut, breadcrumb):
        # only bother doing this once the tree has been cut
        if not (post_cut and menu_tests):
            return navigation_tree

        else:
            # we need to know the current page
            page = getattr(request, "current_page", None)
            # cms Pages won't have request.page_path, so set that using request.path
            request.page_path = getattr(request, "page_path", request.path)  
            self.recursive(request, navigation_tree)  
            return navigation_tree

    def recursive(self, request, nodes):
        for child in nodes:
            
            try:
                ancestor = child.ancestor
            except AttributeError:
                ancestor = False
            try:
                selected = child.selected
            except AttributeError:
                selected = False
            
            # expand branches selectvely, or expand all    
            if selected or ancestor or EXPAND_ALL_MENU_BRANCHES:
                # does the entity have an entity?
                try:
                    page = Page.objects.get(id=child.id, entity__isnull=False)
                    entity = page.entity.all()[0]
                    
                    # does this entity have a news page?
                    if entity.auto_news_page and "news" in menu_tests:
                        # invoke the plugin to find out more
                        instance = NewsAndEventsPlugin()
                        instance.entity = entity
                        instance.type = "menu"
                        instance.limit_to = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
                        instance.view = "current"
                        context = RequestContext(request)
                        
                        # create an instance of the plugin to see if the menu should have items
                        plugin = CMSNewsAndEventsPlugin()   
                        plugin.get_items(instance)
                        plugin.add_links_to_other_items(instance)    
                        
                        # assume there's no menu item required
                        show_menu_item = False
                                               
                        menutitle = entity.news_page_menu_title

                        # create a new node
                        new_node = NavigationNode(
                            mark_safe(menutitle), 
                            entity.get_related_info_page_url('news-and-events'), 
                            None
                            )
                            
                        # go through the lists of items
                        for item in plugin.lists:
                            if item["items"]:
                                show_menu_item = True

                            # and go through the other_items lists for each
                            for other_item in item["other_items"]:
                                new_sub_node = NavigationNode(
                                    mark_safe(other_item["title"]), 
                                    other_item["link"], 
                                    None )
                                if request.page_path == new_sub_node.get_absolute_url():
                                    new_sub_node.selected = True
                                    new_node.selected = False

                                show_menu_item = True
                                new_node.children.append(new_sub_node)

                        if show_menu_item:
                            # is this node the one we are currently looking at?
                            if new_node.get_absolute_url() == request.page_path:
                                new_node.selected = True
                                child.selected = False
                            child.children.append(new_node)

                    if entity.auto_contacts_page and "contacts" in menu_tests:
                        menutitle = entity.contacts_page_menu_title
                        new_node = NavigationNode(mark_safe(menutitle), entity.get_related_info_page_url('contact'), None)
                        if new_node.get_absolute_url() in request.page_path:
                            new_node.selected = True
                            child.selected=False
                            
                        child.children.append(new_node)

                    if getattr(entity, "auto_vacancies_page", None)  and "vacancies" in menu_tests:

                        instance = VacanciesPlugin()
                        instance.entity = entity
                        instance.type = "menu"
                        instance.limit_to = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
                        instance.view = "current"
                        context = RequestContext(request)
                                             
                        # create an instance of the plugin to see if the menu should have items
                        plugin = CMSVacanciesPlugin()   
                        plugin.get_items(instance)
                        plugin.add_links_to_other_items(instance)    

                        # assume there's no menu item required
                        show_menu_item = False

                        # are there actually any vacancies/studentships items to show? if not, no menu
                        for item in plugin.lists:
                            if item["items"]:
                                show_menu_item = True
                                
                        if show_menu_item:
                            print "menu"
                            print plugin.lists
                            menutitle = entity.vacancies_page_menu_title
                            new_node = NavigationNode(mark_safe(menutitle), entity.get_related_info_page_url('vacancies-and-studentships'), None)
                            if request.page_path == new_node.get_absolute_url():
                                new_node.selected = True
                                child.selected=False
                            child.children.append(new_node)
            
                    if getattr(entity, "auto_publications_page", None) and entity.auto_publications_page and "publications" in menu_tests:
                        menutitle = entity.publications_page_menu_title
                        new_node = NavigationNode(mark_safe(menutitle), entity.get_related_info_page_url('publications'), None)
                        if request.page_path == new_node.get_absolute_url():
                            new_node.selected = True
                            child.selected=False
                        child.children.append(new_node)
                except Page.DoesNotExist:
                    pass
            self.recursive(request, child.children)
            
menu_pool.register_modifier(ArkestraPages)