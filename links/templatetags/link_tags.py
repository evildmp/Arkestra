from django import template
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType

import operator
import re

from links.models import ObjectLink

from django.conf import settings
LINK_SCHEMA = getattr(settings, 'LINK_SCHEMA', {})


register = template.Library()

"""
@register.inclusion_tag('links/cms_plugins/links.html', takes_context = True)
def links(context):
    print "in links"
    #Publishes all the links attached to this object - superseded by the more complex version below
    content_object = context.get('content_object', None)
    if content_object:
        model = ContentType.objects.get_for_model(content_object)
        links = ObjectLink.objects.filter(content_type__pk=model.id, object_id = content_object.id)
        return {'links' : links,        
        }
"""

@register.tag
def get_links(parser, token):
    print "in get_links -----"
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return LinksNode(var_name)

class LinksNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name
    def render(self, context):
        content_object = context.get('content_object', None)
        if content_object:
            model = ContentType.objects.get_for_model(content_object)
            links = ObjectLink.objects.filter(content_type__pk=model.id, object_id = content_object.id).order_by('destination_content_type')
            context[self.var_name] = links
        return ''

