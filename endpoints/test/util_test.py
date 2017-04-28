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

"""Tests for endpoints.util."""

import os
import sys
import unittest

import mock

import endpoints._endpointscfg_setup  # pylint: disable=unused-import

import endpoints.util as util

MODULES_MODULE = 'google.appengine.api.modules.modules'


class GetProtocolForEnvTest(unittest.TestCase):

  def testGetHostnamePrefixAllDefault(self):
    with mock.patch('{0}.get_current_version_name'.format(MODULES_MODULE),
                    return_value='v1'):
      with mock.patch('{0}.get_default_version'.format(MODULES_MODULE),
                      return_value='v1'):
         with mock.patch('{0}.get_current_module_name'.format(MODULES_MODULE),
                         return_value='default'):
          result = util.get_hostname_prefix()
          self.assertEqual('', result)

  def testGetHostnamePrefixSpecificVersion(self):
    with mock.patch('{0}.get_current_version_name'.format(MODULES_MODULE),
                    return_value='dev'):
      with mock.patch('{0}.get_default_version'.format(MODULES_MODULE),
                      return_value='v1'):
         with mock.patch('{0}.get_current_module_name'.format(MODULES_MODULE),
                         return_value='default'):
          result = util.get_hostname_prefix()
          self.assertEqual('dev-dot-', result)

  def testGetHostnamePrefixSpecificModule(self):
    with mock.patch('{0}.get_current_version_name'.format(MODULES_MODULE),
                    return_value='v1'):
      with mock.patch('{0}.get_default_version'.format(MODULES_MODULE),
                      return_value='v1'):
         with mock.patch('{0}.get_current_module_name'.format(MODULES_MODULE),
                         return_value='devmodule'):
          result = util.get_hostname_prefix()
          self.assertEqual('devmodule-dot-', result)

  def testGetHostnamePrefixSpecificVersionAndModule(self):
    with mock.patch('{0}.get_current_version_name'.format(MODULES_MODULE),
                    return_value='devversion'):
      with mock.patch('{0}.get_default_version'.format(MODULES_MODULE),
                      return_value='v1'):
         with mock.patch('{0}.get_current_module_name'.format(MODULES_MODULE),
                         return_value='devmodule'):
          result = util.get_hostname_prefix()
          self.assertEqual('devversion-dot-devmodule-dot-', result)


if __name__ == '__main__':
  unittest.main()

