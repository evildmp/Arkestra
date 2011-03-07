from django import template
from django.shortcuts import render_to_response
from django.db.models import Q
from news_and_events.models import Event
from contacts_and_people.models import Entity
from cms.models import Page
from datetime import datetime
#from django.template.defaultfilters import date

register = template.Library()
    
# @register.inclusion_tag('eventslist.html', takes_context = True)
# def events(context, format = "all_info", max_items = 20, entity = None):
#     """
#     probably no longer required
#     Publishes a date-ordered list of events
#     {% events format max_items %}
#     """
#     print "events_tags.events"        
#     if not entity:
#         entity = work_out_entity(context, entity)
#     events = entity.event_set.order_by('start_date').filter(
#         Q(series = False, parent = None)|Q(parent__series = True),
#         Q(single_day_event = True, start_date__gte = datetime.now()) | Q(single_day_event = False, end_date__gte = datetime.now())
#         )
#     previous_events =  entity.event_set.order_by('-start_date').filter(
#         Q(series = False, parent = None)|Q(parent__series = True),
#         Q(single_day_event = True, end_date__lt = datetime.now()) | Q(single_day_event = False, end_date__lt = datetime.now())
#         )
#     return {
#         'events': events[0: max_items],
#         'previous_events': previous_events, 
#         'format': format,
#         'entity': entity,
#         }        
    
@register.inclusion_tag('event_date_and_time.html', takes_context = True)
def event_date_and_time(context, event = None, date_time_info = None):
    date_and_time_heading = []
    date_and_time = []
    if not event:
        event = context.get('event')
    if not event.series:
        dates = event.get_dates()
        if dates and (date_time_info != "no_dates" or event.parent.series or not event.parent.single_day_event):
            date_and_time_heading.append("date")
            date_and_time.append(dates)
        times = event.get_times()
        if times and date_time_info != "no_times":
            date_and_time_heading.append("time")
            date_and_time.append(times)
    return {
        'event': event,
        'date_and_time_heading': date_and_time_heading,
        'date_and_time': date_and_time,
    }

@register.simple_tag
def event_simple_date_and_time(event):
    if not event:
        return
    if not event.series:
        date_and_time = [event.get_dates(),]
        times = event.get_times()
        if times:
            date_and_time.append(times)
        return date_and_time