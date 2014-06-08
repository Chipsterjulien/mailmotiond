#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It create a LaTeX Rapport.
Copyright (C) 2014 Julien Freyermuth
All Rights Reserved

See the file LICENSE for copying permission.
"""


#------
# Used http://www.python.org/dev/peps/pep-0314/ and
# http://getpython3.com/diveintopython3/packaging.html
#
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
#
# to wrote this script
#------------------------


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.4',
]

DATA_FILES = [('/etc/mailmotiond', ['cfg/mailmotiond.conf']),
              ('/usr/lib/systemd/system', ['cfg/mailmotiond.service'])]

SCRIPTS = ['mailmotiond', ]

setup(
    name             = 'mailmotiond',
    version          = '0.1',
    description      = 'Send pictures',
    long_description = 'Send mail when motion save a picture',
    author           = 'Freyermuth Julien',
    author_email     = 'julien.chipster@gmail.com',
    license          = 'WTFPL',
    platforms        = 'Linux',
    url              = 'github/mailmotiond',
    data_files       = DATA_FILES,
    packages         = find_packages(),
    include_package_data = True,
    scripts          = SCRIPTS,
    requires         = ['python (>=3.4)'],
    classifiers      = CLASSIFIERS,
)
