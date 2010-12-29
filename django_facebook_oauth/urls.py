from django.conf.urls.defaults import *

urlpatterns = patterns('django_facebook_oauth', 
	url(r'^.*', 'views.fb_auth', name='fb_auth'),
)
