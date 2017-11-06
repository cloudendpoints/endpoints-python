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

"""Tests for endpoints.discovery_generator."""

import json
import os
import unittest

import endpoints.api_config as api_config
import endpoints.api_exceptions as api_exceptions
import endpoints.users_id_token as users_id_token
import endpoints.types as endpoints_types

from protorpc import message_types
from protorpc import messages
from protorpc import remote

import endpoints.resource_container as resource_container
import endpoints.discovery_generator as discovery_generator
import test_util


package = 'DiscoveryGeneratorTest'


class Nested(messages.Message):
  """Message class to be used in a message field."""
  int_value = messages.IntegerField(1)
  string_value = messages.StringField(2)


class SimpleEnum(messages.Enum):
  """Simple enumeration type."""
  VAL1 = 1
  VAL2 = 2


class IdField(messages.Message):
  """Just contains an integer field."""
  id_value = messages.IntegerField(1, variant=messages.Variant.INT32)


class AllFields(messages.Message):
  """Contains all field types."""

  bool_value = messages.BooleanField(1, variant=messages.Variant.BOOL)
  bytes_value = messages.BytesField(2, variant=messages.Variant.BYTES)
  double_value = messages.FloatField(3, variant=messages.Variant.DOUBLE)
  enum_value = messages.EnumField(SimpleEnum, 4)
  float_value = messages.FloatField(5, variant=messages.Variant.FLOAT)
  int32_value = messages.IntegerField(6, variant=messages.Variant.INT32)
  int64_value = messages.IntegerField(7, variant=messages.Variant.INT64)
  string_value = messages.StringField(8, variant=messages.Variant.STRING)
  uint32_value = messages.IntegerField(9, variant=messages.Variant.UINT32)
  uint64_value = messages.IntegerField(10, variant=messages.Variant.UINT64)
  sint32_value = messages.IntegerField(11, variant=messages.Variant.SINT32)
  sint64_value = messages.IntegerField(12, variant=messages.Variant.SINT64)
  message_field_value = messages.MessageField(Nested, 13)
  datetime_value = message_types.DateTimeField(14)


# This is used test "all fields" as query parameters instead of the body
# in a request.
ALL_FIELDS_AS_PARAMETERS = resource_container.ResourceContainer(
    **{field.name: field for field in AllFields.all_fields()})


class BaseDiscoveryGeneratorTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.maxDiff = None

  def setUp(self):
    self.generator = discovery_generator.DiscoveryGenerator()

  def _def_path(self, path):
    return '#/definitions/' + path


class DiscoveryGeneratorTest(BaseDiscoveryGeneratorTest):

  def testAllFieldTypes(self):

    class PutRequest(messages.Message):
      """Message with just a body field."""
      body = messages.MessageField(AllFields, 1)

    # pylint: disable=invalid-name
    class ItemsPutRequest(messages.Message):
      """Message with path params and a body field."""
      body = messages.MessageField(AllFields, 1)
      entryId = messages.StringField(2, required=True)

    class ItemsPutRequestForContainer(messages.Message):
      """Message with path params and a body field."""
      body = messages.MessageField(AllFields, 1)

    items_put_request_container = resource_container.ResourceContainer(
        ItemsPutRequestForContainer,
        entryId=messages.StringField(2, required=True))

    # pylint: disable=invalid-name
    class EntryPublishRequest(messages.Message):
      """Message with two required params, one in path, one in body."""
      title = messages.StringField(1, required=True)
      entryId = messages.StringField(2, required=True)

    class EntryPublishRequestForContainer(messages.Message):
      """Message with two required params, one in path, one in body."""
      title = messages.StringField(1, required=True)

    entry_publish_request_container = resource_container.ResourceContainer(
        EntryPublishRequestForContainer,
        entryId=messages.StringField(2, required=True))

    class BooleanMessageResponse(messages.Message):
      result = messages.BooleanField(1, required=True)

    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    description='This is an API')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, BooleanMessageResponse,
                        path ='toplevel:withcolon', http_method='GET',
                        name='toplevelwithcolon')
      def toplevel(self, unused_request):
        return BooleanMessageResponse(result=True)

      @api_config.method(AllFields, message_types.VoidMessage, path='entries',
                         http_method='GET', name='entries.get')
      def entries_get(self, unused_request):
        """All field types in the query parameters."""
        return message_types.VoidMessage()

      @api_config.method(ALL_FIELDS_AS_PARAMETERS, message_types.VoidMessage,
                         path='entries/container', http_method='GET',
                         name='entries.getContainer')
      def entries_get_container(self, unused_request):
        """All field types in the query parameters."""
        return message_types.VoidMessage()

      @api_config.method(PutRequest, BooleanMessageResponse, path='entries',
                         name='entries.put')
      def entries_put(self, unused_request):
        """Request body is in the body field."""
        return BooleanMessageResponse(result=True)

      @api_config.method(AllFields, message_types.VoidMessage, path='process',
                         name='entries.process')
      def entries_process(self, unused_request):
        """Message is the request body."""
        return message_types.VoidMessage()

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         name='entries.nested.collection.action',
                         path='nested')
      def entries_nested_collection_action(self, unused_request):
        """A VoidMessage for a request body."""
        return message_types.VoidMessage()

      @api_config.method(AllFields, AllFields, name='entries.roundtrip',
                         path='roundtrip')
      def entries_roundtrip(self, unused_request):
        """All field types in the request and response."""
        pass

      # Test a method with a required parameter in the request body.
      @api_config.method(EntryPublishRequest, message_types.VoidMessage,
                         path='entries/{entryId}/publish',
                         name='entries.publish')
      def entries_publish(self, unused_request):
        """Path has a parameter and request body has a required param."""
        return message_types.VoidMessage()

      @api_config.method(entry_publish_request_container,
                         message_types.VoidMessage,
                         path='entries/container/{entryId}/publish',
                         name='entries.publishContainer')
      def entries_publish_container(self, unused_request):
        """Path has a parameter and request body has a required param."""
        return message_types.VoidMessage()

      # Test a method with a parameter in the path and a request body.
      @api_config.method(ItemsPutRequest, message_types.VoidMessage,
                         path='entries/{entryId}/items',
                         name='entries.items.put')
      def items_put(self, unused_request):
        """Path has a parameter and request body is in the body field."""
        return message_types.VoidMessage()

      @api_config.method(items_put_request_container, message_types.VoidMessage,
                         path='entries/container/{entryId}/items',
                         name='entries.items.putContainer')
      def items_put_container(self, unused_request):
        """Path has a parameter and request body is in the body field."""
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    try:
      pwd = os.path.dirname(os.path.realpath(__file__))
      test_file = os.path.join(pwd, 'testdata', 'discovery', 'allfields.json')
      with open(test_file) as f:
        expected_discovery = json.loads(f.read())
    except IOError as e:
      print 'Could not find expected output file ' + test_file
      raise e

    test_util.AssertDictEqual(expected_discovery, api, self)

  def testNamespace(self):
    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    description='This is an API',
                    namespace=api_config.Namespace('domain', 'name', 'path'))
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(IdField, message_types.VoidMessage, path='entries',
                         http_method='GET', name='get_entry')
      def entries_get(self, unused_request):
        """Id (integer) field type in the query parameters."""
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    try:
      pwd = os.path.dirname(os.path.realpath(__file__))
      test_file = os.path.join(pwd, 'testdata', 'discovery', 'namespace.json')
      with open(test_file) as f:
        expected_discovery = json.loads(f.read())
    except IOError as e:
      print 'Could not find expected output file ' + test_file
      raise e

    test_util.AssertDictEqual(expected_discovery, api, self)

  def testNamespaceDefaultPath(self):
    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    description='This is an API',
                    namespace=api_config.Namespace('domain', 'name', None))
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(IdField, message_types.VoidMessage, path='entries',
                         http_method='GET', name='get_entry')
      def entries_get(self, unused_request):
        """Id (integer) field type in the query parameters."""
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    try:
      pwd = os.path.dirname(os.path.realpath(__file__))
      test_file = os.path.join(pwd, 'testdata', 'discovery', 'namespace.json')
      with open(test_file) as f:
        expected_discovery = json.loads(f.read())
    except IOError as e:
      print 'Could not find expected output file ' + test_file
      raise e

    # Clear the value of the packagePath parameter in the expected results
    expected_discovery['packagePath'] = ''

    test_util.AssertDictEqual(expected_discovery, api, self)

class DiscoveryMultiClassGeneratorTest(BaseDiscoveryGeneratorTest):

  def testMultipleClassService(self):
    '''If multiple classes of a single service are passed to the
    generator, the document should show all methods from all
    classes.'''
    class Airport(messages.Message):
      iata = messages.StringField(1, required=True)
      name = messages.StringField(2, required=True)

    IATA_RESOURCE = resource_container.ResourceContainer(
        iata=messages.StringField(1, required=True)
    )

    class AirportList(messages.Message):
      airports = messages.MessageField(Airport, 1, repeated=True)

    @api_config.api(name='iata', version='v1')
    class ServicePart1(remote.Service):
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

    @api_config.api(name='iata', version='v1')
    class ServicePart2(remote.Service):
      @api_config.method(
          IATA_RESOURCE,
          Airport,
          path='airport/{iata}',
          http_method='GET',
          name='get_airport')
      def get_airport(self, request):
        airports = {
          'DEN': 'Denver International Airport'
        }
        if request.iata not in airports:
          raise endpoints.NotFoundException()
        return Airport(iata=request.iata, name=airports[request.iata])

    doc = self.generator.get_discovery_doc([ServicePart1, ServicePart2])
    self.assertItemsEqual(doc['methods'].keys(), [u'get_airport', u'list_airports'])

  def testMethodCollisionDetection(self):
    '''While multiple classes can be passed to the generator at once,
    they should all belong to the same api and version.'''
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

    error = "Multiple apis/versions found: [('iata', 'v1'), ('iata', 'v2')]"
    with self.assertRaises(api_exceptions.ApiConfigurationError) as catcher:
      self.generator.get_discovery_doc([V1Service, V2Service])
    self.assertEqual(catcher.exception.message, error)


    @api_config.api(name='iata', version='v1')
    class V1ServiceCont(remote.Service):
      @api_config.method(
          message_types.VoidMessage,
          AirportList,
          path='airports',
          http_method='GET',
          name='list_airports')
      def list_airports(self, request):
        return AirportList(airports=[
            Airport(iata=u'JFK', name=u'John F Kennedy International Airport'),
        ])

    error = "Method iata.list_airports used multiple times"
    with self.assertRaises(api_exceptions.ApiConfigurationError) as catcher:
      self.generator.get_discovery_doc([V1Service, V1ServiceCont])
    self.assertEqual(catcher.exception.message[:len(error)], error)


class DiscoveryScopeGeneratorTest(BaseDiscoveryGeneratorTest):

  def testDefaultScope(self):
    IATA_RESOURCE = resource_container.ResourceContainer(
        iata=messages.StringField(1)
    )

    class IataParam(messages.Message):
        iata = messages.StringField(1)

    class Airport(messages.Message):
        iata = messages.StringField(1, required=True)
        name = messages.StringField(2, required=True)

    @api_config.api(
        name='iata', version='v1',
        auth_level=api_config.AUTH_LEVEL.REQUIRED,
        allowed_client_ids=users_id_token.SKIP_CLIENT_ID_CHECK)
    class IataApi(remote.Service):
        @api_config.method(
            IATA_RESOURCE,
            Airport,
            path='airport/{iata}',
            http_method='GET',
            name='get_airport')
        def get_airport(self, request):
            return Airport(iata=request.iata, name='irrelevant')

    doc = self.generator.get_discovery_doc([IataApi])
    auth = doc['auth']
    assert auth == {
        'oauth2': {
            'scopes': {
                'https://www.googleapis.com/auth/userinfo.email': {
                    'description': 'View your email address'
                }
            }
        }
    }

  def testCustomScope(self):
    SCOPE = endpoints_types.OAuth2Scope(
        scope='https://www.googleapis.com/auth/santa',
        description='Access your letter to Santa')

    IATA_RESOURCE = resource_container.ResourceContainer(
        iata=messages.StringField(1)
    )

    class IataParam(messages.Message):
        iata = messages.StringField(1)

    class Airport(messages.Message):
        iata = messages.StringField(1, required=True)
        name = messages.StringField(2, required=True)

    @api_config.api(
        name='iata', version='v1', scopes=[SCOPE],
        auth_level=api_config.AUTH_LEVEL.REQUIRED,
        allowed_client_ids=users_id_token.SKIP_CLIENT_ID_CHECK)
    class IataApi(remote.Service):
        @api_config.method(
            IATA_RESOURCE,
            Airport,
            path='airport/{iata}',
            http_method='GET',
            name='get_airport')
        def get_airport(self, request):
            return Airport(iata=request.iata, name='irrelevant')

    doc = self.generator.get_discovery_doc([IataApi])
    auth = doc['auth']
    assert auth == {
        'oauth2': {
            'scopes': {
                SCOPE.scope: {
                    'description': SCOPE.description
                }
            }
        }
    }

class DiscoveryUrlGeneratorTest(BaseDiscoveryGeneratorTest):

  def testUrlGeneration(self):
    IATA_RESOURCE = resource_container.ResourceContainer(
        iata=messages.StringField(1)
    )

    class IataParam(messages.Message):
        iata = messages.StringField(1)

    class Airport(messages.Message):
        iata = messages.StringField(1, required=True)
        name = messages.StringField(2, required=True)

    @api_config.api(name='iata', version='v1')
    class IataApi(remote.Service):
        @api_config.method(
            IATA_RESOURCE,
            Airport,
            path='airport/{iata}',
            http_method='GET',
            name='get_airport')
        def get_airport(self, request):
            return Airport(iata=request.iata, name='irrelevant')

    doc = self.generator.get_discovery_doc([IataApi], hostname='iata.appspot.com')
    assert doc['baseUrl'] == 'https://iata.appspot.com/_ah/api/iata/v1/'
    assert doc['rootUrl'] == 'https://iata.appspot.com/_ah/api/'
    assert doc['servicePath'] == 'iata/v1/'


class Recursive(messages.Message):
    """Message which can contain itself."""
    desc = messages.StringField(1)
    subrecursive = messages.MessageField('Recursive', 2, repeated=True)

class ContainsRecursive(messages.Message):
    """Message which contains a recursive message."""

    id = messages.IntegerField(1)
    recursives = messages.MessageField(Recursive, 2, repeated=True)

@api_config.api(name='example', version='v1')
class ExampleApi(remote.Service):
    @api_config.method(
        ContainsRecursive,
        message_types.VoidMessage,
        path='recursive',
        http_method='POST',
        name='save_recursive')
    def save_recursive(self, request):
        raise NotImplementedError()


class DiscoveryRecursiveGeneratorTest(BaseDiscoveryGeneratorTest):
  """Ensure that it's possible to generate a doc for an api which
  accepts a recursive message structure in requests."""

  def testRecursive(self):
    doc = self.generator.get_discovery_doc([ExampleApi], hostname='example.appspot.com')
    assert sorted(doc['schemas'].keys()) == [
        'DiscoveryGeneratorTestContainsRecursive', 'DiscoveryGeneratorTestRecursive']


if __name__ == '__main__':
  unittest.main()
