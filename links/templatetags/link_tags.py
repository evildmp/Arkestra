from django import template
from django.contrib.contenttypes.models import ContentType

import re

from links.models import ObjectLink

register = template.Library()

"""
@register.inclusion_tag('links/cms_plugins/links.html', takes_context = True)
def links(context):
    # print "in links"
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
    """
    Place {% get_links as links %} in your template.
    As long as your item is available in the template as {{ content_object }}, you'll 
    have access to any links placed on it.
    
    An as a template:
    
	{% if links %}
    	{% regroup links by wrapped_destination_obj.heading as link_types %}
    	{% for kind in link_types %}
    		<h{{ IN_BODY_HEADING_LEVEL }}>{{kind.grouper}}</h{{ IN_BODY_HEADING_LEVEL }}>
            <ul class= "none">
               	{% for link in kind.list %}
               		<li>
               			<a href = "{{ link.url }}">{% if link.text %}{{ link.text }}
               				{% else %}{{ link.destination_content_object }}
               				{% endif %}
               			</a>{% if link.include_description and link.description %}<br />{{ link.description }}{% endif %}
               		</li>
               	{% endfor %}
           </ul>
    	{% endfor %}
    {% endif %}

    should do the trick.
    
    However, it's just as simple to pass links to the context in the view.
    
    The only reason for doing it this way is to get links into the context of from a 
    view we can't easily set up ourselves, for example that of another application.
    
    There doesn't seem to be much point in using for views that we can easily edit.
    """
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

