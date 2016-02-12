from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.cache import cache
from django.db.models.loading import get_model

from cms.models import Page

from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from menus.base import Modifier

from arkestra_utilities.settings import ARKESTRA_MENUS


try:
    # django CMS < 2.4
    CACHE_DURATIONS = settings.CMS_CACHE_DURATIONS['menus']
except AttributeError:
    # django CMS 2.4 +
    from cms.utils import get_cms_setting
    CACHE_DURATIONS = get_cms_setting('CACHE_DURATIONS')['menus']


menus = []
for menu in ARKESTRA_MENUS:
    # old style
    if type(menu) is dict:

        if menu.get("lister_name"):
            lister_module = __import__(
                menu["lister_module"],
                fromlist=[menu["lister_name"]]
                )
            menu["lister"] = getattr(lister_module, menu["lister_name"])

        menus.append(menu)

    # new style
    elif type(menu) is str:
        module_name, dot, class_name = menu.rpartition(".")
        menu_class = __import__(
            module_name,
            fromlist=[class_name]
            )
        menus.append(getattr(menu_class, class_name))

# ArkestraPages(Modifier) checks whether there are Entities that have automatic
# pages (contacts & people, news & events, etc) that should be featured in the
# menu.
#
# These menu might have this structure:
#
#   Department of Witchcraft    [the home page of the Entity]
#       About witchcraft        [an ordinary CMS Page]
#       Cats & hats             [an ordinary CMS Page]
#       News & Events           [an Arkestra automatic page]
#           Previous Events     [an Arkestra automatic page - won't appear in
#                                menu unless News & Events is selected]
#           News Archive        [an Arkestra automatic page - won't appear in
#                                menu unless News & Events is selected]
#       Contacts & People       [an Arkestra automatic page]
#


def entity_for_node(id):
    """
    If this node represents a page that is an entity's home page, return that;
    otherwise return False
    """
    try:
        # does this node.id represent a page that is an entity's home page?
        return Page.objects.get(id=id).entity.all()[0]
    except (Page.DoesNotExist, IndexError) as e:
        print "getting alternative"
        # if not, maybe the publisher_public version of the page is the one...
        try:
            return Page.objects.get(id=id).publisher_public.entity.all()[0]
        except (Page.DoesNotExist, IndexError) as e:
            return False


class ArkestraPages(Modifier):
    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):

        # this currently relies on the pre-cut nodes
        self.nodes = nodes
        self.auto_page_url = getattr(request, "auto_page_url", None)
        self.request = request

        if menus and not post_cut:
            key = "ArkestraPages.modify()" + request.path + "pre_cut"
            cached_pre_cut_nodes = cache.get(key, None)
            if cached_pre_cut_nodes:
                return cached_pre_cut_nodes

            # loop over all the nodes returned by the nodes in the Menu classes
            for node in self.nodes:

                # for each node, try to identify the Entity for it
                node.entity = entity_for_node(node.id)

                if node.entity:
                    for menu_class in menus:
                        if type(menu_class) is dict:
                            self.do_old_menu(node, menu_class, node.entity)
                        else:
                            self.do_menu(node, menu_class, node.entity)


            # print "    ++ saving cache", key
            cache.set(key, self.nodes, CACHE_DURATIONS)
            # print "    **", len(self.nodes), "nodes in", datetime.now() -
            # start_time, "for ArkestraPages.modify()"
            return self.nodes
        else:
            # print "** post_cut"
            # for node in self.nodes:
            #     # we have found a node for a Page with an Entity, so check it
            #       against arkestra_menus
            #     for menu in arkestra_menus:
            #         # self.do_menu(node, menu, node.entity)
            #         pass
            return self.nodes

    def do_menu(self, node, menu_class, entity):

        entity_model = getattr(menu_class, "entity_model", None)
        # check if we are we using an entity_model
        if entity_model:
            try:
                # can we get and entity_model instance?
                entity_model_instance = entity_model.objects.get(entity=entity)
                # if it doesn't want the page published, give up
                if entity_model_instance.publish_page is False:
                    return
                menu_title = entity_model_instance.menu_title
            # if no entity_model instance has been created for this entity
            except entity_model.DoesNotExist:
                return

        # not using an entity_model; determine menu_title from class
        else:
            menu_title = menu_class.menu_title

        # check if we're using a lister,
        if getattr(menu_class, "lister", None):
            lister_ = menu_class.lister(entity=entity)
            if not lister_.lists:
                return

        # if we haven't bailed out yet, create the menu node
        new_node = self.create_new_node(
            title=menu_title,
            url=entity.get_auto_page_url(menu_class.url),
            parent=node,
            )

        # does this menu call for sub-menu items?
        if getattr(menu_class, "sub_menus", None):
            for list_ in lister_.lists:
                # and go through the other_items lists for each,
                # creating a node for each
                for other_item in list_.other_items():
                    self.create_new_node(
                        title=other_item["title"],
                        url=other_item["link"],
                        parent=new_node,
                    )

    def do_old_menu(self, node, menu_class, entity):
        # does this entity have this kind of auto-page in the menu?
        if getattr(entity, menu_class["auto_page_attribute"]):
            if menu_class.get("lister"):
                # create an instance of the lister with appropriate attributes
                lister_ = menu_class.get("lister")(entity=entity)
                # use the instance to create an instance of the plugin
                # publisher
                if lister_.lists:
                    new_node = self.create_new_node(
                        title=getattr(entity, menu_class["title_attribute"]),
                        url=entity.get_auto_page_url(
                            menu_class["url_attribute"]
                            ),
                        parent=node
                        )
                    # does this menu call for sub-menu items?
                    if menu_class.get("sub_menus", None):
                        for list_ in lister_.lists:
                            # and go through the other_items lists for each,
                            # creating a node for each
                            for other_item in list_.other_items():
                                self.create_new_node(
                                    title=other_item["title"],
                                    url=other_item["link"],
                                    parent=new_node,
                                )

            else:
                new_node = self.create_new_node(
                    title=getattr(entity, menu_class["title_attribute"]),
                    url=entity.get_auto_page_url(menu_class["url_attribute"]),
                    parent=node,
                    )
            # if new_node:
            #     for sub_menu in menu["sub_menus"]:
            #         self.do_menu(node, sub_menu, entity)

        # return new_nodes

    def create_new_node(self, title, url, parent):
        # create a new node for the menu
        new_node = NavigationNode(
            title=mark_safe(title),
            url=url,
            id=None
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
