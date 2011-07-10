from django import template
from django.template.defaultfilters import safe

from arkestra_utilities.models import Insert

from classytags.arguments import Argument
from classytags.core import Tag, Options

register = template.Library()

class RenderInserter(Tag):
    name = 'insert'
    options = Options(
        Argument('insertion_point'),
        Argument('width', default=None, required=False),
    )

    def render_tag(self, context, insertion_point, width):
        inserter, created = Insert.objects.get_or_create(insertion_point = insertion_point)
        request = context.get('request', None)
        if not request:
            return ''
        if not inserter.content:
            return ''
        return safe(inserter.content.render(context, width))
register.tag(RenderInserter)
