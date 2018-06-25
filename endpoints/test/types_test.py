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

"""Tests for types."""

import base64
import json
import os
import string
import time
import unittest

import test_util
from endpoints import api_config
from endpoints import message_types
from endpoints import messages
from endpoints import remote
from endpoints import types as endpoints_types


class ModuleInterfaceTest(test_util.ModuleInterfaceTest,
                          unittest.TestCase):

  MODULE = endpoints_types

class TestOAuth2Scope(unittest.TestCase):
  def testScope(self):
    sample = endpoints_types.OAuth2Scope(scope='foo', description='bar')
    converted = endpoints_types.OAuth2Scope(scope='foo', description='foo')
    self.assertEqual(sample.scope, 'foo')
    self.assertEqual(sample.description, 'bar')

    self.assertEqual(endpoints_types.OAuth2Scope.convert_scope(sample), sample)
    self.assertEqual(endpoints_types.OAuth2Scope.convert_scope('foo'), converted)

    self.assertIsNone(endpoints_types.OAuth2Scope.convert_list(None))
    self.assertEqual(endpoints_types.OAuth2Scope.convert_list([sample, 'foo']), [sample, converted])
