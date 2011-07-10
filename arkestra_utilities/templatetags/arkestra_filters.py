from django import template

register = template.Library()

@register.filter
def truncatewords_by_chars(value, arg):
    """
    Truncate words based on the number of characters
    based on original truncatewords filter code
    
    Receives a parameter separated by spaces where each field means:
     - limit: number of characters after which the string is truncated
     - lower bound: if char number is higher than limit, truncate by lower bound
     - higher bound: if char number is less than limit, truncate by higher bound
    """
    from django.utils.text import truncate_words
    try:
        args = arg.split(' ')
        limit = int(args[0])
        lower = int(args[1])
        higher = int(args[2])
    except ValueError: # Invalid literal for int().
        return value
    if len(value) >= limit:
        return truncate_words(value, lower)
    if len(value) < limit:
        return truncate_words(value, higher)