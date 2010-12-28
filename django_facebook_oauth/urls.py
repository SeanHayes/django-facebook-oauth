from django.conf.urls.defaults import *

urlpatterns = patterns('fb', 
	url(r'^.*', 'views.fb_auth', name='fb_auth'),
)
