from cms.models import Page, CMSPlugin
from contacts_and_people.models import Person, Entity, Membership, Building
from news_and_events.models import NewsArticle, Event
from django.contrib.auth.models import User, Group
import django.http as http
from django.db.models import get_model
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings
from arkestra_utilities.models import ArkestraUser

@login_required
def stats(request):
    pages = Page.objects.count()
    people = Person.objects.count()
    entities = Entity.objects.count()
    roles = Membership.objects.count() 
    newsarticles = NewsArticle.objects.count() 
    events = Event.objects.count() 
    users = ArkestraUser.objects.filter(is_active = True, is_staff = True) 
    groups = Group.objects.all().order_by("name")
    plugins = CMSPlugin.objects.count() 
    return shortcuts.render_to_response(
        "housekeeping/statistics.html", {
            "pages": pages,
            "people": people,
            "roles": roles,
            "entities": entities,
            "newsarticles": newsarticles,
            "events": events,
            "users": users,
            "plugins": plugins,
            "groups": groups,
            "base_template": get_fallback_template(),
            },
        RequestContext(request),
        )
        
@login_required
def userstats(request,slug):
    print "userstats", slug
    user = User.objects.get(username=slug)
    #print user
    return shortcuts.render_to_response(
        "housekeeping/user_statistics.html", {
            "user": user,
            }
        )        