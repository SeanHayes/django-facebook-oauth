from django.contrib.auth.models import User
from django.db import models

class FacebookUser(models.Model):
	user = models.OneToOneField(User, related_name='facebook')
	name = models.CharField(max_length=100)
	uid = models.CharField(max_length=20, unique=True)
	access_token = models.CharField(max_length=500, blank=True, null=True)
	url = models.URLField(blank=True, null=True)
	img_url = models.URLField(blank=True, null=True)
	#gender = models.CharField(max_length=1,choices=(('M','Male'),('F',Female),default=Null,blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return u'%s\'s Facebook Profile' % (self.name)
	
	def natural_key(self):
		return (self.uid)
