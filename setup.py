#!/usr/bin/env python

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Prevent "TypeError: 'NoneType' object is not callable" when running tests.
# (http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'

setup(
    name='django-composite-field',
    version='0.5',
    description='CompositeField implementation for Django',
    long_description=read('README'),
    author='Michael P. Jung',
    author_email='michael.jung@terreon.de',
    license='BSD',
    keywords='django composite field',
    url='http://bitbucket.org/bikeshedder/django-composite-field',
    packages=['composite_field'],
    test_suite='composite_field.tests',
    tests_require=['Django'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
