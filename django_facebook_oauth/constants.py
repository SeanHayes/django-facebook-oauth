from django.contrib.sites.models import Site
from django.conf import settings

_host = None

def _get_host_from_db():
	"Used to get around the fact that the DB isn't set up during testing when this is first called."
	if _host is None:
		_host = Site.objects.get_current().domain
	
	return _host

if hasattr(settings, 'HOST'):
	HOST = settings.HOST
else:
	HOST = property(_get_host_from_db)
