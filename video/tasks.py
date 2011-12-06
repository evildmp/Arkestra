from celery.task import task
from models import VideoVersion


@task
def encodevideo(source, size, codec):
    logger =  encodevideo.get_logger()
    logger.info("**********************")
    print "======== in encodevideo task ========="
    version, created = VideoVersion.objects.get_or_create(source = source, size = size, codec = codec)
    print "== version, created", version, created
    version_status = version.encode()
    print "== version_status", version_status
    return version_status