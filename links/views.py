from django.utils.cache import add_never_cache_headers
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.views.generic.detail import BaseDetailView
from django.contrib.contenttypes.models import ContentType
from schema_registry import schema


class ChainedSelectChoices(BaseDetailView):
    """
    View to handel the ajax request for the field options.
    """

    def get(self, request, *args, **kwargs):

        parent_value = request.GET.get("parent_value")

        wrapper = schema.wrappers[
            ContentType.objects.get(id=parent_value).model_class()
            ]

        default_choices = (
            ("title", u"Title only"),
            ("details", u"Title & summary"),
            ("details image", u"Title, summary & image"),
            )

        choices = getattr(
            wrapper,
            "link_format_choices",
            default_choices
            )

        response = HttpResponse(
            json.dumps(choices, cls=DjangoJSONEncoder),
            mimetype='application/javascript'
        )
        add_never_cache_headers(response)
        return response
