from models import Vacancy, Studentship
from django.db.models import Q
from datetime import datetime
from django.conf import settings
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
        all current:        current items without limit
        archive:            past 
      
    instance.order_by
        importance/date:    show important items first, then by date
        date:               by date only

    instance.group_dates    show get_whens to group items
        
    instance.format
        title
        details

    instance.list_format    
        horizontal:         limited to 3, layout: stacked, format: details 
        vertical:

    instance.type
        main_page       a main vacancies and studentships page
        sub_page        archive, all forthcoming (the only kind that has indexes)
        plugin          produced by a plugin
        for_person      raised by a {% person_studentships %} tag in a person template
        menu            the menu needs to know for the auto vacancies & studentships page
        
    vacanciesindex
    studentshipsindex
    vacancies_index_items
    studentships_index_items 
    """
    print
    print "___________________________ Getting vacancies and studentships _______________________"
    print 
    set_defaults(instance)                  # initialise some variables
    print "instance.type", instance.type
    print "instance.display", instance.display
    print "instance.view", instance.view
    print "instance.order_by", instance.order_by
    print "instance.group_dates", instance.group_dates
    print "instance.format", instance.format
    print "instance.list_format", instance.list_format
    print "instance.limit_to", instance.limit_to
    print "instance.layout", instance.layout
 
    convert_and_save_old_format(instance)   # old-style values might need to be converted (surely no longer required)

    if "vacancies" in instance.display:          # have we been asked to get vacancies?
        print
        print "---------------- Getting vacancies ----------------"
        get_vacancies(instance)            # go and get vacancies
        if instance.view == "archive":
            instance.vacancies = list(instance.archived_vacancies)
        elif instance.order_by == "importance/date" and instance.view == "current":
            instance.vacancies = list(instance.current_vacancies.order_by('importance').reverse())
        else: 
            instance.vacancies = list(instance.current_vacancies)

    if "studentships" in instance.display:    # have we been asked to get studentships?
        print
        print "---------------- Getting studentships ----------------"
        get_studentships(instance)            # go and get studentships
        if instance.view == "archive":
            instance.studentships = list(instance.archived_studentships)
        elif instance.order_by == "importance/date" and instance.view == "current":
            instance.studentships = list(instance.current_studentships.order_by('importance').reverse())
        else: 
            instance.studentships = list(instance.current_studentships)
            
    build_indexes(instance)
    set_links_to_more_views(instance)       # limit lists, set links to previous/archived/etc items as needed
    set_limits_and_indexes(instance)
    determine_layout_settings(instance)     # work out a layout
    set_templates(instance)                 # choose template files
    set_layout_classes(instance)            # apply CSS classes

    instance.lists = [
        {
        "items": instance.vacancies,
        "other_items": instance.other_vacancies,
        "index_file": "arkestra/universal_date_index.html",
        "index": instance.vacanciesindex,
        "index_items": instance.vacancies_index_items,
        "div_class": instance.vacancies_div_class,
        "heading_text": instance.vacancies_heading_text,
        "show_when": instance.show_vacancies_when,
        "item_file": "arkestra/universal_plugin_list_item.html",
        },
        {
        "items": instance.studentships,
        "other_items": instance.other_studentships,
        "index_file": "arkestra/universal_date_index.html",
        "index": instance.studentshipsindex,
        "index_items": instance.studentships_index_items,
        "div_class": instance.studentships_div_class,
        "heading_text": instance.studentships_heading_text,
        "show_when": instance.show_studentships_when,
        "item_file": "arkestra/universal_plugin_list_item.html",
        },
    ]
    return instance

def set_defaults(instance):
    # set defaults
    instance.vacancies, instance.studentships = None, None
    instance.current_vacancies, instance.current_studentships = [], []
    instance.archived_vacancies, instance.archived_studentships = [], []
    instance.other_vacancies, instance.other_studentships = [], []
    instance.current_vacancies, instance.current_studentships = [], []        # actual forthcoming studentships
    instance.show_vacancies_when = instance.show_studentships_when = True # show date groupers?
    instance.vacanciesindex = instance.studentshipsindex = False # show an index?
    instance.vacancies_index_items, instance.studentships_index_items = [], []
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
    if instance.type == "plugin"or instance.type == "sub_page":
        if (instance.vacancies or instance.studentships) and instance.entity.auto_vacancies_page:
            instance.link_to_main_page = instance.entity.get_related_info_page_url("vacancies-and-studentships")
            instance.main_page_name = instance.entity.vacancies_page_menu_title
            
    # not a plugin, but showing current studentships items on main page
    if instance.type == "main_page" or instance.type == "sub_page" or instance.type == "menu":
        if instance.view == "current":

            # studentships
            if instance.archived_studentships or instance.current_studentships:
                if instance.limit_to and len(instance.studentships) > instance.limit_to:
                    if instance.current_studentships.count() > instance.limit_to:
                        instance.other_studentships.append({
                            "link":instance.entity.get_related_info_page_url("all-current-studentships"), 
                            "title":"all forthcoming studentships", 
                            "count": instance.current_studentships.count(),}
                            )
            if instance.archived_studentships:
                instance.other_studentships.append({
                    "link":instance.entity.get_related_info_page_url("studentship-archive"), 
                    "title":"archived studentships",
                    "count": instance.archived_studentships.count(),}
                    )    

            # vacancies
            if instance.archived_vacancies or instance.current_vacancies:
                if instance.limit_to and len(instance.vacancies) > instance.limit_to:
                    if instance.current_vacancies.count() > instance.limit_to:
                        instance.other_vacancies.append({
                            "link":instance.entity.get_related_info_page_url("all-current-vacancies"), 
                            "title":"all forthcoming vacancies", 
                            "count": instance.current_vacancies.count(),}
                            )
            if instance.archived_vacancies:
                instance.other_vacancies.append({
                    "link":instance.entity.get_related_info_page_url("vacancy-archive"), 
                    "title":"archived vacancies",
                    "count": instance.archived_vacancies.count(),}
                    )    

        # an archive
        elif instance.view == "archive":

            if instance.current_vacancies:
                instance.other_vacancies = [{
                    "link":instance.entity.get_related_info_page_url("all-current-vacancies"), 
                    "title":"all current vacancies", 
                    "count": instance.current_vacancies.count(),}]                

            if instance.current_studentships:
                instance.other_studentships = [{
                    "link":instance.entity.get_related_info_page_url("all-current-studentships"), 
                    "title":"all current studentships", 
                    "count": instance.current_studentships.count(),}]                
    
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
        if (instance.vacancies or instance.other_vacancies) and (instance.studentships or instance.other_studentships):
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
                    
def get_studentships(instance):
    """
    returns current_studentships, archived_studentships, series_studentships
    """
    print "____ get_studentships() ____"
    if instance.type == "for_person":
        all_studentships = instance.person.studentship_featuring.all()
    elif instance.type == "for_place":
        all_studentships = instance.place.studentship_set.all()
    # most likely, we're getting studentships related to an entity
    elif MULTIPLE_ENTITY_MODE and instance.entity:
        all_studentships = Studentship.objects.filter( \
        Q(hosted_by__in=instance.entity.get_descendants(include_self = True)) | \
        Q(publish_to=instance.entity)).distinct().order_by('closing_date')
    else:
        all_studentships = Studentship.objects.all()

        # if an entity should automatically publish its descendants' items
        #     all_studentships = Event.objects.filter(Q(hosted_by__in=instance.entity.get_descendants(include_self=True)) | Q(publish_to=instance.entity)).distinct().order_by('start_date')
    print "All studentships", instance.type, all_studentships.count()
            
    instance.current_studentships = all_studentships.filter(closing_date__gte = datetime.now())
    instance.archived_studentships = all_studentships.exclude(closing_date__gte = datetime.now())
        
    print "Previous studentships", instance.archived_studentships.count()
        
    return 
    
def get_vacancies(instance):
    """
    """
    print "____ get_vacancies() ____"
    if instance.type == "for_person":
        all_vacancies = instance.person.vacancy_featuring.all()
    # most likely, we're getting vacancies related to an entity
    elif MULTIPLE_ENTITY_MODE and instance.entity:
        all_vacancies = Vacancy.objects.filter( \
        Q(hosted_by__in=instance.entity.get_descendants(include_self = True)) | \
        Q(publish_to=instance.entity)).distinct().order_by('closing_date')
    else:
        all_vacancies = Vacancy.objects.all()

        # if an entity should automatically publish its descendants' items
        #     all_vacancies = Event.objects.filter(Q(hosted_by__in=instance.entity.get_descendants(include_self=True)) | Q(publish_to=instance.entity)).distinct().order_by('start_date')
    print "All vacancies", all_vacancies.count()
            
    instance.current_vacancies = all_vacancies.filter(closing_date__gte = datetime.now())
    instance.archived_vacancies = all_vacancies.exclude(closing_date__gte = datetime.now())
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