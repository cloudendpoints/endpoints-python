#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

install_requires = [
    'attrs==17.4.0',
    'google-endpoints-api-management>=1.10.0',
    'semver==2.7.7',
    'setuptools>=36.2.5',
]

setup(
    name='google-endpoints',
    version='4.7.0',
    description='Google Cloud Endpoints',
    long_description=open('README.rst').read(),
    author='Google Endpoints Authors',
    author_email='googleapis-packages@google.com',
    url='https://github.com/cloudendpoints/endpoints-python',
    packages=find_packages(exclude=['test', 'test.*']),
    package_dir={'google-endpoints': 'endpoints'},
    include_package_data=True,
    license='Apache',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    scripts=['endpoints/endpointscfg.py'],
    tests_require=['mock', 'protobuf', 'protorpc', 'pytest', 'webtest'],
    install_requires=install_requires,
)
