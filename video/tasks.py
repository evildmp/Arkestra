from celery.task import task
from models import VideoVersion


@task
def encodevideo(source, size, codec):
    version, created = VideoVersion.objects.get_or_create(source = source, size = size, codec = codec)
    version.encode()
    return