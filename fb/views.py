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
import logging
import urlparse
from django.contrib.sites.models import Site

def fb_auth(request):
	v_code = request.GET.get('code')
	APP_ID = settings.FACEBOOK_APP_ID
	FB_P=settings.FB_PERM
	
	if 'fbs_' + APP_ID in request.COOKIES:
		#logging.debug('fbs_')
		user = authenticate(cookies=request.COOKIES)
		if user:
			login(request, user)
		return HttpResponseRedirect("/")
	elif(v_code):
		logging.debug('v_code: %s' % v_code)
		user = authenticate(verification_code=v_code)
		if user:
			login(request, user)
		access_token = user.facebook.select_related()[0].access_token
		url = '/'
		#if request.META.has_key('HTTP_REFERER'):
			#logging.debug("Referrer: "+request.META['HTTP_REFERER'])
			#url = urlparse.parse_qs(urlparse.urlparse(request.META['HTTP_REFERER']).query)
			#url = urlparse.parse_qs(urlparse.urlparse(urlparse.parse_qs(urlparse.urlparse(request.META['HTTP_REFERER']).query)['next'][0]).query)['redirect_uri'][0]
		#logging.debug("URL:"+str(url))
		
		resp=HttpResponseRedirect(url)
		#logging.debug('Username: '+user.username)
		
		domain = None
		try:
			try:
				from IPy import IP
				IP(request.get_host().split(':')[0])
			except ImportError:
				pass
		except Exception as e:
			logging.error(e)
			domain = '.'+request.get_host()
			logging.debug('DOMAIN: '+domain)
		resp=set_cookie(resp, "fbs_"+APP_ID, str(user.username), access_token=access_token, domain=domain, expires=time.time() + 30 * 86400)
		return resp
	else:
		#logging.debug('last case')
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
	
	signature = cookie_signature(args)
	args['sig'] = signature
	#logging.debug(args)
	resp.set_cookie(name, urllib.urlencode(args), path="/", domain=domain, expires=expires)
	
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
