from django.test import Client,TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from fb.views import *
from fb.models import *
import pdb

class TestFb(TestCase):
	def setUp(self):
		self.client=Client(HTTP_HOST="goibibo.ibibo.com")
		user = User.objects.create_user('avinash', 'avinash@gmail.com', 'goibibo')
		user.is_staff=True
		user.is_superuser=True
		user.save()
		log=self.client.login(username="avinash",password="goibibo")

	def test_fb(self):
		response=self.client.get(reverse(fb_auth))
		self.assertEqual(response.status_code,302)
		print "******************************************"
		print "status code ::::::",response.status_code
		print "testing finished"
		print "url:::",response['Location']

	def test_withcode(self):
		code="8a208ba73c48a1692e1f1f63-1200668821|hGtm0rvweoqvHw6m7ftlCWVE1Bw."
		response=self.client.get(reverse(fb_auth),{'code':code})
		self.assertEqual(response.status_code,302)
		print "******************************************"
		print "status code ::::::",response.status_code
		dbObj=FacebookUser.objects.all()[0]
		#testing accesstoken
		atoken="122023101161980|8a208ba73c48a1692e1f1f63-1200668821|yMJjKKwQwJFG6N6lNBjgdksPjVc."
		self.assertEqual(dbObj.access_token,atoken)
		print "testing access token finished"
		#testing uid
		self.assertEqual(dbObj.uid,"1200668821")
		print "testing uid finished::::::",dbObj.uid
		userObj=User.objects.filter(username="1200668821")[0]
		#testing userid in fb table and auth_user table
		self.assertEqual(dbObj.uid,userObj.username)
		print "testing username finished"


