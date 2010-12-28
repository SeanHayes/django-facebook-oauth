#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

version = '0.1.0'

setup(name='django-facebook-oauth',
	version=version,
	description="Django auth backend for Facebook.",
	author='Seán Hayes',
	author_email='sean@seanhayes.name',
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Framework :: Django",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: BSD License",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.6",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Software Development :: Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules"
	],
	keywords='django facebook oauth',
	url='https://github.com/vikalp/django-facebook-oauth',
	license='BSD',
	packages=['django_facebook_oauth'],
	install_requires=['django', 'facebook'],
)

