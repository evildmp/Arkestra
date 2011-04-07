from django import template
register = template.Library()

from cms.models import Page, CMSPlugin
from contacts_and_people.models import Person, Entity, Membership, Building
from news_and_events.models import NewsArticle, Event
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry


def statistics(parser, token):
    print "in statistics template tag"
    return CurrentStats()
  
class CurrentStats(template.Node):
    def render(self, context):
        print "in render"
        stats={}
        stats["pages"] = Page.objects.count()
        stats["people"] = Person.objects.count()
        stats["entities"] = Entity.objects.count()
        stats["roles"] = Membership.objects.count() 
        stats["newsarticles"] = NewsArticle.objects.count() 
        stats["events"] = Event.objects.count() 
        stats["webeditors"] = User.objects.filter(is_active = True, is_staff = True).count() 
        stats["plugins"]  = CMSPlugin.objects.count()
        context["statistics"] = stats
        return ""
        
register.tag(statistics)

@register.inclusion_tag('last_edit.html',takes_context = True)
def last_edit(context):
    """
    Returns the date of the user's most recent admin action.
    """
    user = context["user"]
    try:
        last_edit = LogEntry.objects.filter(user = user).order_by('-id')[0].action_time
        print last_edit
    except IndexError:
        last_edit = "Never"
    print " -------- statistics.last_edit --------"
    return {'last_edit': last_edit}
