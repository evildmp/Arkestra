from classytags.arguments import IntegerArgument, Argument
from classytags.core import Options
from classytags.helpers import InclusionTag

from django import template

from cms.menu import page_to_node
from menus.templatetags.menu_tags import cut_levels
from menus.menu_pool import apply_modifiers


register = template.Library()

class ShowRootMenu(InclusionTag):
    template = 'cms/cardiff_menu.html'
    name = "show_root_menu"

    options = Options(
        Argument('template', default='menu/menu.html', required=False),
    )

    def get_context(self, context, template):

        try:
            # If there's an exception (500), default context_processors may not be called.
            request = context['request']
        except KeyError:
            return {'template': 'menu/empty.html'}
            
        page = request.current_page
        node = page_to_node(page, page, None)
        children = cut_levels([node], 0, 100, 0, 1)
        children = apply_modifiers(children, request, None, None, post_cut=True)
        # try:
        context.update({'children':children,
                        'template':template,})
        # except:
        context = {"template":template}

        return context

register.tag(ShowRootMenu)


