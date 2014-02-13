from django.test.client import Client
from django.contrib.sites.models import Site

print Site.objects.all()

client = Client()
