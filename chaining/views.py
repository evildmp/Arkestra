from django.http import HttpResponse
from django.core import serializers
from models import SubCategory

def subcategory(request, category_id):
    print "Doing the view"
    return HttpResponse(serializers.serialize('json', SubCategory.objects.filter(category=category_id), fields=('pk','name')))