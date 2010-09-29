from datetime import datetime
import facebook
import pdb
import urllib, urllib2

from django.contrib.auth.models import User
from models import FacebookUser

from django.contrib.auth.backends import ModelBackend
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings
APP_ID = settings.FACEBOOK_APP_ID
APP_SECRET = settings.FACEBOOK_SECRET_KEY
import logging
import json

class FbAuth(ModelBackend):
	"""
	Authenticate against the Facebook Authentication
	
	Use the login name, and a hash of the password. For example:
	"""
	
	def authenticate(self, verification_code=None, cookies=[]):
		access_token = None
		fb_profile = None
		if(cookies):
			access_token = facebook.get_user_from_cookie(cookies, APP_ID, APP_SECRET)
			if 'fbs_' + APP_ID in cookies and datetime.fromtimestamp(float(access_token['expires'])) > datetime.now():
				graph = facebook.GraphAPI(access_token['access_token'])
				fb_profile = graph.get_object('me')
			
			id = access_token['uid']
		
		elif verification_code:
			#url = 'http://'+settings.HOST+'/fb/fb-auth/'
			url = 'http://%s%s' % (Site.objects.get_current().domain, reverse('fb_auth'))
			logging.debug(url)
			
			args = dict(client_id=APP_ID, redirect_uri=url)
			args["client_secret"] = APP_SECRET
			args["code"] = verification_code
			logging.debug(args)
			
			url = "https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(args)
			logging.debug('Access Token URL: %s' % url)
			response = urllib2.urlopen(url).read()
			logging.debug('response: %s' % response)
			atoken = response.split('&')[0].split('=')[-1]
			access_token = atoken
			
			graph = facebook.GraphAPI(access_token)
			fb_profile = graph.get_object('me')
			id = fb_profile['id']
			
		
		if(fb_profile):
			#logging.debug('fb_profile: %s' % fb_profile)
			if type(access_token) == dict:
				access_token = access_token['access_token']
			logging.debug('Access Token: %s' % access_token)
			fb_user = self.updateDb(fb_profile, access_token)
			logging.debug('FB User: %s' % fb_user)
			return fb_user.user
		else:
			return None
	
	def updateDb(self, fb_profile, access_token):
		#logging.debug(fb_profile)
		#logging.debug('Access Token: %s' % access_token)
		#TODO: check for admin:
		is_admin = False
		try:
			url = 'https://api.facebook.com/method/fql.query?format=json&query=SELECT%%20application_id%%20FROM%%20developer%%20WHERE%%20developer_id%%20=%%20%s&access_token=%s' % (fb_profile['id'], access_token)
			
			apps = json.loads(urllib2.urlopen(url).read())
			
			for app in apps:
				if app['application_id'] == APP_ID:
					is_admin = True
					break
		except Exception:
			pass
		logging.debug('Admin status: %s' % is_admin)
		
		try:
			fb_user = FacebookUser.objects.get(uid=fb_profile['id'])
			#should the access_token be updated?
			user = fb_user.user
			user.is_staff = is_admin
			user.is_superuser = is_admin
			user.save()
		except FacebookUser.DoesNotExist as e:
			logging.debug('%s' % e)
			try:
				email = fb_profile['email']
			except:
				email = fb_profile['id'] + '@dummyfbemail.com'
			
			user = User(
				username=fb_profile['id'],
				email=email,
				first_name=fb_profile['first_name'],
				last_name=fb_profile['last_name'])
			user.set_unusable_password()
			user.is_staff = is_admin
			user.is_superuser = is_admin
			user.save()
			
			fb_user = FacebookUser(
				user=user,
				uid=str(fb_profile["id"]),
				name=fb_profile["name"],
				access_token=access_token,
				url=fb_profile["link"])
			fb_user.save()
		
		return fb_user
	
