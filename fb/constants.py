from django.contrib.sites.models import Site
from django.conf import settings

HOST = Site.objects.get_current().domain

if HOST is 'example.com' and hasattr(settings, 'HOST'):
	HOST = settings.HOST
