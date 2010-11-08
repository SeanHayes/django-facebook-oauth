# Create your views here.
from datetime import datetime
import hashlib,pdb
import urllib
import time
import urllib2
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect,HttpResponse
from django.conf import settings
import facebook


def fb_auth(request):
	v_code = request.GET.get('code')
	APP_ID = settings.FACEBOOK_APP_ID
	FB_P=settings.FB_PERM

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
		if request.META.has_key('HTTP_REFERER'):
			url = request.META['HTTP_REFERER']
			resp=HttpResponseRedirect(urllib2.unquote(url))

		else:
			resp=HttpResponseRedirect("http://goibibo.ibibo.com")
		if(FB_P.count('offline_access')):
			resp=set_cookie(resp, "fbs_"+APP_ID, str(user.username),access_token=access_token,expires=time.time() + 30 * 86400)
		else:
			resp=set_cookie(resp, "fbs_"+APP_ID, str(user.username),access_token=access_token,expires=time.time() + 3600)
		return resp
	else:
		ur = 'http://' + request.get_host() + request.get_full_path()
		perm=",".join(FB_P)
		args = dict(client_id=APP_ID, redirect_uri=ur, scope=perm)
		return HttpResponseRedirect("https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args))


def set_cookie(resp, name, value, access_token=None, domain=None, path="/", expires=None):
	"""Generates and signs a cookie for the give name/value"""
	expires = str(int(time.time())+21600000)
	args = {}
	args['expires'] = expires
	args['uid'] = value
	if(access_token):	
		args['access_token'] = access_token
		graph = facebook.GraphAPI(access_token)
                graph=graph.get_object('me')
		fname = graph['first_name']
		args['fname']=fname

	signature = cookie_signature(args)
	args['sig'] = signature
	#resp.set_cookie(name,urllib.urlencode(args),path="/",domain="goibibo.ibibo.com",expires=str(int(time.time())+21600000))
	max_age = 365*24*60*60
        resp.set_cookie(name,urllib.urlencode(args), max_age=max_age, expires=None, path='/', domain="goibibo.ibibo.com", secure=None)
	return resp

def cookie_signature(parts):
	"""Generates a cookie signature.

	We use the Facebook app secret since it is different for every app (so
	people using this example don't accidentally all use the same secret).
	"""
	payload = ''
	for part in sorted(parts.keys()):
		payload += part+"="+parts[part]
	payload += settings.FACEBOOK_SECRET_KEY
	return hashlib.md5(payload).hexdigest()	
