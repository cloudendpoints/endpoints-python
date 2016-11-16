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
import unittest

import endpoints.api_config as api_config

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

    # Some constants to shorten line length in expected Swagger output
    prefix = 'SwaggerGeneratorTest'
    boolean_response = prefix + 'BooleanMessageResponse'
    all_fields = prefix + 'AllFields'
    nested = prefix + 'Nested'
    entry_publish_request = prefix + 'EntryPublishRequest'
    publish_request_for_container = prefix + 'EntryPublishRequestForContainer'
    items_put_request = prefix + 'ItemsPutRequest'
    put_request_for_container = prefix + 'ItemsPutRequestForContainer'
    put_request = prefix + 'PutRequest'

    expected_discovery = {
        'kind': 'discovery#restDescription',
        'discoveryVersion': 'v1',
        'id': 'root:v1',
        'name': 'root',
        'version': 'v1',
        'description': 'This is an API',
        'icons': {
            'x16': 'http://www.google.com/images/icons/product/search-16.gif',
            'x32': 'http://www.google.com/images/icons/product/search-32.gif'
        },
        'protocol': 'rest',
        'baseUrl': 'https://example.appspot.com/_ah/api/root/v1/',
        'basePath': '/_ah/api/root/v1/',
        'rootUrl': 'https://example.appspot.com/_ah/api/',
        'servicePath': 'root/v1/',
        'batchPath': 'batch',
        'parameters': {
            'alt': {
                'type': 'string',
                'description': 'Data format for the response.',
                'default': 'json',
                'enum': [
                    'json'
                ],
                'enumDescriptions': [
                    'Responses with Content-Type of application/json'
                ],
                'location': 'query'
            },
            'fields': {
                'type': 'string',
                'description': 'Selector specifying which fields to include in '
                               'a partial response.',
                'location': 'query'
            },
            'key': {
                'type': 'string',
                'description': 'API key. Your API key identifies your project '
                               'and provides you with API access, quota, and '
                               'reports. Required unless you provide an '
                               'OAuth 2.0 token.',
                'location': 'query'
            },
            'oauth_token': {
                'type': 'string',
                'description': 'OAuth 2.0 token for the current user.',
                'location': 'query'
            },
            'prettyPrint': {
                'type': 'boolean',
                'description': 'Returns response with indentations and line '
                               'breaks.',
                'default': 'true',
                'location': 'query'
            },
            'quotaUser': {
                'type': 'string',
                'description': 'Available to use for quota purposes for '
                               'server-side applications. Can be any arbitrary '
                               'string assigned to a user, but should not '
                               'exceed 40 characters. Overrides userIp if both '
                               'are provided.',
                'location': 'query'
            },
            'userIp': {
                'type': 'string',
                'description': 'IP address of the site where the request '
                               'originates. Use this if you want to enforce '
                               'per-user limits.',
                'location': 'query'
            }
        },
        'auth': {
            'oauth2': {
                'scopes': {
                    'https://www.googleapis.com/auth/userinfo.email': {
                        'description': 'View your email address'
                    }
                }
            }
        },
        'schemas': {
          'DiscoveryGeneratorTestAllFields': {
           'id': 'DiscoveryGeneratorTestAllFields',
           'type': 'object',
           'description': 'Contains all field types.',
           'properties': {
            'bool_value': {
             'type': 'boolean'
            },
            'bytes_value': {
             'type': 'string',
             'format': 'byte'
            },
            'datetime_value': {
             'type': 'string',
             'format': 'date-time'
            },
            'double_value': {
             'type': 'number',
             'format': 'double'
            },
            'enum_value': {
             'type': 'string',
             'enum': [
              'VAL1',
              'VAL2'
             ],
             'enumDescriptions': [
              '',
              ''
             ]
            },
            'float_value': {
             'type': 'number',
             'format': 'float'
            },
            'int32_value': {
             'type': 'integer',
             'format': 'int32'
            },
            'int64_value': {
             'type': 'string',
             'format': 'int64'
            },
            'message_field_value': {
             '$ref': 'DiscoveryGeneratorTestNested',
             'description': 'Message class to be used in a message field.'
            },
            'sint32_value': {
             'type': 'integer',
             'format': 'int32'
            },
            'sint64_value': {
             'type': 'string',
             'format': 'int64'
            },
            'string_value': {
             'type': 'string'
            },
            'uint32_value': {
             'type': 'integer',
             'format': 'uint32'
            },
            'uint64_value': {
             'type': 'string',
             'format': 'uint64'
            }
           }
          },
          'DiscoveryGeneratorTestBooleanMessageResponse': {
           'id': 'DiscoveryGeneratorTestBooleanMessageResponse',
           'type': 'object',
           'properties': {
            'result': {
             'type': 'boolean'
            }
           }
          },
          'DiscoveryGeneratorTestEntryPublishRequest': {
           'id': 'DiscoveryGeneratorTestEntryPublishRequest',
           'type': 'object',
           'description': 'Message with two required params, one in path, one in body.',
           'properties': {
            'entryId': {
             'type': 'string'
            },
            'title': {
             'type': 'string'
            }
           }
          },
          'DiscoveryGeneratorTestEntryPublishRequestForContainer': {
           'id': 'DiscoveryGeneratorTestEntryPublishRequestForContainer',
           'type': 'object',
           'description': 'Message with two required params, one in path, one in body.',
           'properties': {
            'title': {
             'type': 'string'
            }
           }
          },
          'DiscoveryGeneratorTestItemsPutRequest': {
           'id': 'DiscoveryGeneratorTestItemsPutRequest',
           'type': 'object',
           'description': 'Message with path params and a body field.',
           'properties': {
            'body': {
             '$ref': 'DiscoveryGeneratorTestAllFields',
             'description': 'Contains all field types.'
            },
            'entryId': {
             'type': 'string'
            }
           }
          },
          'DiscoveryGeneratorTestItemsPutRequestForContainer': {
           'id': 'DiscoveryGeneratorTestItemsPutRequestForContainer',
           'type': 'object',
           'description': 'Message with path params and a body field.',
           'properties': {
            'body': {
             '$ref': 'DiscoveryGeneratorTestAllFields',
             'description': 'Contains all field types.'
            }
           }
          },
          'DiscoveryGeneratorTestNested': {
           'id': 'DiscoveryGeneratorTestNested',
           'type': 'object',
           'description': 'Message class to be used in a message field.',
           'properties': {
            'int_value': {
             'type': 'string',
             'format': 'int64'
            },
            'string_value': {
             'type': 'string'
            }
           }
          },
          'DiscoveryGeneratorTestPutRequest': {
           'id': 'DiscoveryGeneratorTestPutRequest',
           'type': 'object',
           'description': 'Message with just a body field.',
           'properties': {
            'body': {
             '$ref': 'DiscoveryGeneratorTestAllFields',
             'description': 'Contains all field types.'
            }
           }
          }
         },
         'resources': {
          'entries': {
           'methods': {
            'get': {
             'id': 'root.entries.get',
             'path': 'entries',
             'httpMethod': 'GET',
             'description': 'All field types in the query parameters.',
             'parameters': {
              'bool_value': {
               'type': 'boolean',
               'location': 'query'
              },
              'bytes_value': {
               'type': 'string',
               'format': 'byte',
               'location': 'query'
              },
              'datetime_value.milliseconds': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'datetime_value.time_zone_offset': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'double_value': {
               'type': 'number',
               'format': 'double',
               'location': 'query'
              },
              'enum_value': {
               'type': 'string',
               'enum': [
                'VAL1',
                'VAL2'
               ],
               'enumDescriptions': [
                '',
                ''
               ],
               'location': 'query'
              },
              'float_value': {
               'type': 'number',
               'format': 'float',
               'location': 'query'
              },
              'int32_value': {
               'type': 'integer',
               'format': 'int32',
               'location': 'query'
              },
              'int64_value': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'message_field_value.int_value': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'message_field_value.string_value': {
               'type': 'string',
               'location': 'query'
              },
              'sint32_value': {
               'type': 'integer',
               'format': 'int32',
               'location': 'query'
              },
              'sint64_value': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'string_value': {
               'type': 'string',
               'location': 'query'
              },
              'uint32_value': {
               'type': 'integer',
               'format': 'uint32',
               'location': 'query'
              },
              'uint64_value': {
               'type': 'string',
               'format': 'uint64',
               'location': 'query'
              }
             },
             'scopes': [
              'https://www.googleapis.com/auth/userinfo.email'
             ]
            },
            'getContainer': {
             'id': 'root.entries.getContainer',
             'path': 'entries/container',
             'httpMethod': 'GET',
             'description': 'All field types in the query parameters.',
             'parameters': {
              'bool_value': {
               'type': 'boolean',
               'location': 'query'
              },
              'bytes_value': {
               'type': 'string',
               'format': 'byte',
               'location': 'query'
              },
              'datetime_value.milliseconds': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'datetime_value.time_zone_offset': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'double_value': {
               'type': 'number',
               'format': 'double',
               'location': 'query'
              },
              'enum_value': {
               'type': 'string',
               'enum': [
                'VAL1',
                'VAL2'
               ],
               'enumDescriptions': [
                '',
                ''
               ],
               'location': 'query'
              },
              'float_value': {
               'type': 'number',
               'format': 'float',
               'location': 'query'
              },
              'int32_value': {
               'type': 'integer',
               'format': 'int32',
               'location': 'query'
              },
              'int64_value': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'message_field_value.int_value': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'message_field_value.string_value': {
               'type': 'string',
               'location': 'query'
              },
              'sint32_value': {
               'type': 'integer',
               'format': 'int32',
               'location': 'query'
              },
              'sint64_value': {
               'type': 'string',
               'format': 'int64',
               'location': 'query'
              },
              'string_value': {
               'type': 'string',
               'location': 'query'
              },
              'uint32_value': {
               'type': 'integer',
               'format': 'uint32',
               'location': 'query'
              },
              'uint64_value': {
               'type': 'string',
               'format': 'uint64',
               'location': 'query'
              }
             },
             'scopes': [
              'https://www.googleapis.com/auth/userinfo.email'
             ]
            },
            'process': {
             'id': 'root.entries.process',
             'path': 'process',
             'httpMethod': 'POST',
             'description': 'Message is the request body.',
             'request': {
              '$ref': 'DiscoveryGeneratorTestAllFields',
              'parameterName': 'resource'
             },
             'scopes': [
              'https://www.googleapis.com/auth/userinfo.email'
             ]
            },
            'publish': {
             'id': 'root.entries.publish',
             'path': 'entries/{entryId}/publish',
             'httpMethod': 'POST',
             'description': 'Path has a parameter and request body has a required param.',
             'parameters': {
              'entryId': {
               'type': 'string',
               'required': True,
               'location': 'path'
              }
             },
             'parameterOrder': [
              'entryId'
             ],
             'request': {
              '$ref': 'DiscoveryGeneratorTestEntryPublishRequest',
              'parameterName': 'resource'
             },
             'scopes': [
              'https://www.googleapis.com/auth/userinfo.email'
             ]
            },
            'publishContainer': {
             'id': 'root.entries.publishContainer',
             'path': 'entries/container/{entryId}/publish',
             'httpMethod': 'POST',
             'description': 'Path has a parameter and request body has a required param.',
             'parameters': {
              'entryId': {
               'type': 'string',
               'required': True,
               'location': 'path'
              }
             },
             'parameterOrder': [
              'entryId'
             ],
             'request': {
              '$ref': 'DiscoveryGeneratorTestEntryPublishRequestForContainer',
              'parameterName': 'resource'
             },
             'scopes': [
              'https://www.googleapis.com/auth/userinfo.email'
             ]
            },
            'put': {
             'id': 'root.entries.put',
             'path': 'entries',
             'httpMethod': 'POST',
             'description': 'Request body is in the body field.',
             'request': {
              '$ref': 'DiscoveryGeneratorTestPutRequest',
              'parameterName': 'resource'
             },
             'response': {
              '$ref': 'DiscoveryGeneratorTestBooleanMessageResponse'
             },
             'scopes': [
              'https://www.googleapis.com/auth/userinfo.email'
             ]
            },
            'roundtrip': {
             'id': 'root.entries.roundtrip',
             'path': 'roundtrip',
             'httpMethod': 'POST',
             'description': 'All field types in the request and response.',
             'request': {
              '$ref': 'DiscoveryGeneratorTestAllFields',
              'parameterName': 'resource'
             },
             'response': {
              '$ref': 'DiscoveryGeneratorTestAllFields'
             },
             'scopes': [
              'https://www.googleapis.com/auth/userinfo.email'
             ]
            }
           },
           'resources': {
            'items': {
             'methods': {
              'put': {
               'id': 'root.entries.items.put',
               'path': 'entries/{entryId}/items',
               'httpMethod': 'POST',
               'description': 'Path has a parameter and request body is in the body field.',
               'parameters': {
                'entryId': {
                 'type': 'string',
                 'required': True,
                 'location': 'path'
                }
               },
               'parameterOrder': [
                'entryId'
               ],
               'request': {
                '$ref': 'DiscoveryGeneratorTestItemsPutRequest',
                'parameterName': 'resource'
               },
               'scopes': [
                'https://www.googleapis.com/auth/userinfo.email'
               ]
              },
              'putContainer': {
               'id': 'root.entries.items.putContainer',
               'path': 'entries/container/{entryId}/items',
               'httpMethod': 'POST',
               'description': 'Path has a parameter and request body is in the body field.',
               'parameters': {
                'entryId': {
                 'type': 'string',
                 'required': True,
                 'location': 'path'
                }
               },
               'parameterOrder': [
                'entryId'
               ],
               'request': {
                '$ref': 'DiscoveryGeneratorTestItemsPutRequestForContainer',
                'parameterName': 'resource'
               },
               'scopes': [
                'https://www.googleapis.com/auth/userinfo.email'
               ]
              }
             }
            },
            'nested': {
             'resources': {
              'collection': {
               'methods': {
                'action': {
                 'id': 'root.entries.nested.collection.action',
                 'path': 'nested',
                 'httpMethod': 'POST',
                 'description': 'A VoidMessage for a request body.',
                 'scopes': [
                  'https://www.googleapis.com/auth/userinfo.email'
                 ]
                }
               }
              }
             }
            }
           }
          }
         }
    }

    test_util.AssertDictEqual(expected_discovery, api, self)


if __name__ == '__main__':
  unittest.main()
