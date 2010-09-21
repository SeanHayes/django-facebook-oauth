# Create your views here.
from datetime import datetime
import hashlib,pdb
import urllib
import time

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.conf import settings


def fb_auth(request):
	v_code = request.GET.get('code')
	APP_ID = settings.FACEBOOK_APP_ID

	if 'fbs_' + APP_ID in request.COOKIES:
		user = authenticate(cookies=request.COOKIES)
		if user:
			login(request, user)
		return HttpResponseRedirect("/")
	elif(v_code):
		user = authenticate(verification_code=v_code)
		if user:
			login(request, user)
		access_token = user.facebook.select_related()[0].access_token
		set_cookie(request, "fbs_"+APP_ID, str(user.username),access_token=access_token,expires=time.time() + 30 * 86400)
		return HttpResponseRedirect("/")
	else:
		ur = 'http://' + request.get_host() + request.get_full_path()
		args = dict(client_id=APP_ID, redirect_uri=ur)
		return HttpResponseRedirect("https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args))


def set_cookie(request, name, value, access_token=None, domain=None, path="/", expires=None):
	"""Generates and signs a cookie for the give name/value"""
	expires = str(int(time.time()))
	args = {}
	args['expires'] = expires
	args['uid'] = value
	if(access_token):	
		args['access_token'] = access_token
	signature = cookie_signature(args)
	args['sig'] = signature
	request.COOKIES[name] = urllib.urlencode(args)

def cookie_signature(parts):
	"""Generates a cookie signature.

	We use the Facebook app secret since it is different for every app (so
	people using this example don't accidentally all use the same secret).
	"""
	payload = ''
	for part in sorted(parts.keys()):
		payload += parts[part]
	payload += settings.FACEBOOK_SECRET_KEY
	return hashlib.md5(payload).hexdigest()	
