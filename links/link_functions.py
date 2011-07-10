from django.contrib.contenttypes.models import ContentType
from links.models import ObjectLink

def object_links(content_object):
    model = ContentType.objects.get_for_model(content_object)
    links = ObjectLink.objects.filter(content_type__pk=model.id, object_id = content_object.id).order_by('destination_content_type')
    links = [link for link in links if link.wrapped_destination_obj.obj]
    
    def mykey(obj): # would a lambda be nicer here?
        return obj.wrapped_destination_obj.heading()
    
    links.sort(key=mykey)
    #links.sort(key=operator.attrgetter('wrapped_destination_obj.heading()'))
    return links