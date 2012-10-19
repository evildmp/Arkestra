"""
This module will try to clean up the external links database
"""

from links.models import ExternalLink, ObjectLink, GenericLinkListPluginItem, LinkType, ExternalSite

# from cms.models import Placeholder
# from cms.models.pluginmodel import CMSPlugin
# from cms.plugins.text.models import Text
# 
# from BeautifulSoup import BeautifulSoup
# import re
# 
# import django.http as http
# from django.db.models import get_model
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from django.core.exceptions import ObjectDoesNotExist



def tidy_links(action = "dryrun"):
    if action == "execute":
        execute = True
    else:
        execute = False

    messages = {}
    links, de_duplicated_links = de_duplicate_links(execute) # , messages["Duplicate links"]
    sites_to_delete, unused_sites  = check_sites(execute) #, messages["External sites"] 
    models_dictionary = convert_url_fields(execute) # summary["Fields requiring conversion"] = 
        
    report = {
        "action": execute,
        "links": links,
        "de_duplicated_links": de_duplicated_links,
        "unused_sites": unused_sites,
        "sites_to_delete": sites_to_delete,
        "models_dictionary": models_dictionary,
        "template": "housekeeping/tidy_links.html"
        }        

    return report
    

def de_duplicate_links(execute):
    # a message to summarise state
    summary = "Everything seems in order, no action required"
        
    # find out what link.kinds are permissible
    permissible_kinds = LinkType.objects.all()
    
    # get the content_type of ExternalLinks
    content_type = ContentType.objects.get_for_model(ExternalLink)
    
    # get a set of ObjectLinks and GenericLinkListPluginItems that are ExternalLinks
    object_links = ObjectLink.objects.filter(destination_content_type = content_type)
    plugin_links = GenericLinkListPluginItem.objects.filter(destination_content_type = content_type)
    
    # create a set of ExternalLinks
    links = ExternalLink.objects.all().order_by('url')
    
    # we need this the first time around the loop - next time, good-link will be a real one
    
    de_duplicated_links = []
    good_link = None
    
    # loop over our set of links
    for link in links:
        
        # to help find duplicates, remove the trailing slash if there is one
        if link.url:
            # we don't actually want to touch link.url, so we create a temporary variable
            url = link.url
            if url[-1] == "/":
                url = url[0:-1]
                
            # keep some infomrmation about where the duplicates were used
            link.objects = []
            link.plugins = []

            # do we already have a good_link to compare with?
            if good_link:
                # is it a duplicate
                print good_link.url.lower(), url.lower()
                if (good_link.url.lower() == url.lower()) or  (good_link.url.lower()[0:-1] == url.lower()):
                    print "duplicate", url
                    # add this to the list of duplicates for the good_link
                    good_link.duplicates.append(link)
                                                
                    # for each one, change it so it uses the good_link instead
                    for object_link in object_links.filter(destination_object_id = link.id):
                        object_link.destination_object_id = good_link.id
                    
                        if execute:
                            object_link.save()
                        link.objects.append(object_link)
                
                    # for each one, change it so it uses the good_link instead
                    for plugin_link in plugin_links.filter(destination_object_id = link.id):
                        plugin_link.destination_object_id = good_link.id

                        if execute:
                            plugin_link.save()
                        link.plugins.append(plugin_link)

                    # delete the duplicate
                    if execute:
                        print "    deleting", link
                        link.delete()

                    de_duplicated_links.append(good_link)
                # this link wasn't a duplicate
                else:
                    if execute:
                        # force a save, to trigger the code in save()
                        link.save()
                    good_link = link
                    # each good link starts off with no duplicates
                    good_link.duplicates = []
            else:
                # the first time we find a good link, assign it
                print "assigning link"
                good_link = link

        else:
            # delete this link because it's blank
            link.blank = True
            if execute:
                link.delete()
        
        # check that every link is of a permissible type
        if not link.kind in permissible_kinds:
            link.kind_warning = True

    de_duplicated_links = set(de_duplicated_links)
    
    duplicates = len(de_duplicated_links)

    return links, de_duplicated_links
            
def check_sites(execute):
    # deletes sites without children or links
    sites_to_delete = ExternalSite.objects.filter(children=None, links=None)
    for site in sites_to_delete:
        if execute:
            site.delete()      
    unused_sites = ExternalSite.objects.filter(children=None, links=None)
    return sites_to_delete, unused_sites
 
def convert_url_fields(execute):
    # gets hold of URL fields and turns them into FK fields to links in the database
    models_dictionary = {
        "messages": {},                             # a general set of messages for the user
        "modules":  {
            "news_and_events.models": {             # each module containing the models must be represented, like this
                "application": "News & Events",     # this is the human-friendly name of the module
                "models": {                         # a dictionary with each model in that module
                    "NewsArticle": {                # the actual name of the class
                        "fields": [                 # a list of the fields we're working on
                            {                       # a dictionary for each field
                                "url_field": "url",
                                "title_field": "title",
                                "description_field": "summary", # unlike the others this is optional
                                "new_field": "external_url",                
                                },
                            ],
                        "model": "News articles",   # the human-friendly name of the model
                        "actions": {},              # an empty dictionary where we we store the results
                        },
                    "Event": {                      # a second model in that module
                        "fields": [                 
                            {                       
                                "url_field": "url",
                                "title_field": "title",
                                "description_field": "summary",
                                "new_field": "external_url",                
                                },
                            ],
                        "model": "Events",
                        "actions": {},
                        },
                    },
                },
            "contacts_and_people.models": {             # each module containing the models must be represented, like this
                "application": "Contacts & People",     # this is the human-friendly name of the module
                "models": {                         # a dictionary with each model in that module
                    "Entity": {                # the actual name of the class
                        "fields": [                 # a list of the fields we're working on
                            {                       # a dictionary for each field
                                "url_field": "url",
                                "title_field": "name",
                                "new_field": "external_url",                
                                },
                            ],
                        "model": "Entity",   # the human-friendly name of the model
                        "actions": {},              # an empty dictionary where we we store the results
                        },
                    "Person": {                      # a second model in that module
                        "fields": [                 
                            {                       
                                "url_field": "url",
                                "title_field": "__unicode__",
                                "new_field": "external_url",                
                                },
                            ],
                        "model": "Person",
                        "actions": {},
                        },
                    },
                },
            "vacancies_and_studentships.models": {             # each module containing the models must be represented, like this
                "application": "Vacancies and Studentships",     # this is the human-friendly name of the module
                "models": {                         # a dictionary with each model in that module
                    "Vacancy": {                # the actual name of the class
                        "fields": [                 # a list of the fields we're working on
                            {                       # a dictionary for each field
                                "url_field": "url",
                                "title_field": "title",
                                "description_field": "summary",
                                "new_field": "external_url",                
                                },
                            ],
                        "model": "Vacancy",   # the human-friendly name of the model
                        "actions": {},              # an empty dictionary where we we store the results
                        },
                    "Studentship": {                      # a second model in that module
                        "fields": [                 
                            {                       
                                "url_field": "url",
                                "title_field": "title",
                                "description_field": "summary",
                                "new_field": "external_url",                
                                },
                            ],
                        "model": "Studentship",
                        "actions": {},
                        },
                    },
                },
            },
        }
       
    # loop over the modules
    for module, module_values in models_dictionary["modules"].items():
        # models_dictionary["modules"][module]={}
        
        # loop over the models in the module
        for model, model_values in module_values["models"].items():
            
            # mmodel is the human-readable name of the model, used for the report summary
            mmodel = models_dictionary["modules"][module]["models"][model]["model"]
            # create a messages list for this model
            messages = []

            # import the model
            actual_model = getattr(__import__(module, globals(), locals(), module_values["models"], -1), model)
                                            
            # loop over the fields that need converting
            for field in model_values["fields"]:
                print field
                
                url_field = field["url_field"]
                title_field = field["title_field"]
                description_field = field.get("description_field", None)
                new_field = field["new_field"]

                # create a summary report for this field
                # models_dictionary["messages"][mmodel][url_field]={}

                try:
                    getattr(actual_model, new_field)
                except AttributeError:
                    message = "field " + new_field + " is missing - check the model and try agin"
                    messages.append(message)


            if not messages:
                message = "Checked " + str(actual_model.objects.count()) + " items"
                items_to_convert =[]
                messages.append(message)
                
                
                # loop over each item in the class
                for item in actual_model.objects.all():

                    url_field_content = getattr(item, url_field)  # the old fields we want to save
                    title_field_content = getattr(item, title_field)  # the old fields we want to save
                    if description_field: # remember this one is optional
                        description_field_content = getattr(item, description_field)  # the old fields we want to save
                    else:
                        description_field_content = ""
                    new_field_content = getattr(item, new_field)  # the old fields we want to save
                    if url_field_content:
                        items_to_convert.append(item)
                        # if the link exists, assign a FK to it, otherwise create it then assign
                        if execute:
                            link, created = ExternalLink.objects.get_or_create(url=url_field_content, defaults={'title': title_field_content, 'description': description_field_content})
                            setattr(item, new_field, link)
                            setattr(item, url_field, "")
                            item.save()
                            if created:
                                message = "Created new link: " + url_field_content
                                messages.append(message)
                        else:
                            matches = ExternalLink.objects.filter(url=url_field_content).count()
                            message = "Need to create new link: " + url_field_content, matches
                            messages.append(message)
                message = "Items requiring conversion: " + str(len(items_to_convert))
                messages.insert(1, message)                    
            models_dictionary["modules"][module]["models"][model]["messages"]=messages
                
                            
    return models_dictionary