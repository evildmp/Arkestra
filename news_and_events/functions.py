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
    """
    display
        news:           show news
        events:         show events
        news events:    show both
        
    view (applies to events only)
        current:        future
        archive:        past 
      
    order_by
        importance/date:    show important items first, then by date
        date:               by date only

    format
        featured horizontal:    limited to 3, layout stacked, importance/date, use images
        featured vertical:      limited to 3, importance/date, use images

    type
        sub_page        news archive, events archive, all forthcoming events (the only kind that has indexes)
        plugin          produced by a plugin
        none            must be a main page
        for_person      raised by a {% person_events %} tag in a person template
        for_place      raised by a {% place_events %} tag in a person template
        
    newsindex
    eventsindex
    news_index_items
    events_index_items 
    """
    print
    print "___________________________ Getting news and events _______________________"
    print 
    set_defaults(instance)                  # initialise some variables
    print "instance.display", instance.display
    print "instance.view", instance.view
    print "instance.order_by", instance.order_by
    print "instance.format", instance.format
    print "instance.type", instance.type
    print "instance.limit_to", instance.limit_to
    print "instance.layout", instance.layout
 
    convert_and_save_old_format(instance)   # old-style values might need to be converted (surely no longer required)

    if "news" in instance.display:          # have we been asked to get news?
        if instance.order_by == "importance/date":
            top_news, ordinary_news = get_news_ordered_by_importance_and_date(instance)
            instance.news =  top_news + ordinary_news
        else:
            instance.news = get_publishable_news(instance)
        
    if "events" in instance.display:    # have we been asked to get events?
        get_events(instance)            #
        if instance.view == "archive":
            instance.events = instance.previous_events
        elif instance.order_by == "importance/date":
            get_events_ordered_by_importance_and_date(instance)
            instance.events = instance.top_events + instance.ordinary_events
        else: 
            instance.events = instance.forthcoming_events
        
    set_links_to_more_views(instance)       # limit lists, set links to previous/archived/etc items as needed
    set_limits_and_indexes(instance)
    determine_layout_settings(instance)     # work out a layout
    set_templates(instance)                 # choose template files
    set_layout_classes(instance)            # apply CSS classes
    return

def set_defaults(instance):
    # set defaults
    instance.news = instance.events = None
    instance.link_to_news_and_events = None # link to more news and/or events for this entity
    instance.other_events = []  # a list of dicts recording what other events are available
    instance.forthcoming_events = []        # actual forthcoming events
    instance.other_news = []                # dicts recording kinds of other news available
    instance.show_news_when = instance.show_events_when = True # show date groupers?
    instance.newsindex = instance.eventsindex = False # show an index?
    instance.news_index_items = instance.events_index_items = []
    instance.limit_to = getattr(instance, "limit_to", None)
    instance.layout = getattr(instance, "layout", "sidebyside")
    instance.show_images = getattr(instance, "show_images", True)
    instance.show_venue = getattr(instance, "show_venue", True)
    # are we looking at current or archived items?
    try:
        instance.view
    except AttributeError:
        instance.view = "current"
    return

def set_links_to_more_views(instance):
    """
    determines whether we need to offer links to other views of news/events for this entity
    if this is a plugin, create the "More news/events" link
    limits "current" views to the number of items specified in settings
    """
    if instance.type == "plugin":
        if instance.news:
            instance.link_to_news_and_events = "news"
            # if instance.limit_to and len(instance.news) > instance.limit_to:
            #     instance.news = instance.news[:instance.limit_to]
        if instance.events:
            # if instance.limit_to and len(instance.events) > instance.limit_to:
            #     instance.events = instance.events[:instance.limit_to]
            if instance.link_to_news_and_events:
                instance.link_to_news_and_events = "news & events"
            else:
                instance.link_to_news_and_events = "events"
    # not a plugin, but still current     
    elif instance.view == "current":
        if instance.previous_events or instance.forthcoming_events:
            if instance.limit_to and len(instance.events) > instance.limit_to:
                # instance.events = instance.events[:instance.limit_to]
                if instance.forthcoming_events.count() > instance.limit_to:
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
                # instance.news = instance.news[:instance.limit_to]
                instance.other_news = [{
                    "link":"news-archive", 
                    "title":"news archive",
                    "count": all_news_count,}]
    # an archive
    elif instance.view == "archive":
        if instance.forthcoming_events[instance.default_limit:]:
            instance.other_events = [{
                "link":"all-forthcoming", 
                "title":"all forthcoming events", 
                "count": instance.forthcoming_events.count(),}]
                
    # if this is a news/events sub-page                
    if instance.type == "sub_page":
        if instance.news:
            instance.link_to_news_and_events = "news"
            if instance.link_to_news_and_events:
                instance.link_to_news_and_events = "news & events"
            else:
                instance.link_to_news_and_events = "events"
    return

def set_limits_and_indexes(instance):
    if instance.news and len(instance.news) > instance.limit_to:
        instance.news = instance.news[:instance.limit_to]
        instance.news_index_items = [newsitem for newsitem in instance.news if not getattr(newsitem, 'sticky', False)] # put non-top items in it
    no_of_news_get_whens = len(set(newsarticle.get_when() for newsarticle in instance.news_index_items))
    if instance.type == "sub_page" and len(set(newsarticle.get_when() for newsarticle in instance.news_index_items)) > 1: # more than get_when()?
        instance.newsindex = True   # show an index
    if "featured" in instance.format or no_of_news_get_whens < 2:
        instance.show_news_when = False

    if instance.events and len(instance.events) > instance.limit_to:
        instance.events = instance.events[:instance.limit_to]
        instance.events_index_items = [event for event in instance.events if not getattr(event, 'sticky', False)]
    no_of_event_get_whens = len(set(event.get_when() for event in instance.events_index_items))
    print no_of_event_get_whens
    if instance.type == "sub_page" and no_of_event_get_whens > 1:
        instance.eventsindex = True
    if "featured" in instance.format or no_of_event_get_whens < 2:
        instance.show_events_when = False

def determine_layout_settings(instance):
    # determine layout and other settings
    # instance.image_size
    # show_news_when, instance.show_events_when
    
    if "featured" in instance.format:
        instance.image_size = (75,75)

        if "horizontal" in instance.format:
            instance.news_list_class = instance.events_list_class = "row columns" + str(instance.limit_to) + " " + instance.format

            if instance.news:
                for item in instance.news:
                    item.column_class = "column"
                    item.list_item_template = "includes/news_list_item_featured.html"
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
        instance.news_list_class = instance.events_list_class = "news-and-events"
        # instance.show_events_when = True    # no when group in featured style
    return

def set_templates(instance):
    # set the templates for the list items
    instance.news_list_item_template = "includes/news_list_item_" + instance.format + ".html"
    instance.events_list_item_template = "includes/event_list_item_" + instance.format + ".html"
    return

def set_layout_classes(instance):
    """
    Lays out the plugin's news and events divs
    """
    instance.row_class="plugin row"
    # if news and events will be side-by-side
    if instance.layout == "sidebyside":
        instance.news_div_class = instance.events_div_class = "column firstcolumn" # if both news & events we set the events column a few lines later
        if instance.news and instance.events:
            instance.row_class=instance.row_class+" columns2"
            instance.events_div_class = "column lastcolumn"
        # if just news or events, and it needs an index     
        elif instance.newsindex or instance.eventsindex:
            instance.row_class=instance.row_class+" columns3"
            instance.index_div_class = "column lastcolumn"
            instance.news_div_class = instance.events_div_class = "column firstcolumn doublecolumn"
        # and if it doesn't need an index    
        else: 
            instance.row_class=instance.row_class+" columns1"
    return
                
def get_events_ordered_by_importance_and_date(instance):
    """
    When we need more than just a simple list-by-date, this keeps the top items separate
    """
    ordinary_events = []
    # split the within-date items for this entity into two sets
    actual_events = instance.forthcoming_events
    # top_events jump the queue
    top_events = actual_events.filter(
        Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
        jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
        ).order_by('importance').reverse()  
    # non_top events are the rest
    non_top_events = actual_events.exclude(
        Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
        jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
        )
    print "_____________________________________________________"
    print "Top events", top_events
    print "Non top events", non_top_events.count()

    # now we have to go through the non-top items, and find any that can be promoted to top_events
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
        list(top_events).extend(possible_top_events.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1))
        top_events = top_events | possible_top_events.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1)
        # print top_events | possible_top_events.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1))
        # if this date set contains any unimportant items, then there are no more to promote
        demotable_items = possible_top_events.exclude(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1)
        if demotable_items.count() > 0:
            # put those unimportant items into ordinary news
            ordinary_events = demotable_items
            print "    demoting",  demotable_items.count()
            # and stop looking for any more
            break
    # and everything left in non-top items after this date
    if dates:
        remaining_items = non_top_events.filter(start_date__gt=date)
        print "  demoting the remaining", remaining_items.count()            
        ordinary_events = ordinary_events | remaining_items
        top_events = list(top_events)
        ordinary_events = list(ordinary_events)
        for item in top_events:
            item.sticky = True
        
        print "_____________________________________________________"
        print "Top events", len(top_events), top_events
        print "Ordinary events", len(ordinary_events)
        # ordinary_events.sort(key=operator.attrgetter('start_date'))
    instance.top_events, instance.ordinary_events = top_events, ordinary_events
    return 
    
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
    """
    sets fortcoming_events, previous_events, series_events
    """
    if instance.type == "for_person":
        all_events = instance.person.event_featuring.all()
        print "all", all_events
    elif instance.type == "for_place":
        all_events = instance.place.event_set.all()
        print "all", all_events
    else:    
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
