#!/usr/bin/env python

import os
from setuptools import Command, setup

# Prevent "TypeError: 'NoneType' object is not callable" when running tests.
# (http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing  # noqa: F401
except ImportError:
    pass


def read(*p):
    '''Utility function to read files relative to the project root'''
    return open(os.path.join(os.path.dirname(__file__), *p)).read()


def get_version():
    '''Get __version__ information from __init__.py without importing it'''
    import re
    VERSION_RE = r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]'
    VERSION_PATTERN = re.compile(VERSION_RE, re.MULTILINE)
    m = VERSION_PATTERN.search(read('composite_field', '__init__.py'))
    if m:
        return m.group(1)
    else:
        raise RuntimeError('Could not get __version__ from composite_field/__init__.py')


class DjangoTestCommand(Command):
    description = "run unit test using Django management command"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Prepare DJANGO_SETTINGS_MODULE and PYTHONPATH
        import os
        import sys
        os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
        sys.path[0:0] = [os.path.dirname(os.path.dirname(__file__))]
        # Execute management command 'test'
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'test'])


setup(
    name='django-composite-field',
    version=get_version(),
    description='CompositeField implementation for Django',
    long_description=read('README.rst'),
    author='Michael P. Jung',
    author_email='michael.jung@terreon.de',
    license='BSD',
    keywords='django composite field',
    url='http://bitbucket.org/bikeshedder/django-composite-field',
    packages=['composite_field'],
    tests_require=['Django'],
    setup_requires=[
        'setuptools_git',
        'wheel',
        'twine',
    ],
    cmdclass={
        'test': DjangoTestCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
