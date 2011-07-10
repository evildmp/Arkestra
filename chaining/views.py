from django.http import HttpResponse
from django.core import serializers
from models import SubCategory

def subcategory(request, category_id):
    queryset = SubCategory.objects.filter(category=category_id)
    content = serializers.serialize('json', queryset, fields=('pk','name'))
    return HttpResponse(content, content_type='application/json')
