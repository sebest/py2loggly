#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from py2loggly import __version__, __email__, __author__

from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()

setup(
    name='py2loggly',
    version=__version__,
    description='A proxy for python UDP/TCP logging to loggly',
    long_description=readme,
    author=__author__,
    author_email=__email__,
    url='https://github.com/sebest/py2loggly',
    packages=[
        'py2loggly',
    ],
    package_dir={'py2loggly': 'py2loggly'},
    include_package_data=True,
    install_requires=[
        'gevent',
    ],
    license="MIT",
    zip_safe=False,
    keywords=['loggly', 'logging'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    entry_points = {
        'console_scripts': [
            'py2loggly = py2loggly.cli:main',
        ]
    }
)
