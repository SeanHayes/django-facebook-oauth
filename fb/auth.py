from django.contrib.auth.models import User, check_password

from datetime import datetime
from django.conf import settings
import facebook
import urllib,urllib2

from models import FacebookUser

from settings import FACEBOOK_APP_ID as APP_ID
from settings import FACEBOOK_SECRET_KEY as APP_SECRET


class FbAuth:
	"""
	Authenticate against the Facebook Authentication

	Use the login name, and a hash of the password. For example:
	"""

	def authenticate(self,verification_code=None,cookies=[]):
		access_token = None
		fb_profile = None
		if(cookies):
			access_token = facebook.get_user_from_cookie(cookies, APP_ID, APP_SECRET)
			if 'fbs_' + APP_ID in cookies and datetime.fromtimestamp(float(access_token['expires'])) > datetime.now():
				graph = facebook.GraphAPI(access_token['access_token'])
				fb_profile = graph.get_object('me')

			id = access_token['uid']

		elif verification_code:
			ur = 'http://'+settings.HOST+'/fb/fb-auth/'
			args = dict(client_id=APP_ID, redirect_uri=ur)
			args["client_secret"] = APP_SECRET
			args["code"] = verification_code

			ur = "https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(args)

			response = urllib2.urlopen(ur).read()
			atoken = response.split('&')[0].split('=')[-1]
			access_token = urllib2.unquote(atoken)

			graph = facebook.GraphAPI(access_token)
			fb_profile = graph.get_object('me')
			id = fb_profile['id']
		
		if(fb_profile):	
			fb_user = self.updateDb(fb_profile,access_token)
			return fb_user.user
		else:
			return None

	def updateDb(self,fb_profile,access_token):
			try:
				fb_user = FacebookUser.objects.get(uid=fb_profile['id'])
			except FacebookUser.DoesNotExist:
				try:
					email = fb_profile['email']
				except:
					email = fb_profile['id'] + '@dummyfbemail.com'

				user = User.objects.create(username=fb_profile['id'], email=email)
				user.first_name = fb_profile['first_name']
				user.last_name = fb_profile['last_name']
				user.save()
				
				fb_user = FacebookUser(user=user,uid=str(fb_profile["id"]),
					name=fb_profile["name"],
					access_token=access_token,
					url=fb_profile["link"])
				fb_user.save()

			return fb_user


	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
