# Copyright 2017 Google Inc. All Rights Reserved.
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

from mock import patch
import os
import pytest

# The environment settings in this section were extracted from the
# google.appengine.ext.testbed library, as extracted from version
# 1.9.61 of the SDK.

# from google.appengine.ext.testbed
DEFAULT_ENVIRONMENT = {
    'APPENGINE_RUNTIME': 'python27',
    'APPLICATION_ID': 'testbed-test',
    'AUTH_DOMAIN': 'gmail.com',
    'HTTP_HOST': 'testbed.example.com',
    'CURRENT_MODULE_ID': 'default',
    'CURRENT_VERSION_ID': 'testbed-version',
    'REQUEST_ID_HASH': 'testbed-request-id-hash',
    'REQUEST_LOG_ID': '7357B3D7091D',
    'SERVER_NAME': 'testbed.example.com',
    'SERVER_SOFTWARE': 'Development/1.0 (testbed)',
    'SERVER_PORT': '80',
    'USER_EMAIL': '',
    'USER_ID': '',
}

# endpoints updated value
DEFAULT_ENVIRONMENT['CURRENT_VERSION_ID'] = '1.0'


def environ_patcher(**kwargs):
    replaces = dict(DEFAULT_ENVIRONMENT, **kwargs)
    return patch.dict(os.environ, replaces)


@pytest.fixture()
def appengine_environ():
    """Patch os.environ with appengine values."""
    patcher = environ_patcher()
    with patcher:
        yield
