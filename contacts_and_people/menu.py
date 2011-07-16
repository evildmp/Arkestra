from django.utils.safestring import mark_safe 
from django.template import RequestContext
from django.conf import settings

from cms.models import Page

from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from menus.base import Modifier

from news_and_events.models import NewsAndEventsPlugin        
from news_and_events.mixins import NewsAndEventsPluginMixin
from vacancies_and_studentships.models import VacanciesPlugin        
from vacancies_and_studentships.mixins import VacancyStudentshipPluginMixin

MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH = settings.MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH

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
    
            if selected or ancestor:
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
                        NewsAndEventsPluginMixin().get_items(instance)   
                                             
                        # are there actually any new/events items to show? if not, no menu
                        if instance.news or instance.other_news or instance.events or instance.other_events:
                        
                            menutitle = entity.news_page_menu_title
                            new_node = NavigationNode(mark_safe(menutitle), entity.get_related_info_page_url('news-and-events'), None)
                            if new_node.get_absolute_url() in request.page_path:

                                new_node.selected = True
                                child.selected=False

                                if instance.other_news  and "news_archive" in menu_tests:
                                    new_sub_node = NavigationNode(mark_safe("News archive"), entity.get_related_info_page_url('news-archive'), None )
                                    if request.page_path == new_sub_node.get_absolute_url():
                                        new_sub_node.selected = True
                                        new_node.selected=False
                                    new_node.children.append(new_sub_node)

                                if any("all-forthcoming" in d.itervalues() for d in instance.other_events) and "forthcoming_events" in menu_tests:
                                    new_sub_node = NavigationNode(mark_safe("All forthcoming events"), entity.get_related_info_page_url('forthcoming-events'), None )
                                    if request.page_path == new_sub_node.get_absolute_url():
                                        new_sub_node.selected = True
                                        new_node.selected=False
                                    new_node.children.append(new_sub_node)
                
                                if any("previous-events" in d.itervalues() for d in instance.other_events) and "previous_events" in menu_tests:
                                    new_sub_node = NavigationNode(mark_safe("Previous events"), entity.get_related_info_page_url('previous-events'), None )
                                    if request.page_path == new_sub_node.get_absolute_url():
                                        new_sub_node.selected = True
                                        new_node.selected=False
                                    new_node.children.append(new_sub_node)

                            child.children.append(new_node)

                    if entity.auto_contacts_page and "contacts" in menu_tests:
                        menutitle = entity.contacts_page_menu_title
                        new_node = NavigationNode(mark_safe(menutitle), entity.get_related_info_page_url('contact'), None)
                        if new_node.get_absolute_url() in request.page_path:
                            new_node.selected = True
                            child.selected=False
                            
                        child.children.append(new_node)

                    if getattr(entity, "auto_vacancies_page", None)  and "vacancies" in menu_tests:

                        # # this requires some work on the vacancies_and_studentships manager before it can be enabled
                        # 
                        # instance = VacanciesPlugin()
                        # instance.entity = entity
                        # instance.type = "menu"
                        # instance.limit_to = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
                        # instance.view = "current"
                        # context = RequestContext(request)
                        # VacancyStudentshipPluginMixin().get_items(instance)   
                        #                      
                        # # are there actually any vacancies/studentships items to show? if not, no menu
                        # if instance.vacancies or instance.studentships:

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