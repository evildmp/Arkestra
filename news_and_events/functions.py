from models import NewsAndEventsPlugin, NewsArticle, Event
from django.db.models import Q
from datetime import datetime
import operator
from django.conf import settings
from contacts_and_people.models import Entity

multiple_entity_mode = getattr(settings, "MULTIPLE_ENTITY_MODE", False)
if not multiple_entity_mode:
    default_entity = Entity.objects.get(id = getattr(settings, 'ARKESTRA_BASE_ENTITY'))
else:
    default_entity = None

def get_news_and_events(instance):
    # initialise some variables
    set_defaults(instance)
    convert_and_save_old_format(instance)
    get_items(instance)   
    #apply_limits(instance)
    set_links_to_more_views(instance)
    determine_layout_settings(instance)
    set_templates(instance)
    set_layout_classes(instance)
    return

def set_defaults(instance):
    # set defaults
    instance.link_to_news_and_events = None
    instance.other_events = []
    instance.forthcoming_events = []
    instance.other_news = []  
    instance.show_news_when = instance.show_events_when = True
    instance.newsindex = instance.eventsindex = False
    try:
        instance.view
    except AttributeError:
        instance.view = "current"
    return
    
def convert_and_save_old_format(instance):
    # the older version used integers; this will convert and save them
    if instance.format == "0":
        instance.format = "title"
        instance.save()
    if instance.format == "1":
        instance.format = "details"
        instance.save()
    if instance.display == "0":
        instance.display = "news_and_events"
        instance.save()
    if instance.display == "1":
        instance.display = "news"
        instance.save()
    if instance.display == "2":
        instance.display = "events"
        instance.save()
    return

def determine_layout_settings(instance):
    # determine layout and other settings
    if "featured" in instance.format:
        instance.image_size = (75,75)
        instance.show_news_when = instance.show_events_when = False

        if "horizontal" in instance.format:
            instance.news_list_class = instance.events_list_class = "row columns" + str(instance.limit_to) + " " + instance.format

            if instance.news:
                for item in instance.news:
                    item.column_class = "column"
                    item.listitem_template = "includes/news_listitem_featured.html"
                instance.news[0].column_class = instance.news[0].column_class + " firstcolumn"
                instance.news[-1].column_class = instance.news[-1].column_class + " lastcolumn"

            if instance.events:
                for item in instance.events:
                    item.column_class = "column"
                instance.events[0].column_class = instance.events[0].column_class + " firstcolumn"
                instance.events[-1].column_class = instance.events[-1].column_class + " lastcolumn"               
        
        elif "vertical" in instance.format:
            instance.news_list_class = instance.events_list_class = "row columns1"
        instance.format = "featured"
    else:
        instance.image_size = (75,75)
        instance.news_list_class = instance.events_list_class = "news_and_events"
    return

def apply_limits(instance):
    # apply the appropriate limits and "more items" links            
    if instance.events:
        if instance.limit_to and len(instance.events) > instance.limit_to:
            instance.events = instance.events[:instance.limit_to]
    if instance.news:
        if instance.limit_to and len(instance.news) > instance.limit_to:
            instance.news = instance.news[:instance.limit_to]
    print "instance.limit_to", instance.limit_to
    return

def set_links_to_more_views(instance):
    """Determines whether we need to offer links to other views of news/events for this entity"""
    if instance.type == "plugin":
        if instance.news:
            instance.link_to_news_and_events = "news"
            if instance.limit_to and len(instance.news) > instance.limit_to:
                instance.news = instance.news[:instance.limit_to]
        if instance.events:
            if instance.limit_to and len(instance.events) > instance.limit_to:
                instance.events = instance.events[:instance.limit_to]
            if instance.link_to_news_and_events:
                instance.link_to_news_and_events = "news & events"
            else:
                instance.link_to_news_and_events = "events"
    # not a plugin, but still current     
    elif instance.view == "current":
        if instance.previous_events or instance.forthcoming_events:
            if instance.limit_to and len(instance.events) > instance.limit_to:
                instance.events = instance.events[:instance.limit_to]
                if instance.forthcoming_events.count() > len(instance.events):
                    instance.other_events.append({
                        "link":"all-forthcoming", 
                        "title":"all forthcoming events", 
                        "count": instance.forthcoming_events.count(),}
                        )
        if instance.previous_events:
            instance.other_events.append({
                "link":"previous-events", 
                "title":"previous events",
                "count": instance.previous_events.count(),}
                )    
        if instance.news:
            all_news_count = len(instance.news)
            if instance.limit_to and all_news_count > instance.limit_to:
                instance.news = instance.news[:instance.limit_to]
                instance.other_news = [{
                    "link":"news-archive", 
                    "title":"news archive",
                    "count": all_news_count,}]
        print "instance.limit_to", instance.limit_to
    # an archive
    elif instance.view == "archive":
        if instance.forthcoming_events[instance.default_limit:]:
            instance.other_events = [{
                "link":"all-forthcoming", 
                "title":"all forthcoming events", 
                "count": instance.forthcoming_events.count(),}]
    if instance.type <> "plugin" and not (instance.news and instance.events): 
        if instance.news and len(instance.news) > instance.limit_to:
            instance.newsindex = True
        if instance.events and len(instance.events) > instance.limit_to:
            instance.eventsindex = True
    if instance.type == "sub_page":
        if instance.news:
            instance.link_to_news_and_events = "news"
            if instance.limit_to and len(instance.news) > instance.limit_to:
                instance.news = instance.news[:instance.limit_to]
        if instance.events:
            if instance.limit_to and len(instance.events) > instance.limit_to:
                instance.events = instance.events[:instance.limit_to]
            if instance.link_to_news_and_events:
                instance.link_to_news_and_events = "news & events"
            else:
                instance.link_to_news_and_events = "events"
    return

def set_templates(instance):
    # set the templates for the list items
    instance.news_listitem_template = "includes/news_listitem_" + instance.format + ".html"
    instance.events_listitem_template = "includes/event_listitem_" + instance.format + ".html"
    return

def get_items(instance):
    # goes to the appropriate functions to get lists of items
    instance.news = instance.events = None
    if "news" in instance.display:
        if instance.order_by == "importance/date":
            top_news, ordinary_news = get_news_ordered_by_importance_and_date(instance)
            instance.news =  top_news + ordinary_news
        else:
            instance.news = get_publishable_news(instance)
        instance.news_index_items = [newsitem for newsitem in instance.news if not getattr(newsitem, 'sticky', False)]


    if "events" in instance.display:
        print ">> ------- instance.view", instance.view
        get_events(instance)
        if instance.view == "archive":
            print "archive"
            instance.events = instance.previous_events
        elif instance.order_by == "importance/date":
            top_events, ordinary_events = get_events_ordered_by_importance_and_date(instance)
            instance.events =  top_events + ordinary_events
        else:
            instance.events = instance.forthcoming_events
        instance.events_index_items = [event for event in instance.events if not getattr(event, 'sticky', False)]
    return         

def set_layout_classes(instance):
    """
    Lays out the plugin's news and events divs
    """
    instance.row_class="plugin row"
    if instance.layout == "sidebyside":
        instance.news_div_class = instance.events_div_class = "column firstcolumn"
        if instance.news and instance.events:
            instance.row_class=instance.row_class+" columns2"
            instance.events_div_class = "column lastcolumn"
        elif instance.newsindex or instance.eventsindex:
            instance.row_class=instance.row_class+" columns3"
            instance.index_div_class = "column lastcolumn"
            instance.news_div_class = instance.events_div_class = "column firstcolumn doublecolumn"
        else: 
            instance.row_class=instance.row_class+" columns1"
    return
                
def get_events_ordered_by_importance_and_date(instance):
    ordinary_events = []
    # split the within-date items for this entity into two sets
    actual_events = instance.forthcoming_events
    top_events = actual_events.filter(
        Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
        jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
        ).order_by('importance').reverse()  
    non_top_events = actual_events.exclude(
        Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
        jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
        )
    print "_____________________________________________________"
    print "Top events", top_events
    print "Non top events", non_top_events.count()
    top_events = list(top_events)

    # now we have to go through the non-top items, and find any that can be promoted
    # get the set of dates where possible promotable items can be found             
    dates = non_top_events.dates('start_date', 'day')
    print "_____________________________________________________"
    print "Going through the date set"
    for date in dates:
        print "  examining possibles from", date
        # get all non-top items from this date
        possible_top_events = non_top_events.filter(
            start_date = date)
        # promotable items have importance > 0
        print "    found", possible_top_events.count(), "of which I will promote", possible_top_events.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1).count()
        # promote the promotable items
        top_events.extend(possible_top_events.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1))
        # if this date set contains any unimportant items, then there are no more to promote
        demotable_items = possible_top_events.exclude(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1)
        if demotable_items.count() > 0:
            # put those unimportant items into ordinary news
            ordinary_events.extend(demotable_items)
            print "    demoting",  demotable_items.count()
            # and stop looking for any more
            break
    # and everything left in non-top items after this date
    if dates:
        remaining_items = non_top_events.filter(start_date__gt=date)
        print "  demoting the remaining", remaining_items.count()            
        ordinary_events.extend(remaining_items)
        for item in top_events:
            item.sticky = True
        print "_____________________________________________________"
        print "Top events", len(top_events)
        print "Ordinary events", len(ordinary_events)
        ordinary_events.sort(key=operator.attrgetter('start_date'))
    return list(top_events), ordinary_events
    
def get_actual_events(instance):
    actual_events = get_all_events(instance).filter(
        # if it's (not a series and not a child) or if its parent is a series ....
        Q(series = False, parent = None) | Q(parent__series = True,  parent__do_not_advertise_children = False), 
        # ... and it's (a single-day event starting after today) or (not a single-day event and ends after today)     
        Q(single_day_event = True, start_date__gte = datetime.now()) | Q(single_day_event = False, end_date__gte = datetime.now())
        ).order_by('start_date')
    print "_____________________________________________________"
    print "Actual events", actual_events.count()
    return actual_events

def get_previous_events(instance):
    previous_events = get_all_events(instance).filter(
        # if it's (not a series and not a child) or if its parent is a series ....
        Q(series = False, parent = None) | Q(parent__series = True,  parent__do_not_advertise_children = False), 
        # ... and it's (a single-day event starting after today) or (not a single-day event and ends after today)     
        Q(single_day_event = True, start_date__lt = datetime.now()) | Q(single_day_event = False, end_date__lt = datetime.now())
        )
    print "_____________________________________________________"
    print "Previous events", previous_events.count()
    return previous_events        

def get_events(instance):
    instance.entity = instance.entity or work_out_entity(context, None)
    all_events = Event.objects.filter(Q(hosted_by=instance.entity) | Q(publish_to=instance.entity)).distinct().order_by('start_date')
    # if an entity should automatically publish its descendants' items
    #     all_events = Event.objects.filter(Q(hosted_by__in=instance.entity.get_descendants(include_self=True)) | Q(publish_to=instance.entity)).distinct().order_by('start_date')
    print "_____________________________________________________"
    print "All events", all_events.count()
    
    actual_events = all_events.filter(
        # if it's (not a series and not a child) - series events are excluded, children too unless:
        # the child's parent is a series and its children can be advertised
        # tough luck if it's the child of a series and can't be advertised
        Q(series = False, parent = None) | Q(parent__series = True,  parent__do_not_advertise_children = False), 
        )
    print "_____________________________________________________"
    print "Actual events", actual_events.count()
        
    instance.forthcoming_events = actual_events.filter(  
        # ... and it's (a single-day event starting after today) or (not a single-day event and ends after today)     
        Q(single_day_event = True, start_date__gte = datetime.now()) | Q(single_day_event = False, end_date__gte = datetime.now())
        ).order_by('start_date')

    instance.previous_events = actual_events.exclude(  
        # ... and it's (a single-day event starting after today) or (not a single-day event and ends after today)     
        Q(single_day_event = True, start_date__gte = datetime.now()) | Q(single_day_event = False, end_date__gte = datetime.now())
        ).order_by('-start_date')
        
    print "_____________________________________________________"
    print "Previous events", instance.previous_events.count()
        
    instance.series_events = all_events.filter(series = True)
    print "_____________________________________________________"
    print "Series events", instance.series_events.count()

    return 

def get_news_ordered_by_importance_and_date(instance):
    ordinary_news = []
    # split the within-date items for this entity into two sets

    publishable_news = get_publishable_news(instance)
    sticky_news = publishable_news.order_by('-importance').filter(
        Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),
        sticky_until__gte=datetime.today(),  
        )
    non_sticky_news = publishable_news.exclude(
        Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),
        sticky_until__gte=datetime.today(), 
        )
    print "_____________________________________________________"
    print "Sticky news", sticky_news.count()
    print "Non-sticky news", non_sticky_news.count()
    top_news = list(sticky_news)

    # now we have to go through the non-top items, and find any that can be promoted
    # get the set of dates where possible promotable items can be found             
    dates = non_sticky_news.dates('date', 'day').reverse()
    print "_____________________________________________________"
    print "Going through the date set"
    for date in dates:
        print "  examining possibles from", date
        # get all non-top items from this date
        possible_top_news = non_sticky_news.filter(date__year=date.year, date__month= date.month, date__day= date.day)
        # promotable items have importance > 0
        print "    found", possible_top_news.count(), "of which I will promote", possible_top_news.filter(Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),importance__gte = 1).count()
        # add the good ones to the top news list
        top_news.extend(possible_top_news.filter(
            Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),
            importance__gte = 1)
            )
        # if this date set contains any unimportant items, then there are no more to promote
        demotable_items = possible_top_news.exclude(
            Q(hosted_by=instance.entity) | Q(is_sticky_everywhere = True),
            importance__gte = 1
            )
        if demotable_items.count() > 0:
            # put those unimportant items into ordinary news
            ordinary_news.extend(demotable_items)
            print "    demoting",  demotable_items.count()
            # and stop looking for any more
            break
    # and add everything left in non-sticky news before this date
    if dates:
        remaining_items = non_sticky_news.filter(date__lte=date)
        print "  demoting the remaining", remaining_items.count()
        ordinary_news.extend(remaining_items)
        for item in top_news:
            item.sticky = True
        print "_____________________________________________________"
        print "Top news", len(top_news)
        print "Ordinary news", len(ordinary_news)
        ordinary_news.sort(key=operator.attrgetter('date'), reverse = True)
    return top_news, ordinary_news

def get_publishable_news(instance):
    # returns news items that can be published, latest news first
    publishable_news = get_all_news(instance) \
        .filter(date__lte = datetime.today()) \
        .order_by('-date')
    print "_____________________________________________________"
    print "Publishable news", publishable_news.count()
    return publishable_news


def get_all_news(instance):
    # returns every news item associated with this entity
    if multiple_entity_mode:
        all_news = NewsArticle.objects.filter(
            Q(hosted_by=instance.entity) | Q(publish_to=instance.entity)
            ).distinct()
    else:
        all_news = NewsArticle.objects.all()
    print "_____________________________________________________"
    print "All news", all_news.count()
    return all_news