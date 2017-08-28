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

"""Tests for discovery_service."""

import os
import unittest

import endpoints.api_config as api_config
import endpoints.api_config_manager as api_config_manager
import endpoints.apiserving as apiserving
import endpoints.discovery_service as discovery_service
import test_util

import webtest

from protorpc import message_types
from protorpc import messages
from protorpc import remote


@api_config.api('aservice', 'v3', hostname='aservice.appspot.com',
                description='A Service API')
class AService(remote.Service):

  @api_config.method(path='noop')
  def Noop(self, unused_request):
    return message_types.VoidMessage()


class DiscoveryServiceTest(unittest.TestCase):

  class FakeRequest(object):

    def __init__(self, server=None, port=None, url_scheme=None, api=None,
                 version=None):
      self.server = server
      self.port = port
      self.url_scheme = url_scheme
      self.body_json = {'api': api, 'version': version}

  def setUp(self):
    """Make ApiConfigManager with a few helpful fakes."""
    self.backend = self._create_wsgi_application()
    self.config_manager = api_config_manager.ApiConfigManager()
    self.discovery = discovery_service.DiscoveryService(
        self.config_manager, self.backend)

  def _create_wsgi_application(self):
    return apiserving._ApiServer([AService], registry_path='/my_registry')

  def _check_api_config(self, expected_base_url, server, port, url_scheme, api,
                        version):
    request = DiscoveryServiceTest.FakeRequest(
        server=server, port=port, url_scheme=url_scheme, api=api,
        version=version)
    config_dict = self.discovery._generate_api_config_with_root(request)

    # Check bns entry
    adapter = config_dict.get('adapter')
    self.assertIsNotNone(adapter)
    self.assertEqual(expected_base_url, adapter.get('bns'))

    # Check root
    self.assertEqual(expected_base_url, config_dict.get('root'))


class ProdDiscoveryServiceTest(DiscoveryServiceTest):

  def testGenerateApiConfigWithRoot(self):
    server = 'test.appspot.com'
    port = '12345'
    url_scheme = 'https'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}:{2}/_ah/api'.format(url_scheme, server, port)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigWithRootLocalhost(self):
    server = 'localhost'
    port = '12345'
    url_scheme = 'http'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}:{2}/_ah/api'.format(url_scheme, server, port)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigLocalhostDefaultHttpPort(self):
    server = 'localhost'
    port = '80'
    url_scheme = 'http'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}/_ah/api'.format(url_scheme, server)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigWithRootDefaultHttpsPort(self):
    server = 'test.appspot.com'
    port = '443'
    url_scheme = 'https'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}/_ah/api'.format(url_scheme, server)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)


class DevServerDiscoveryServiceTest(DiscoveryServiceTest,
                                    test_util.DevServerTest):

  def setUp(self):
    super(DevServerDiscoveryServiceTest, self).setUp()
    self.env_key, self.orig_env_value = (test_util.DevServerTest.
                                         setUpDevServerEnv())
    self.addCleanup(test_util.DevServerTest.restoreEnv,
                    self.env_key, self.orig_env_value)

  def testGenerateApiConfigWithRootDefaultHttpPort(self):
    server = 'test.appspot.com'
    port = '80'
    url_scheme = 'http'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}/_ah/api'.format(url_scheme, server)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigLocalhostDefaultHttpPort(self):
    server = 'localhost'
    port = '80'
    url_scheme = 'http'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}/_ah/api'.format(url_scheme, server)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigHTTPS(self):
    server = 'test.appspot.com'
    port = '443'
    url_scheme = 'http'  # Should still be 'http' because we're using devserver
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}:{2}/_ah/api'.format(url_scheme, server, port)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)


class Airport(messages.Message):
  iata = messages.StringField(1, required=True)
  name = messages.StringField(2, required=True)

class AirportList(messages.Message):
  airports = messages.MessageField(Airport, 1, repeated=True)

@api_config.api(name='iata', version='v1')
class V1Service(remote.Service):
  @api_config.method(
      message_types.VoidMessage,
      AirportList,
      path='airports',
      http_method='GET',
      name='list_airports')
  def list_airports(self, request):
    return AirportList(airports=[
        Airport(iata=u'DEN', name=u'Denver International Airport'),
        Airport(iata=u'SEA', name=u'Seattle Tacoma International Airport'),
    ])

@api_config.api(name='iata', version='v2')
class V2Service(remote.Service):
  @api_config.method(
      message_types.VoidMessage,
      AirportList,
      path='airports',
      http_method='GET',
      name='list_airports')
  def list_airports(self, request):
    return AirportList(airports=[
        Airport(iata=u'DEN', name=u'Denver International Airport'),
        Airport(iata=u'JFK', name=u'John F Kennedy International Airport'),
        Airport(iata=u'SEA', name=u'Seattle Tacoma International Airport'),
    ])

class DiscoveryServiceVersionTest(unittest.TestCase):
  def setUp(self):
    api = apiserving.api_server([V1Service, V2Service])
    self.app = webtest.TestApp(api)

  def testListApis(self):
    resp = self.app.get('http://localhost/_ah/api/discovery/v1/apis')
    items = resp.json['items']
    self.assertItemsEqual(
        (i['id'] for i in items), [u'iata:v1', u'iata:v2'])
    self.assertItemsEqual(
        (i['discoveryLink'] for i in items),
        [u'./apis/iata/v1/rest', u'./apis/iata/v2/rest'])

  def testGetApis(self):
    for version in ['v1', 'v2']:
      resp = self.app.get(
          'http://localhost/_ah/api/discovery/v1/apis/iata/{}/rest'.format(version))
      self.assertEqual(resp.json['version'], version)
      self.assertItemsEqual(resp.json['methods'].keys(), [u'list_airports'])

if __name__ == '__main__':
  unittest.main()
