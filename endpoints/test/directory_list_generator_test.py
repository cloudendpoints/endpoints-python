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

"""Tests for endpoints.directory_list_generator."""

import json
import os
import unittest

import endpoints.api_config as api_config

from protorpc import message_types
from protorpc import messages
from protorpc import remote

import endpoints.api_request as api_request
import endpoints.apiserving as apiserving
import endpoints.directory_list_generator as directory_list_generator

import test_util


_GET_REST_API = 'apisdev.getRest'
_GET_RPC_API = 'apisdev.getRpc'
_LIST_API = 'apisdev.list'
API_CONFIG = {
    'name': 'discovery',
    'version': 'v1',
    'methods': {
        'discovery.apis.getRest': {
            'path': 'apis/{api}/{version}/rest',
            'httpMethod': 'GET',
            'rosyMethod': _GET_REST_API,
        },
        'discovery.apis.getRpc': {
            'path': 'apis/{api}/{version}/rpc',
            'httpMethod': 'GET',
            'rosyMethod': _GET_RPC_API,
        },
        'discovery.apis.list': {
            'path': 'apis',
            'httpMethod': 'GET',
            'rosyMethod': _LIST_API,
        },
    }
}


class BaseDirectoryListGeneratorTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.maxDiff = None

  def _def_path(self, path):
    return '#/definitions/' + path


class DirectoryListGeneratorTest(BaseDirectoryListGeneratorTest):

  def testBasic(self):

    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    description='This is an API')
    class RootService(remote.Service):
      """Describes RootService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='foo', http_method='GET', name='foo')
      def foo(self, unused_request):
        """Blank endpoint."""
        return message_types.VoidMessage()

    @api_config.api(name='myapi', hostname='example.appspot.com', version='v1',
                    description='This is my API')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='foo', http_method='GET', name='foo')
      def foo(self, unused_request):
        """Blank endpoint."""
        return message_types.VoidMessage()

    api_server = apiserving.api_server([RootService, MyService])
    api_config_response = api_server.get_api_configs()
    if api_config_response:
      api_server.config_manager.process_api_config_response(api_config_response)
    else:
      raise Exception('Could not process API config response')

    configs = []
    for config in api_server.config_manager.configs.itervalues():
      if config != API_CONFIG:
        configs.append(config)

    environ = test_util.create_fake_environ(
        'https', 'example.appspot.com', path='/_ah/api/discovery/v1/apis')
    request = api_request.ApiRequest(environ, base_paths=['/_ah/api'])
    generator = directory_list_generator.DirectoryListGenerator(request)

    directory = json.loads(generator.pretty_print_config_to_json(configs))

    try:
      pwd = os.path.dirname(os.path.realpath(__file__))
      test_file = os.path.join(pwd, 'testdata', 'directory_list', 'basic.json')
      with open(test_file) as f:
        expected_directory = json.loads(f.read())
    except IOError as e:
      print 'Could not find expected output file ' + test_file
      raise e

    test_util.AssertDictEqual(expected_directory, directory, self)


class DevServerDirectoryListGeneratorTest(BaseDirectoryListGeneratorTest,
                                          test_util.DevServerTest):

  def setUp(self):
    super(DevServerDirectoryListGeneratorTest, self).setUp()
    self.env_key, self.orig_env_value = (test_util.DevServerTest.
                                         setUpDevServerEnv())
    self.addCleanup(test_util.DevServerTest.restoreEnv,
                    self.env_key, self.orig_env_value)

  def testLocalhost(self):

    @api_config.api(name='root', hostname='localhost:8080', version='v1',
                    description='This is an API')
    class RootService(remote.Service):
      """Describes RootService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='foo', http_method='GET', name='foo')
      def foo(self, unused_request):
        """Blank endpoint."""
        return message_types.VoidMessage()

    @api_config.api(name='myapi', hostname='localhost:8081', version='v1',
                    description='This is my API')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='foo', http_method='GET', name='foo')
      def foo(self, unused_request):
        """Blank endpoint."""
        return message_types.VoidMessage()

    api_server = apiserving.api_server([RootService, MyService])
    api_config_response = api_server.get_api_configs()
    if api_config_response:
      api_server.config_manager.process_api_config_response(api_config_response)
    else:
      raise Exception('Could not process API config response')

    configs = []
    for config in api_server.config_manager.configs.itervalues():
      if config != API_CONFIG:
        configs.append(config)

    environ = test_util.create_fake_environ(
        'http', 'localhost', path='/_ah/api/discovery/v1/apis')
    request = api_request.ApiRequest(environ, base_paths=['/_ah/api'])
    generator = directory_list_generator.DirectoryListGenerator(request)

    directory = json.loads(generator.pretty_print_config_to_json(configs))

    try:
      pwd = os.path.dirname(os.path.realpath(__file__))
      test_file = os.path.join(pwd, 'testdata', 'directory_list',
                               'localhost.json')
      with open(test_file) as f:
        expected_directory = json.loads(f.read())
    except IOError as e:
      print 'Could not find expected output file ' + test_file
      raise e

    test_util.AssertDictEqual(expected_directory, directory, self)


if __name__ == '__main__':
  unittest.main()
