from models import Vacancy, Studentship
from django.db.models import Q
from datetime import datetime
import operator
from django.conf import settings
from contacts_and_people.models import Entity
# from contacts_and_people.templatetags.entity_tags import work_out_entity
from itertools import groupby

MULTIPLE_ENTITY_MODE = settings.MULTIPLE_ENTITY_MODE

def get_vacancies_and_studentships(instance):
    """
    instance.display
        vacancies:              show vacancies
        studentships:           show studentships
        vacancies studentships: show both
        
    instance.view
        current:            future (may be limited)
        all_forthcoming:    future studentships without limit
        archive:            past 
      
    instance.order_by
        importance/date:    show important items first, then by date
        date:               by date only

    instance.format
        featured horizontal:    limited to 3, layout stacked, importance/date, use images
        featured vertical:      limited to 3, importance/date, use images

    instance.type
        main_page       a main vacancies and studentships page
        sub_page        archive, all forthcoming
        plugin          produced by a plugin
        for_person      raised by a {% person_studentships %} tag in a person template
        
    vacanciesindex
    studentshipsindex
    vacancies_index_items
    studentships_index_items 
    """
    print
    print "___________________________ Getting vacancies and studentships _______________________"
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

    if "vacancies" in instance.display:          # have we been asked to get vacancies?
        print
        print "============ Getting vacancies ============"
        get_vacancies(instance)            # go and get vacancies
        if instance.order_by == "archive":
            instance.vacancies = instance.archived_vacancies
            top_vacancies, ordinary_vacancies = get_vacancies_ordered_by_importance_and_date(instance)
        elif instance.order_by == "importance/date" and instance.view == "current":
            get_vacancies_ordered_by_importance_and_date(instance)
            instance.vacancies = instance.top_vacancies + instance.ordinary_vacancies
        else: 
            instance.vacancies = instance.all_current_vacancies
            
    if "studentships" in instance.display:    # have we been asked to get studentships?
        print
        print "============ Getting studentships ============"
        get_studentships(instance)            # go and get studentships
        if instance.view == "archive":
            instance.studentships = instance.archived_studentships
        # keep top studentships together where appropriate - not in long lists if COLLECT_TOP_ALL_FORTHCOMING_EVENTS is False
        elif instance.order_by == "importance/date" and (instance.view == "current" or COLLECT_TOP_ALL_FORTHCOMING_EVENTS):
            get_studentships_ordered_by_importance_and_date(instance)
            instance.studentships = instance.top_studentships + instance.ordinary_studentships
        else: 
            instance.studentships = instance.all_current_studentships
            
        build_indexes(instance)
    set_links_to_more_views(instance)       # limit lists, set links to previous/archived/etc items as needed
    set_limits_and_indexes(instance)
    determine_layout_settings(instance)     # work out a layout
    set_templates(instance)                 # choose template files
    set_layout_classes(instance)            # apply CSS classes
    return instance

def set_defaults(instance):
    # set defaults
    instance.vacancies = instance.studentships = None
    instance.link_to_vacancies_and_studentships_page = None # link to more vacancies and/or studentships for this entity
    instance.other_studentships = []  # a list of dicts recording what other studentships are available
    instance.all_current_studentships = []        # actual forthcoming studentships
    instance.other_vacancies = []                # dicts recording kinds of other vacancies available
    instance.show_vacancies_when = instance.show_studentships_when = True # show date groupers?
    instance.vacanciesindex = instance.studentshipsindex = False # show an index?
    instance.vacancies_index_items = instance.studentships_index_items = []
    instance.limit_to = getattr(instance, "limit_to", None)
    instance.layout = getattr(instance, "layout", "sidebyside")
    instance.show_images = getattr(instance, "show_images", True)
    instance.show_venue = getattr(instance, "show_venue", True)
    instance.at_venue = getattr(instance, "at_venue", None) # if specified, only show venue's studentships
    # are we looking at current or archived items?
    try:
        instance.view
    except AttributeError:
        instance.view = "current"
    return

def set_links_to_more_views(instance):
    """
    determines whether we need to offer links to other views of vacancies/studentships for this entity
    if this is a plugin, create the "More vacancies/studentships" link
    limits "current" views to the number of items specified in settings
    """
    if instance.type == "plugin":
        if (instance.vacancies or instance.studentships) and instance.entity.auto_vacancies_page:
            instance.link_to_vacancies_and_studentships_page = instance.entity.get_related_info_page_url("vacancies-and-studentships")

    # not a plugin, but showing current studentships items on main page
    if instance.type == "main_page" or instance.type == "sub_page":
        if instance.view == "current":
            if instance.archived_studentships or instance.all_current_studentships:
                if instance.limit_to and len(instance.studentships) > instance.limit_to:
                    # instance.studentships = instance.studentships[:instance.limit_to]
                    if instance.all_current_studentships.count() > instance.limit_to:
                        instance.other_studentships.append({
                            "link":instance.entity.get_related_info_page_url("all-current-studentships"), 
                            "title":"all forthcoming studentships", 
                            "count": instance.all_current_studentships.count(),}
                            )
            if instance.archived_studentships:
                instance.other_studentships.append({
                    "link":instance.entity.get_related_info_page_url("studentship-archive"), 
                    "title":"previous studentships",
                    "count": instance.archived_studentships.count(),}
                    )    
            if instance.archived_vacancies or instance.all_current_vacancies:
                if instance.limit_to and len(instance.vacancies) > instance.limit_to:
                    # instance.studentships = instance.studentships[:instance.limit_to]
                    if instance.all_current_vacancies.count() > instance.limit_to:
                        instance.other_vacancies.append({
                            "link":instance.entity.get_related_info_page_url("all-current-vacancies"), 
                            "title":"all forthcoming vacancies", 
                            "count": instance.all_current_vacancies.count(),}
                            )
            if instance.archived_vacancies:
                instance.other_vacancies.append({
                    "link":instance.entity.get_related_info_page_url("vacancy-archive"), 
                    "title":"previous vacancies",
                    "count": instance.archived_vacancies.count(),}
                    )    
        # an archive
        elif instance.view == "archive":
            if instance.all_current_studentships[instance.default_limit:]:
                instance.other_studentships = [{
                    "link":instance.entity.get_related_info_page_url("forthcoming-studentships"), 
                    "title":"all forthcoming studentships", 
                    "count": instance.all_current_studentships.count(),}]                
    return

def set_limits_and_indexes(instance):
    if instance.vacancies and len(instance.vacancies) > instance.limit_to:
        instance.vacancies = instance.vacancies[:instance.limit_to]
        instance.vacancies_index_items = [vacancy for vacancy in instance.vacancies if not getattr(vacancy, 'sticky', False)] # put non-top items in it
    no_of_vacancies_get_whens = len(set(vacancy.get_when() for vacancy in instance.vacancies_index_items))
    if instance.type == "sub_page" and len(set(vacancy.get_when() for vacancy in instance.vacancies_index_items)) > 1: # more than get_when()?
        instance.vacanciesindex = True   # show an index
    if "featured" in instance.format or no_of_vacancies_get_whens < 2:
        instance.show_vacancies_when = False

    if instance.studentships and len(instance.studentships) > instance.limit_to:
        instance.studentships = instance.studentships[:instance.limit_to]
        instance.studentships_index_items = [studentship for studentship in instance.studentships if not getattr(studentship, 'sticky', False)]
    no_of_studentship_get_whens = len(set(studentship.get_when() for studentship in instance.studentships_index_items))
    print no_of_studentship_get_whens
    if instance.type == "sub_page" and no_of_studentship_get_whens > 1:
        instance.studentshipsindex = True
    if "featured" in instance.format or no_of_studentship_get_whens < 2:
        instance.show_studentships_when = False

def determine_layout_settings(instance):
    # determine layout and other settings
    # instance.image_size
    # show_vacancies_when, instance.show_studentships_when
    
    if "featured" in instance.format:
        instance.image_size = (75,75)

        if "horizontal" in instance.format:
            instance.vacancies_list_class = instance.studentships_list_class = "row columns" + str(instance.limit_to) + " " + instance.format

            if instance.vacancies:
                for item in instance.vacancies:
                    item.column_class = "column"
                    item.list_item_template = "includes/vacancies_list_item_featured.html"
                instance.vacancies[0].column_class = instance.vacancies[0].column_class + " firstcolumn"
                instance.vacancies[-1].column_class = instance.vacancies[-1].column_class + " lastcolumn"

            if instance.studentships:
                for item in instance.studentships:
                    item.column_class = "column"
                instance.studentships[0].column_class = instance.studentships[0].column_class + " firstcolumn"
                instance.studentships[-1].column_class = instance.studentships[-1].column_class + " lastcolumn"               
        
        elif "vertical" in instance.format:
            instance.vacancies_list_class = instance.studentships_list_class = "row columns1"
        instance.format = "featured"
    else:
        instance.image_size = (75,75)
        instance.vacancies_list_class = instance.studentships_list_class = "vacancies-and-studentships"
        # instance.show_studentships_when = True    # no when group in featured style
    return

def set_templates(instance):
    # set the templates for the list items
    instance.vacancies_list_item_template = "includes/vacancies_list_item_" + instance.format + ".html"
    instance.studentships_list_item_template = "includes/studentship_list_item_" + instance.format + ".html"
    return

def set_layout_classes(instance):
    """
    Lays out the plugin's vacancies and studentships divs
    """
    instance.row_class="plugin row"
    # if vacancies and studentships will be side-by-side
    if instance.layout == "sidebyside":
        instance.vacancies_div_class = instance.studentships_div_class = "column firstcolumn" # if both vacancies & studentships we set the studentships column a few lines later
        if instance.vacancies and instance.studentships:
            instance.row_class=instance.row_class+" columns2"
            instance.studentships_div_class = "column lastcolumn"
        # if just vacancies or studentships, and it needs an index     
        elif instance.vacanciesindex or instance.studentshipsindex:
            instance.row_class=instance.row_class+" columns3"
            instance.index_div_class = "column lastcolumn"
            instance.vacancies_div_class = instance.studentships_div_class = "column firstcolumn doublecolumn"
        # and if it doesn't need an index    
        else: 
            instance.row_class=instance.row_class+" columns1"
    return
                
def get_studentships_ordered_by_importance_and_date(instance):
    """
    When we need more than just a simple list-by-date, this keeps the top items separate
    """
    print "____ get_studentships_ordered_by_importance_and_date() ____"
    ordinary_studentships = []
    # split the within-date items for this entity into two sets
    actual_studentships = instance.all_current_studentships
    # top_studentships jump the queue
    top_studentships = actual_studentships.filter(
        Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
        jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
        ).order_by('importance').reverse()  
    # non_top studentships are the rest
    non_top_studentships = actual_studentships.exclude(
        Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
        jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
        )
    print "Queue-jumping top studentships", top_studentships
    print "Non top studentships", non_top_studentships.count()

    # now we have to go through the non-top items, and find any that can be promoted to top_studentships
    # get the set of dates where possible promotable items can be found             
    dates = non_top_studentships.dates('start_date', 'day')
    print "Going through the date set"
    for date in dates:
        print "    examining possibles from", date
        # get all non-top items from this date
        possible_top_studentships = non_top_studentships.filter(
            start_date = date)
        # promotable items have importance > 0
        print "        found", possible_top_studentships.count(), "of which I will promote", possible_top_studentships.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1).count()
        # promote the promotable items
        list(top_studentships).extend(possible_top_studentships.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1))
        top_studentships = top_studentships | possible_top_studentships.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1)
        # print top_studentships | possible_top_studentships.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1))
        # if this date set contains any unimportant items, then there are no more to promote
        demotable_items = possible_top_studentships.exclude(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1)
        if demotable_items.count() > 0:
            # put those unimportant items into ordinary vacancies
            ordinary_studentships = demotable_items
            print "        demoting",  demotable_items.count()
            # and stop looking for any more
            break
    # and everything left in non-top items after this date
    if dates:
        remaining_items = non_top_studentships.filter(start_date__gt=date)
        print "    demoting the remaining", remaining_items.count()            
        ordinary_studentships = ordinary_studentships | remaining_items
        top_studentships = top_studentships
        ordinary_studentships = list(ordinary_studentships)
        for item in top_studentships:
            item.sticky = True
        
        print "Top studentships after processing", len(top_studentships), top_studentships
        print "Ordinary studentships", len(ordinary_studentships)
        # ordinary_studentships.sort(key=operator.attrgetter('start_date'))
    instance.top_studentships, instance.ordinary_studentships = list(top_studentships), ordinary_studentships
    return 
    
def get_actual_studentships(instance):
    actual_studentships = get_all_studentships(instance).filter(
        # if it's (not a series and not a child) or if its parent is a series ....
        Q(series = False, parent = None) | Q(parent__series = True,  parent__do_not_advertise_children = False), 
        # ... and it's (a single-day studentship starting after today) or (not a single-day studentship and ends after today)     
        Q(single_day_studentship = True, start_date__gte = datetime.now()) | Q(single_day_studentship = False, end_date__gte = datetime.now())
        ).order_by('start_date')
    print "_____________________________________________________"
    print "Actual studentships", actual_studentships.count()
    return actual_studentships

def get_archived_studentships(instance):
    archived_studentships = get_all_studentships(instance).filter(
        # if it's (not a series and not a child) or if its parent is a series ....
        Q(series = False, parent = None) | Q(parent__series = True,  parent__do_not_advertise_children = False), 
        # ... and it's (a single-day studentship starting after today) or (not a single-day studentship and ends after today)     
        Q(single_day_studentship = True, start_date__lt = datetime.now()) | Q(single_day_studentship = False, end_date__lt = datetime.now())
        )
    print "_____________________________________________________"
    print "Previous studentships", archived_studentships.count()
    return archived_studentships        

def get_studentships(instance):
    """
    returns all_current_studentships, archived_studentships, series_studentships
    """
    print "____ get_studentships() ____"
    if instance.type == "for_person":
        all_studentships = instance.person.studentship_featuring.all()
    elif instance.type == "for_place":
        all_studentships = instance.place.studentship_set.all()
    # most likely, we're getting studentships related to an entity
    elif MULTIPLE_ENTITY_MODE and instance.entity:
        all_studentships = Studentship.objects.filter(Q(hosted_by=instance.entity) | Q(publish_to=instance.entity)).distinct().order_by('closing_date')
    else:
        all_studentships = Studentship.objects.all()

        # if an entity should automatically publish its descendants' items
        #     all_studentships = Event.objects.filter(Q(hosted_by__in=instance.entity.get_descendants(include_self=True)) | Q(publish_to=instance.entity)).distinct().order_by('start_date')
    print "All studentships", instance.type, all_studentships.count()
            
    instance.all_current_studentships = all_studentships.filter(closing_date__gte = datetime.now())
    instance.archived_studentships = all_studentships.exclude(closing_date__gte = datetime.now())
        
    print "Previous studentships", instance.archived_studentships.count()
        
    return 

def get_vacancies_ordered_by_importance_and_date(instance):
    """
    When we need more than just a simple list-by-date, this keeps the top items separate
    """
    print "____ get_vacancies_ordered_by_importance_and_date() ____"
    ordinary_vacancies = []
    # split the within-date items for this entity into two sets
    actual_vacancies = instance.all_current_vacancies
    # top_vacancies jump the queue
    top_vacancies = actual_vacancies.filter(
        Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
        jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
        ).order_by('importance').reverse()  
    # non_top vacancies are the rest
    non_top_vacancies = actual_vacancies.exclude(
        Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),
        jumps_queue_on__lte=datetime.today(), jumps_queue_on__isnull=False,
        )
    print "Queue-jumping top vacancies", top_vacancies
    print "Non top vacancies", non_top_vacancies.count()

    # now we have to go through the non-top items, and find any that can be promoted to top_vacancies
    # get the set of dates where possible promotable items can be found             
    dates = non_top_vacancies.dates('start_date', 'day')
    print "Going through the date set"
    for date in dates:
        print "    examining possibles from", date
        # get all non-top items from this date
        possible_top_vacancies = non_top_vacancies.filter(
            start_date = date)
        # promotable items have importance > 0
        print "        found", possible_top_vacancies.count(), "of which I will promote", possible_top_vacancies.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1).count()
        # promote the promotable items
        list(top_vacancies).extend(possible_top_vacancies.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1))
        top_vacancies = top_vacancies | possible_top_vacancies.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1)
        # print top_vacancies | possible_top_vacancies.filter(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1))
        # if this date set contains any unimportant items, then there are no more to promote
        demotable_items = possible_top_vacancies.exclude(Q(hosted_by=instance.entity) | Q(jumps_queue_everywhere = True),importance__gte = 1)
        if demotable_items.count() > 0:
            # put those unimportant items into ordinary vacancies
            ordinary_vacancies = demotable_items
            print "        demoting",  demotable_items.count()
            # and stop looking for any more
            break
    # and everything left in non-top items after this date
    if dates:
        remaining_items = non_top_vacancies.filter(start_date__gt=date)
        print "    demoting the remaining", remaining_items.count()            
        ordinary_vacancies = ordinary_vacancies | remaining_items
        top_vacancies = top_vacancies
        ordinary_vacancies = list(ordinary_vacancies)
        for item in top_vacancies:
            item.sticky = True
        
        print "Top vacancies after processing", len(top_vacancies), top_vacancies
        print "Ordinary vacancies", len(ordinary_vacancies)
        # ordinary_vacancies.sort(key=operator.attrgetter('start_date'))
    instance.top_vacancies, instance.ordinary_vacancies = list(top_vacancies), ordinary_vacancies
    return 
    
def get_actual_vacancies(instance):
    print "get_actual_vacancies"
    actual_vacancies = get_vacancies(instance).filter(
        # if it's (not a series and not a child) or if its parent is a series ....
        Q(series = False, parent = None) | Q(parent__series = True,  parent__do_not_advertise_children = False), 
        # ... and it's (a single-day vacancy starting after today) or (not a single-day vacancy and ends after today)     
        Q(single_day_vacancy = True, start_date__gte = datetime.now()) | Q(single_day_vacancy = False, end_date__gte = datetime.now())
        ).order_by('start_date')
    print "_____________________________________________________"
    print "Actual vacancies", actual_vacancies.count()
    return actual_vacancies

def get_archived_vacancies(instance):
    archived_vacancies = get_vacancies(instance).filter(
        # if it's (not a series and not a child) or if its parent is a series ....
        Q(series = False, parent = None) | Q(parent__series = True,  parent__do_not_advertise_children = False), 
        # ... and it's (a single-day vacancy starting after today) or (not a single-day vacancy and ends after today)     
        Q(single_day_vacancy = True, start_date__lt = datetime.now()) | Q(single_day_vacancy = False, end_date__lt = datetime.now())
        )
    print "_____________________________________________________"
    print "Previous vacancies", archived_vacancies.count()
    return archived_vacancies        

def get_vacancies(instance):
    """
    returns all_current_vacancies, archived_vacancies, series_vacancies
    """
    print "____ get_vacancies() ____"
    if instance.type == "for_person":
        all_vacancies = instance.person.vacancy_featuring.all()
    elif instance.type == "for_place":
        all_vacancies = instance.place.vacancy_set.all()
    # most likely, we're getting vacancies related to an entity
    elif MULTIPLE_ENTITY_MODE and instance.entity:
        all_vacancies = Vacancy.objects.filter(Q(hosted_by=instance.entity) | Q(publish_to=instance.entity)).distinct().order_by('closing_date')
    else:
        all_vacancies = Vacancy.objects.all()

        # if an entity should automatically publish its descendants' items
        #     all_vacancies = Event.objects.filter(Q(hosted_by__in=instance.entity.get_descendants(include_self=True)) | Q(publish_to=instance.entity)).distinct().order_by('start_date')
    print "All vacancies", instance.type, all_vacancies.count()
            
    instance.all_current_vacancies = all_vacancies.filter(closing_date__gte = datetime.now())
    instance.archived_vacancies = all_vacancies.exclude(closing_date__gte = datetime.now())
        
    print "Previous vacancies", instance.archived_vacancies.count()
        
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
        instance.display = "vacancies_and_studentships"
        instance.save()
    if instance.display == "1":
        instance.display = "vacancies"
        instance.save()
    if instance.display == "2":
        instance.display = "studentships"
        instance.save()
    return
    
def build_indexes(instance):
    """docstring for build_indexes"""
    return
    print [{'grouper': key, 'list': list(val)}
            for key, val in
            groupby(instance.studentships, lambda v, f="start_date": f(v, True))
        ]