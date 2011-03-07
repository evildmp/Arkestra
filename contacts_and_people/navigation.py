from cms.utils.navigation import NavigationNode
from cms.models import Page
from django.utils.safestring import mark_safe 

from django.conf import settings

def inject_contactpage_for_entities(navigation_tree, request):
    
    pages = list(Page.objects.filter(entity__isnull=False))
    def recursive(nodes):
        for child in nodes: 
            try:
                ancestor = child.ancestor
            except:
                ancestor = False
            try:
                selected = child.selected
            except:
                selected = False
            
            if selected or ancestor:
            
                if 'news_and_events' in settings.INSTALLED_APPS and child in pages and child.entity.all()[0].auto_news_page:
                    menutitle = child.entity.all()[0].news_page_menu_title
                    new_node = NavigationNode(mark_safe(menutitle), child.entity.all()[0].get_absolute_url()  + "news-and-events/")
                    if request.path == new_node.get_absolute_url():
                        new_node.selected = True
                        child.selected=False
                    child.childrens.append(new_node)
                    
                if child in pages and child.entity.all()[0].auto_contacts_page:
                    menutitle = child.entity.all()[0].contacts_page_menu_title
                    new_node = NavigationNode(mark_safe(menutitle), child.entity.all()[0].get_absolute_url() + "contact/")
                    if request.path == new_node.get_absolute_url():
                        new_node.selected = True
                        child.selected=False
                    child.childrens.append(new_node)

                if 'vacancies_and_studentships' in settings.INSTALLED_APPS and child in pages and child.entity.all()[0].auto_vacancies_page:
                    menutitle = child.entity.all()[0].vacancies_page_menu_title
                    new_node = NavigationNode(mark_safe(menutitle), child.entity.all()[0].get_absolute_url()  + "vacancies-and-studentships/")
                    if request.path == new_node.get_absolute_url():
                        new_node.selected = True
                        child.selected=False
                    child.childrens.append(new_node)
                    
                if 'publications' in settings.INSTALLED_APPS and child in pages and child.entity.all()[0].auto_publications_page:
                    menutitle = child.entity.all()[0].publications_page_menu_title
                    new_node = NavigationNode(mark_safe(menutitle), child.entity.all()[0].get_absolute_url()  + "publications/")
                    if request.path == new_node.get_absolute_url():
                        new_node.selected = True
                        child.selected=False
                    child.childrens.append(new_node)
                    
            recursive(child.childrens)
    recursive(navigation_tree)    

""""    
def inject_news_events_page_for_entities(navigation_tree, request):
    pages = list(Page.objects.filter(entity__isnull=False))
    def recursive(nodes):
        for child in nodes:

            if child in pages and child.entity.all()[0].auto_news_page:
                newspage_menutitle = "injected: " + child.entity.all()[0].news_page_menu_title
                new_node = NavigationNode(mark_safe(newspage_menutitle), child.entity.all()[0].get_absolute_url()) 
                if request.path == new_node.get_absolute_url():
                    new_node.selected = True
                    child.selected=False
                    child.childrens.append(new_node)
                # this is a hack - it's only here because currently the menu injection doesn't seem to respect extra_inactive, and so without it, unwanted items appear in the menu
                if child.get_absolute_url() in request.path:
                    child.childrens.append(new_node)
            recursive(child.childrens)
    recursive(navigation_tree)

def recursive(nodes):
    
    if child in pages and child.entity.all()[0].auto_vacancies_page:
        menutitle = "injected: " + child.entity.all()[0].vacancies_page_menu_title
        new_node = NavigationNode(mark_safe(menutitle), child.entity.all()[0].get_absolute_url()  + "vacancies-and-studentships/")
        if request.path in new_node.get_absolute_url():
            if request.path == new_node.get_absolute_url():
                new_node.selected = True
                child.selected=False
            child.childrens.append(new_node)
        if child.get_absolute_url() in request.path:
            child.childrens.append(new_node)
            
            
this is the code to mark as active the current item:

if request.path in new_node.get_absolute_url():
    print "request path is url"
    new_node.selected = True
    child.selected=False
            

"""