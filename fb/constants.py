from django.contrib.sites.models import Site
from django.conf import settings

if hasattr(settings, 'HOST'):
	HOST = settings.HOST
else:
	HOST = Site.objects.get_current().domain
