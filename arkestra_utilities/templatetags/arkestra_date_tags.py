from django import template

from datetime import datetime
from django.template.defaultfilters import date
from arkestra_utilities.output_libraries.dates import nice_date

register = template.Library()

@register.simple_tag(takes_context = True)
def date(context, date = date):
    """
    The `date` argument is a context attribute containing the date you want published; if not specified, the "date" will be used by default.
    """
    date_format = "jS F Y"
    now = datetime.now()
    # this year? don't include the year
    if date.year == now.year:
        date_format = "jS F"
    # nicedate will use tomorrow, today or yesterday when appropriate
    date = nice_date(date, date_format) 
    return date