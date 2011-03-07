from django import template

register = template.Library()

def show_externalsite_tree_item(context, externalsite):
    request = context['request']
    if context.has_key("cl"):
        filtered = False#context['cl'].is_filtered()
    elif context.has_key('filtered'):
        filtered = context['filtered']
    context.update({'filtered':filtered, 'externalsite':externalsite})
    return context
show_externalsite_tree_item = register.inclusion_tag(
        'admin/links/externalsite/change_list_tree_items.html',
        takes_context=True)(show_externalsite_tree_item)


