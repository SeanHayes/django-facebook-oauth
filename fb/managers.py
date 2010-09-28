from django.db import models

class FacebookUserManager(models.Manager):
	"""Custom manager for a Facebook User."""
	
	def get_by_natural_key(self, uid):
		return self.get(uid=uid)

