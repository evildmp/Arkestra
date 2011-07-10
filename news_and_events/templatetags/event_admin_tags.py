from django import template

register = template.Library()

def show_event_tree_item(context, event):
    if context.has_key("cl"):
        filtered = False#context['cl'].is_filtered()
    elif context.has_key('filtered'):
        filtered = context['filtered']
    context.update({'filtered':filtered, 'event':event})
    return context

show_event_tree_item = register.inclusion_tag(
        'admin/news_and_events/event/change_list_tree_items.html',
        takes_context=True)(show_event_tree_item)
