from django import template

register = template.Library()

def show_entity_tree_item(context, entity):
    """
    For the entity tree in admin
    """
    if context.has_key("cl"):
        filtered = False # context['cl'].is_filtered()
    elif context.has_key('filtered'):
        filtered = context['filtered']
    context.update({'filtered':filtered, 'entity':entity})
    return context

show_entity_tree_item = register.inclusion_tag(
        'admin/contacts_and_people/entity/change_list_tree_items.html',
        takes_context=True)(show_entity_tree_item)


