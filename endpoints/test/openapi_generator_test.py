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

"""Tests for endpoints.openapi_generator."""

import json
import unittest

import endpoints.api_config as api_config

from protorpc import message_types
from protorpc import messages
from protorpc import remote

import endpoints.resource_container as resource_container
import endpoints.openapi_generator as openapi_generator
import test_util


package = 'OpenApiGeneratorTest'


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


class IdRepeatedField(messages.Message):
  """Contains a repeated integer field."""
  id_values = messages.IntegerField(1, variant=messages.Variant.INT32,
                                    repeated=True)


class NestedRepeatedMessage(messages.Message):
  """Contains a repeated Message field."""
  message_field_value = messages.MessageField(Nested, 1, repeated=True)


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


REPEATED_CONTAINER = resource_container.ResourceContainer(
    IdField,
    repeated_field=messages.StringField(2, repeated=True))


# Some constants to shorten line length in expected OpenAPI output
PREFIX = 'OpenApiGeneratorTest'
BOOLEAN_RESPONSE = PREFIX + 'BooleanMessageResponse'
ALL_FIELDS = PREFIX + 'AllFields'
NESTED = PREFIX + 'Nested'
NESTED_REPEATED_MESSAGE = PREFIX + 'NestedRepeatedMessage'
ENTRY_PUBLISH_REQUEST = PREFIX + 'EntryPublishRequest'
PUBLISH_REQUEST_FOR_CONTAINER = PREFIX + 'EntryPublishRequestForContainer'
ITEMS_PUT_REQUEST = PREFIX + 'ItemsPutRequest'
PUT_REQUEST_FOR_CONTAINER = PREFIX + 'ItemsPutRequestForContainer'
PUT_REQUEST = PREFIX + 'PutRequest'
ID_FIELD = PREFIX + 'IdField'
ID_REPEATED_FIELD = PREFIX + 'IdRepeatedField'


class BaseOpenApiGeneratorTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.maxDiff = None

  def setUp(self):
    self.generator = openapi_generator.OpenApiGenerator()

  def _def_path(self, path):
    return '#/definitions/' + path


class OpenApiGeneratorTest(BaseOpenApiGeneratorTest):

  def testAllFieldTypesPost(self):

    @api_config.api(name='root', hostname='example.appspot.com', version='v1')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(AllFields, message_types.VoidMessage, path='entries',
                         http_method='POST', name='entries')
      def entries_post(self, unused_request):
        return message_types.VoidMessage()

      @api_config.method(AllFields, message_types.VoidMessage, path='entries2',
                         http_method='POST', name='entries2', api_key_required=True)
      def entries_post_protected(self, unused_request):
        return message_types.VoidMessage()

      @api_config.method(AllFields, message_types.VoidMessage, path='entries3',
                         http_method='POST', name='entries3', audiences=['foo'])
      def entries_post_audience(self, unused_request):
        return message_types.VoidMessage()

      @api_config.method(AllFields, message_types.VoidMessage, path='entries4',
                         http_method='POST', name='entries4', audiences=['foo', 'bar'])
      def entries_post_audiences(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/entries': {
                'post': {
                    'operationId': 'MyService_entriesPost',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(ALL_FIELDS)
                            },
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
            "/root/v1/entries2": {
                "post": {
                    "operationId": "MyService_entriesPostProtected",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "$ref": "#/definitions/OpenApiGeneratorTestAllFields"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A successful response"
                        }
                    },
                    "security": [
                        {
                            "api_key": []
                        }
                    ]
                }
            },
            "/root/v1/entries3": {
                "post": {
                    "operationId": "MyService_entriesPostAudience",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "$ref": "#/definitions/OpenApiGeneratorTestAllFields"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A successful response"
                        }
                    },
                    "security": [
                        {
                            "google_id_token-acbd18db": []
                        }
                    ],
                }
            },
            "/root/v1/entries4": {
                "post": {
                    "operationId": "MyService_entriesPostAudiences",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "$ref": "#/definitions/OpenApiGeneratorTestAllFields"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A successful response"
                        }
                    },
                    "security": [
                        {
                            "google_id_token-eb76e999": []
                        }
                    ],
                }
            },
        },
        'definitions': {
            ALL_FIELDS: {
                'type': 'object',
                'properties': {
                    'bool_value': {
                        'type': 'boolean',
                    },
                    'bytes_value': {
                        'type': 'string',
                        'format': 'byte',
                    },
                    'datetime_value': {
                        'type': 'string',
                        'format': 'date-time',
                    },
                    'double_value': {
                        'type': 'number',
                        'format': 'double',
                    },
                    'enum_value': {
                        'type': 'string',
                        'enum': [
                            'VAL1',
                            'VAL2',
                        ],
                    },
                    'float_value': {
                        'type': 'number',
                        'format': 'float',
                    },
                    'int32_value': {
                        'type': 'integer',
                        'format': 'int32',
                    },
                    'int64_value': {
                        'type': 'string',
                        'format': 'int64',
                    },
                    'message_field_value': {
                        '$ref': self._def_path(NESTED),
                        'description':
                            'Message class to be used in a message field.',
                    },
                    'sint32_value': {
                        'type': 'integer',
                        'format': 'int32',
                    },
                    'sint64_value': {
                        'type': 'string',
                        'format': 'int64',
                    },
                    'string_value': {
                        'type': 'string',
                    },
                    'uint32_value': {
                        'type': 'integer',
                        'format': 'uint32',
                    },
                    'uint64_value': {
                        'type': 'string',
                        'format': 'uint64',
                    },
                },
            },
            "OpenApiGeneratorTestNested": {
                "type": "object",
                "properties": {
                    "int_value": {
                        "format": "int64",
                        "type": "string"
                    },
                    "string_value": {
                        "type": "string"
                    },
                },
            },
        },
        "securityDefinitions": {
            "api_key": {
                "type": "apiKey",
                "name": "key",
                "in": "query",
            },
            "google_id_token": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
            "google_id_token-acbd18db": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
                "x-google-audiences": "foo",
            },
            "google_id_token-eb76e999": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
                "x-google-audiences": "bar,foo",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

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

    @api_config.api(name='root', hostname='example.appspot.com', version='v1')
    class MyService(remote.Service):
      """Describes MyService."""

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

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/entries': {
                'get': {
                    'operationId': 'MyService_entriesGet',
                    'parameters': [
                        {
                            'name': 'bool_value',
                            'in': 'query',
                            'type': 'boolean',
                        },
                        {
                            'name': 'bytes_value',
                            'in': 'query',
                            'type': 'string',
                            'format': 'byte',
                        },
                        {
                            'name': 'double_value',
                            'in': 'query',
                            'type': 'number',
                            'format': 'double',
                        },
                        {
                            'name': 'enum_value',
                            'in': 'query',
                            'type': 'string',
                            'enum': [
                                'VAL1',
                                'VAL2',
                            ],
                        },
                        {
                            'name': 'float_value',
                            'in': 'query',
                            'type': 'number',
                            'format': 'float',
                        },
                        {
                            'name': 'int32_value',
                            'in': 'query',
                            'type': 'integer',
                            'format': 'int32',
                        },
                        {
                            'name': 'int64_value',
                            'in': 'query',
                            'type': 'string',
                            'format': 'int64',
                        },
                        {
                            'name': 'string_value',
                            'in': 'query',
                            'type': 'string',
                        },
                        {
                            'name': 'uint32_value',
                            'in': 'query',
                            'type': 'integer',
                            'format': 'uint32',
                        },
                        {
                            'name': 'uint64_value',
                            'in': 'query',
                            'type': 'string',
                            'format': 'uint64',
                        },
                        {
                            'name': 'sint32_value',
                            'in': 'query',
                            'type': 'integer',
                            'format': 'int32',
                        },
                        {
                            'name': 'sint64_value',
                            'in': 'query',
                            'type': 'string',
                            'format': 'int64',
                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
                'post': {
                    'operationId': 'MyService_entriesPut',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(PUT_REQUEST)
                            }

                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                            'schema': {
                                '$ref': self._def_path(BOOLEAN_RESPONSE),
                            },
                        },
                    },
                },
            },
            '/root/v1/entries/container': {
                'get': {
                    'operationId': 'MyService_entriesGetContainer',
                    'parameters': [
                        {
                            'name': 'bool_value',
                            'in': 'query',
                            'type': 'boolean',
                        },
                        {
                            'name': 'bytes_value',
                            'in': 'query',
                            'type': 'string',
                            'format': 'byte',
                        },
                        {
                            'name': 'double_value',
                            'in': 'query',
                            'type': 'number',
                            'format': 'double',
                        },
                        {
                            'name': 'enum_value',
                            'in': 'query',
                            'type': 'string',
                            'enum': [
                                'VAL1',
                                'VAL2',
                            ],
                        },
                        {
                            'name': 'float_value',
                            'in': 'query',
                            'type': 'number',
                            'format': 'float',
                        },
                        {
                            'name': 'int32_value',
                            'in': 'query',
                            'type': 'integer',
                            'format': 'int32',
                        },
                        {
                            'name': 'int64_value',
                            'in': 'query',
                            'type': 'string',
                            'format': 'int64',
                        },
                        {
                            'name': 'string_value',
                            'in': 'query',
                            'type': 'string',
                        },
                        {
                            'name': 'uint32_value',
                            'in': 'query',
                            'type': 'integer',
                            'format': 'uint32',
                        },
                        {
                            'name': 'uint64_value',
                            'in': 'query',
                            'type': 'string',
                            'format': 'uint64',
                        },
                        {
                            'name': 'sint32_value',
                            'in': 'query',
                            'type': 'integer',
                            'format': 'int32',
                        },
                        {
                            'name': 'sint64_value',
                            'in': 'query',
                            'type': 'string',
                            'format': 'int64',
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
            '/root/v1/entries/container/{entryId}/items': {
                'post': {
                    'operationId': 'MyService_itemsPutContainer',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(
                                    PUT_REQUEST_FOR_CONTAINER)
                            },
                        },
                        {
                            'name': 'entryId',
                            'in': 'path',
                            'required': True,
                            'type': 'string',
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
            '/root/v1/entries/container/{entryId}/publish': {
                'post': {
                    'operationId': 'MyService_entriesPublishContainer',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(
                                    PUBLISH_REQUEST_FOR_CONTAINER)
                            },
                        },
                        {
                            'name': 'entryId',
                            'in': 'path',
                            'required': True,
                            'type': 'string',
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
            '/root/v1/entries/{entryId}/items': {
                'post': {
                    'operationId': 'MyService_itemsPut',
                    'parameters': [
                        {
                            'name': 'entryId',
                            'in': 'path',
                            'required': True,
                            'type': 'string',
                        },
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(ITEMS_PUT_REQUEST)
                            },
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
            '/root/v1/entries/{entryId}/publish': {
                'post': {
                    'operationId': 'MyService_entriesPublish',
                    'parameters': [
                        {
                            'name': 'entryId',
                            'in': 'path',
                            'required': True,
                            'type': 'string',
                        },
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(ENTRY_PUBLISH_REQUEST)
                            },
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
            '/root/v1/nested': {
                'post': {
                    'operationId': 'MyService_entriesNestedCollectionAction',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
            '/root/v1/process': {
                'post': {
                    'operationId': 'MyService_entriesProcess',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(ALL_FIELDS)
                            },
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
            '/root/v1/roundtrip': {
                'post': {
                    'operationId': 'MyService_entriesRoundtrip',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(ALL_FIELDS)
                            },
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                            'schema': {
                                '$ref': self._def_path(ALL_FIELDS)
                            },
                        },
                    },
                },
            },
        },
        'definitions': {
            ALL_FIELDS: {
                'type': 'object',
                'properties': {
                    'bool_value': {
                        'type': 'boolean',
                    },
                    'bytes_value': {
                        'type': 'string',
                        'format': 'byte',
                    },
                    'datetime_value': {
                        'type': 'string',
                        'format': 'date-time',
                    },
                    'double_value': {
                        'type': 'number',
                        'format': 'double',
                    },
                    'enum_value': {
                        'type': 'string',
                        'enum': [
                            'VAL1',
                            'VAL2',
                        ],
                    },
                    'float_value': {
                        'type': 'number',
                        'format': 'float',
                    },
                    'int32_value': {
                        'type': 'integer',
                        'format': 'int32',
                    },
                    'int64_value': {
                        'type': 'string',
                        'format': 'int64',
                    },
                    'message_field_value': {
                        '$ref': self._def_path(NESTED),
                        'description':
                            'Message class to be used in a message field.',
                    },
                    'sint32_value': {
                        'type': 'integer',
                        'format': 'int32',
                    },
                    'sint64_value': {
                        'type': 'string',
                        'format': 'int64',
                    },
                    'string_value': {
                        'type': 'string',
                    },
                    'uint32_value': {
                        'type': 'integer',
                        'format': 'uint32',
                    },
                    'uint64_value': {
                        'type': 'string',
                        'format': 'uint64',
                    },
                },
            },
            BOOLEAN_RESPONSE: {
                'type': 'object',
                'properties': {
                    'result': {
                        'type': 'boolean',
                    },
                },
                'required': ['result'],
            },
            ENTRY_PUBLISH_REQUEST: {
                'type': 'object',
                'properties': {
                    'entryId': {
                        'type': 'string',
                    },
                    'title': {
                        'type': 'string',
                    },
                },
                'required': [
                    'entryId',
                    'title',
                ]
            },
            PUBLISH_REQUEST_FOR_CONTAINER: {
                'type': 'object',
                'properties': {
                    'title': {
                        'type': 'string',
                    },
                },
                'required': [
                    'title',
                ]
            },
            ITEMS_PUT_REQUEST: {
                'type': 'object',
                'properties': {
                    'body': {
                        '$ref': self._def_path(ALL_FIELDS),
                        'description': 'Contains all field types.'
                    },
                    'entryId': {
                        'type': 'string',
                    },
                },
                'required': [
                    'entryId',
                ]
            },
            NESTED: {
                'type': 'object',
                'properties': {
                    'int_value': {
                        'type': 'string',
                        'format': 'int64',
                    },
                    'string_value': {
                        'type': 'string',
                    },
                },
            },
            PUT_REQUEST: {
                'type': 'object',
                'properties': {
                    'body': {
                        '$ref': self._def_path(ALL_FIELDS),
                        'description': 'Contains all field types.',
                    },
                },
            },
            PUT_REQUEST_FOR_CONTAINER: {
                'type': 'object',
                'properties': {
                    'body': {
                        '$ref': self._def_path(ALL_FIELDS),
                        'description': 'Contains all field types.',
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testPathParamImpliedRequired(self):

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

        @api_config.method(
            IataParam,
            Airport,
            path='airport/2/{iata}',
            http_method='GET',
            name='get_airport_2')
        def get_airport_2(self, request):
            return Airport(iata=request.iata, name='irrelevant')

    api = json.loads(self.generator.pretty_print_config_to_json(IataApi))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'iata',
            'version': 'v1',
        },
        'host': None,
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'definitions': {
            'OpenApiGeneratorTestAirport': {
                'properties': {
                    'iata': {'type': 'string'},
                    'name': {'type': 'string'}
                },
                'required': [
                    'iata',
                    'name'],
                'type': 'object'
            }
        },
        'paths': {
            '/iata/v1/airport/2/{iata}': {
                'get': {
                    'operationId': 'IataApi_getAirport2',
                    'parameters': [
                        {
                            'in': 'path',
                            'name': 'iata',
                            'required': True,
                            'type': 'string'
                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                            'schema': {
                                '$ref': '#/definitions/OpenApiGeneratorTestAirport'
                            }
                        }
                    }
                }
            },
            '/iata/v1/airport/{iata}': {
                'get': {
                    'operationId': 'IataApi_getAirport',
                    'parameters': [
                        {
                            'in': 'path',
                            'name': 'iata',
                            'required': True,
                            'type': 'string'
                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                            'schema': {
                                '$ref': '#/definitions/OpenApiGeneratorTestAirport'
                            }
                        }
                    }
                }
            }
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                'x-google-issuer': 'https://accounts.google.com',
                'x-google-jwks_uri': 'https://www.googleapis.com/oauth2/v3/certs',
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testLocalhost(self):
    @api_config.api(name='root', hostname='localhost:8080', version='v1')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='noop', http_method='GET', name='noop')
      def noop_get(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'localhost:8080',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['http'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/noop': {
                'get': {
                    'operationId': 'MyService_noopGet',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testMetricCosts(self):

    limit_definitions = [
        api_config.LimitDefinition('example/read_requests',
                                   'My Read API Requests per Minute',
                                   1000),
        api_config.LimitDefinition('example/list_requests',
                                   'My List API Requests per Minute',
                                   100),
    ]

    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    limit_definitions=limit_definitions)
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='noop', http_method='GET', name='noop',
                         metric_costs={'example/read_requests': 5,
                                       'example/list_requests': 1})
      def noop_get(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/noop': {
                'get': {
                    'operationId': 'MyService_noopGet',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                    'x-google-quota': {
                        'metricCosts': {
                            'example/read_requests': 5,
                            'example/list_requests': 1,
                        }
                    }
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                'x-google-issuer': 'https://accounts.google.com',
                'x-google-jwks_uri': 'https://www.googleapis.com/oauth2/v3/certs',
            },
        },
        'x-google-management': {
            'quota': {
                'limits': [
                    {
                        'name': 'example/read_requests',
                        'metric': 'example/read_requests',
                        'unit': '1/min/{project}',
                        'values': {
                            'STANDARD': 1000
                        },
                        'displayName': 'My Read API Requests per Minute',
                    },
                    {
                        'name': 'example/list_requests',
                        'metric': 'example/list_requests',
                        'unit': '1/min/{project}',
                        'values': {
                            'STANDARD': 100
                        },
                        'displayName': 'My List API Requests per Minute',
                    },
                ],
            },
            'metrics': [
                {
                    'name': 'example/read_requests',
                    'valueType': 'INT64',
                    'metricKind': 'GAUGE',
                },
                {
                    'name': 'example/list_requests',
                    'valueType': 'INT64',
                    'metricKind': 'GAUGE',
                },
            ]
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testApiKeyRequired(self):

    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    api_key_required=True)
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='noop', http_method='GET', name='noop')
      def noop_get(self, unused_request):
        return message_types.VoidMessage()

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='override', http_method='GET', name='override',
                         api_key_required=False)
      def override_get(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/noop': {
                'get': {
                    'operationId': 'MyService_noopGet',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                    'security': [
                        {
                            'api_key': [],
                        }
                    ],
                },
            },
            '/root/v1/override': {
                'get': {
                    'operationId': 'MyService_overrideGet',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
            'api_key': {
                'type': 'apiKey',
                'name': 'key',
                'in': 'query',
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testCustomUrl(self):

    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    base_path='/my/base/path/')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='noop', http_method='GET', name='noop')
      def noop_get(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/my/base/path',
        'paths': {
            '/root/v1/noop': {
                'get': {
                    'operationId': 'MyService_noopGet',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testRootUrl(self):

    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    base_path='/')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='noop', http_method='GET', name='noop')
      def noop_get(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/',
        'paths': {
            '/root/v1/noop': {
                'get': {
                    'operationId': 'MyService_noopGet',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    assert api == expected_openapi

  def testRepeatedResourceContainer(self):
    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    description='Testing repeated params')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(REPEATED_CONTAINER, message_types.VoidMessage,
                         path='toplevel', http_method='POST')
      def toplevel(self, unused_request):
        """Testing a ResourceContainer with a repeated query param."""
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Testing repeated params',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'definitions': {
            'OpenApiGeneratorTestIdField': {
                'properties': {
                    'id_value': {
                        'format': 'int32',
                        'type': 'integer'
                    }
                },
                'type': 'object'
            },
        },
        'paths': {
            '/root/v1/toplevel': {
                'post': {
                    'operationId': 'MyService_toplevel',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(ID_FIELD)
                            },
                        },
                        {
                            "collectionFormat": "multi",
                            "in": "query",
                            "items": {
                                "type": "string"
                            },
                            "name": "repeated_field",
                            "type": "array"
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testRepeatedSimpleField(self):

    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    description='Testing repeated simple field params')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(IdRepeatedField, message_types.VoidMessage,
                         path='toplevel', http_method='POST')
      def toplevel(self, unused_request):
        """Testing a repeated simple field body param."""
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Testing repeated simple field params',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'definitions': {
            ID_REPEATED_FIELD: {
                'properties': {
                    'id_values': {
                        'items': {
                            'format': 'int32',
                            'type': 'integer'
                        },
                        'type': 'array'
                    }
                },
                'type': 'object'
            },
        },
        'paths': {
            '/root/v1/toplevel': {
                'post': {
                    'operationId': 'MyService_toplevel',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(ID_REPEATED_FIELD)
                            }
                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testRepeatedMessage(self):

    @api_config.api(name='root', hostname='example.appspot.com', version='v1',
                    description='Testing repeated Message params')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(NestedRepeatedMessage, message_types.VoidMessage,
                         path='toplevel', http_method='POST')
      def toplevel(self, unused_request):
        """Testing a repeated Message body param."""
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Testing repeated Message params',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'definitions': {
            'OpenApiGeneratorTestNested': {
                'properties': {
                    'int_value': {
                        'format': 'int64',
                        'type': 'string'
                    },
                    'string_value': {
                        'type': 'string'
                    }
                },
                'type': 'object'
            },
            "OpenApiGeneratorTestNestedRepeatedMessage": {
                "properties": {
                    "message_field_value": {
                        "description": "Message class to be used in a message field.",
                        "items": {
                            "$ref": self._def_path(NESTED)
                        },
                        "type": "array"
                    },
                },
                'type': 'object'
            },
        },
        'paths': {
            '/root/v1/toplevel': {
                'post': {
                    'operationId': 'MyService_toplevel',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(NESTED_REPEATED_MESSAGE)
                            }
                        }

                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)


class DevServerOpenApiGeneratorTest(BaseOpenApiGeneratorTest,
                                    test_util.DevServerTest):

  def setUp(self):
    super(DevServerOpenApiGeneratorTest, self).setUp()
    self.env_key, self.orig_env_value = (test_util.DevServerTest.
                                         setUpDevServerEnv())
    self.addCleanup(test_util.DevServerTest.restoreEnv,
                    self.env_key, self.orig_env_value)

  def testDevServerOpenApi(self):

    @api_config.api(name='root', hostname='example.appspot.com', version='v1')
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage, message_types.VoidMessage,
                         path='noop', http_method='GET', name='noop')
      def noop_get(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['http'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/noop': {
                'get': {
                    'operationId': 'MyService_noopGet',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                },
            },
        },
        'securityDefinitions': {
            'google_id_token': {
                'authorizationUrl': '',
                'flow': 'implicit',
                'type': 'oauth2',
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)


ISSUERS = {
    'auth0': api_config.Issuer(
        'https://test.auth0.com/authorize',
        'https://test.auth0.com/.wellknown/jwks.json')
}

class ThirdPartyAuthTest(BaseOpenApiGeneratorTest):

  def testAllFieldTypesPost(self):

    @api_config.api(name='root', hostname='example.appspot.com',
                    version='v1', issuers=ISSUERS, audiences={'auth0': ['auth0audapi']})
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(AllFields, message_types.VoidMessage, path='entries',
                         http_method='POST', name='entries')
      def entries_post(self, unused_request):
        return message_types.VoidMessage()
      @api_config.method(AllFields, message_types.VoidMessage, path='entries3',
                         http_method='POST', name='entries3', audiences={'auth0': ['auth0audmethod']})
      def entries_post_audience(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/entries': {
                'post': {
                    'operationId': 'MyService_entriesPost',
                    'parameters': [
                        {
                            'name': 'body',
                            'in': 'body',
                            'schema': {
                                '$ref': self._def_path(ALL_FIELDS)
                            },
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                    "security": [
                        {
                            "auth0-1af981e8": []
                        }
                    ],
                },
            },
            "/root/v1/entries3": {
                "post": {
                    "operationId": "MyService_entriesPostAudience",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "$ref": "#/definitions/OpenApiGeneratorTestAllFields"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A successful response"
                        }
                    },
                    "security": [
                        {
                            "auth0-67eeef35": []
                        }
                    ],
                }
            },
        },
        'definitions': {
            ALL_FIELDS: {
                'type': 'object',
                'properties': {
                    'bool_value': {
                        'type': 'boolean',
                    },
                    'bytes_value': {
                        'type': 'string',
                        'format': 'byte',
                    },
                    'datetime_value': {
                        'type': 'string',
                        'format': 'date-time',
                    },
                    'double_value': {
                        'type': 'number',
                        'format': 'double',
                    },
                    'enum_value': {
                        'type': 'string',
                        'enum': [
                            'VAL1',
                            'VAL2',
                        ],
                    },
                    'float_value': {
                        'type': 'number',
                        'format': 'float',
                    },
                    'int32_value': {
                        'type': 'integer',
                        'format': 'int32',
                    },
                    'int64_value': {
                        'type': 'string',
                        'format': 'int64',
                    },
                    'message_field_value': {
                        '$ref': self._def_path(NESTED),
                        'description':
                            'Message class to be used in a message field.',
                    },
                    'sint32_value': {
                        'type': 'integer',
                        'format': 'int32',
                    },
                    'sint64_value': {
                        'type': 'string',
                        'format': 'int64',
                    },
                    'string_value': {
                        'type': 'string',
                    },
                    'uint32_value': {
                        'type': 'integer',
                        'format': 'uint32',
                    },
                    'uint64_value': {
                        'type': 'string',
                        'format': 'uint64',
                    },
                },
            },
            "OpenApiGeneratorTestNested": {
                "type": "object",
                "properties": {
                    "int_value": {
                        "format": "int64",
                        "type": "string"
                    },
                    "string_value": {
                        "type": "string"
                    },
                },
            },
        },
        "securityDefinitions": {
            "auth0": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "https://test.auth0.com/authorize",
                "x-google-jwks_uri": "https://test.auth0.com/.wellknown/jwks.json",
            },
            "auth0-1af981e8": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-audiences": "auth0audapi",
                "x-google-issuer": "https://test.auth0.com/authorize",
                "x-google-jwks_uri": "https://test.auth0.com/.wellknown/jwks.json",
            },
            "auth0-67eeef35": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-audiences": "auth0audmethod",
                "x-google-issuer": "https://test.auth0.com/authorize",
                "x-google-jwks_uri": "https://test.auth0.com/.wellknown/jwks.json",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)


MULTI_ISSUERS = {
    'google_id_token': api_config.Issuer(
        'https://accounts.google.com',
        'https://www.googleapis.com/oauth2/v3/certs'),
    'auth0': api_config.Issuer(
        'https://test.auth0.com/authorize',
        'https://test.auth0.com/.wellknown/jwks.json')
}


class MultiIssuerAuthTest(BaseOpenApiGeneratorTest):

  def testMultiIssuers(self):

    @api_config.api(name='root', hostname='example.appspot.com',
                    version='v1', issuers=MULTI_ISSUERS)
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage,
                         message_types.VoidMessage, path='entries',
                         http_method='POST', name='entries',
                         audiences={'auth0': ['one'], 'google_id_token': ['two']})
      def entries_post(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/entries': {
                'post': {
                    'operationId': 'MyService_entriesPost',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                    "security": [
                        {
                            "auth0-f97c5d29": []
                        },
                        {
                            "google_id_token-b8a9f715": []
                        },
                    ],
                },
            },
        },
        "securityDefinitions": {
            "auth0": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "https://test.auth0.com/authorize",
                "x-google-jwks_uri": "https://test.auth0.com/.wellknown/jwks.json",
            },
            "auth0-f97c5d29": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-audiences": "one",
                "x-google-issuer": "https://test.auth0.com/authorize",
                "x-google-jwks_uri": "https://test.auth0.com/.wellknown/jwks.json",
            },
            "google_id_token": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
            "google_id_token-b8a9f715": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-audiences": "two",
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)

  def testMultiIssuersWithApiKey(self):

    @api_config.api(name='root', hostname='example.appspot.com',
                    version='v1', issuers=MULTI_ISSUERS)
    class MyService(remote.Service):
      """Describes MyService."""

      @api_config.method(message_types.VoidMessage,
                         message_types.VoidMessage, path='entries',
                         http_method='POST', name='entries',
                         api_key_required=True,
                         audiences={'auth0': ['one'], 'google_id_token': ['two']})
      def entries_post(self, unused_request):
        return message_types.VoidMessage()

    api = json.loads(self.generator.pretty_print_config_to_json(MyService))

    expected_openapi = {
        'swagger': '2.0',
        'info': {
            'title': 'root',
            'description': 'Describes MyService.',
            'version': 'v1',
        },
        'host': 'example.appspot.com',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'schemes': ['https'],
        'basePath': '/_ah/api',
        'paths': {
            '/root/v1/entries': {
                'post': {
                    'operationId': 'MyService_entriesPost',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'A successful response',
                        },
                    },
                    "security": [
                        {
                            "api_key": [],
                            "auth0-f97c5d29": []
                        },
                        {
                            "api_key": [],
                            "google_id_token-b8a9f715": []
                        },
                    ],
                },
            },
        },
        "securityDefinitions": {
            "api_key": {
                "type": "apiKey",
                "name": "key",
                "in": "query",
            },
            "auth0": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "https://test.auth0.com/authorize",
                "x-google-jwks_uri": "https://test.auth0.com/.wellknown/jwks.json",
            },
            "auth0-f97c5d29": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-audiences": "one",
                "x-google-issuer": "https://test.auth0.com/authorize",
                "x-google-jwks_uri": "https://test.auth0.com/.wellknown/jwks.json",
            },
            "google_id_token": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
            "google_id_token-b8a9f715": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-audiences": "two",
                "x-google-issuer": "https://accounts.google.com",
                "x-google-jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            },
        },
    }

    test_util.AssertDictEqual(expected_openapi, api, self)


if __name__ == '__main__':
  unittest.main()
