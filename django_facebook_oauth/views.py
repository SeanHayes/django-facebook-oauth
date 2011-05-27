# Create your views here.
from datetime import datetime
import hashlib,pdb
import urllib
import time
import urllib2
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect,HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from constants import HOST
import logging
import urlparse
import facebook

logger = logging.getLogger(__name__)

cookie_key = 'fbs_' + settings.FACEBOOK_APP_ID
cookie_path = '/'
cookie_domain = settings.SESSION_COOKIE_DOMAIN

def fb_auth(request):
	v_code = request.GET.get('code')
	APP_ID = settings.FACEBOOK_APP_ID
	FB_P=settings.FB_PERM
	next = request.GET['next'] if 'next' in request.GET else settings.FB_AUTH_REDIRECT if hasattr(settings, "FB_AUTH_REDIRECT") else '/'
	
	if cookie_key in request.COOKIES:
		logger.debug('cookie value: %s' % request.COOKIES[cookie_key])
		user = authenticate(cookies=request.COOKIES)
		if user:
			login(request, user)
			return HttpResponseRedirect(next)
		else:
			logger.debug("no user was returned")
	
	if(v_code):
		logger.debug('v_code: %s' % v_code)
		user = authenticate(verification_code=v_code)
		if user:
			login(request, user)
		access_token = user.facebook.select_related()[0].access_token
		
		#if request.META.has_key('HTTP_REFERER'):
		#	url = request.META['HTTP_REFERER']
		#	resp=HttpResponseRedirect(urllib2.unquote(url))
		#else:
		#	resp=HttpResponseRedirect("http://"+settings.SESSION_COOKIE_DOMAIN)
		
		resp=HttpResponseRedirect(next)
		
		if(FB_P.count('offline_access')):
			resp=set_cookie(resp, "fbs_"+APP_ID, user.username, access_token=access_token, expires=time.time() + 30 * 86400)
		else:
			resp=set_cookie(resp, "fbs_"+APP_ID, user.username, access_token=access_token, expires=time.time() + 3600)
		return resp
	else:
		#logger.debug('last case')
		url = 'http://%s%s' % (HOST, reverse('fb_auth'))
		logger.debug(url)
		perm=",".join(FB_P)
		args = dict(client_id=APP_ID, redirect_uri=url, scope=perm)
		resp = HttpResponseRedirect("https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args))
		#it's possible the cookie could be stale
		resp.delete_cookie(cookie_key, cookie_path, cookie_domain)
		return resp

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
	
	for arg in args:
		if type(args[arg]) is unicode:
			args[arg] = args[arg].encode('utf-8')
	signature = cookie_signature(args)
	args['sig'] = signature
	
	#resp.set_cookie(name,urllib.urlencode(args),path="/",domain=cookie_domain,expires=str(int(time.time())+21600000))
	max_age = 365*24*60*60
	resp.set_cookie(name,urllib.urlencode(args), max_age=max_age, expires=None, path=cookie_path, domain=cookie_domain, secure=None)
	return resp

def cookie_signature(parts):
	"""Generates a cookie signature.

	We use the Facebook app secret since it is different for every app (so
	people using this example don't accidentally all use the same secret).
	"""
	payload = []
	for part in sorted(parts.keys()):
		payload.append('%s=%s' % (part, parts[part]))
	payload.append(settings.FACEBOOK_SECRET_KEY)
	payload = ''.join(payload)
	
	return hashlib.md5(payload).hexdigest()

