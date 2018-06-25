# Copyright 2018 Google Inc. All Rights Reserved.
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

"""Test various discovery docs"""

import json
import os.path
import urllib

import endpoints
import pytest
import webtest
from endpoints import discovery_generator
from endpoints import message_types
from endpoints import messages
from endpoints import remote


def make_collection(cls):
    return type(
        'Collection_{}'.format(cls.__name__),
        (messages.Message,),
        {
            'items': messages.MessageField(cls, 1, repeated=True),
            'nextPageToken': messages.StringField(2)
        })

def load_expected_document(filename):
    try:
        pwd = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(pwd, 'testdata', 'discovery', filename)
        with open(test_file) as f:
            return json.loads(f.read())
    except IOError as e:
        print 'Could not find expected output file ' + test_file
        raise e


class Foo(messages.Message):
    name = messages.StringField(1)
    value = messages.IntegerField(2, variant=messages.Variant.INT32)

FooCollection = make_collection(Foo)
FooResource = endpoints.ResourceContainer(
    Foo,
    id=messages.StringField(1, required=True),
)
FooIdResource = endpoints.ResourceContainer(
    message_types.VoidMessage,
    id=messages.StringField(1, required=True),
)
FooNResource = endpoints.ResourceContainer(
    message_types.VoidMessage,
    n = messages.IntegerField(1, required=True, variant=messages.Variant.INT32),
)

@endpoints.api(
    name='foo', version='v1', audiences=['audiences'],
    title='The Foo API', description='Just Foo Things',
    documentation='https://example.com', canonical_name='CanonicalName')
class FooEndpoint(remote.Service):
    @endpoints.method(FooResource, Foo, name='foo.create', path='foos/{id}', http_method='PUT')
    def createFoo(self, request):
        pass
    @endpoints.method(FooIdResource, Foo, name='foo.get', path='foos/{id}', http_method='GET')
    def getFoo(self, request):
        pass
    @endpoints.method(FooResource, Foo, name='foo.update', path='foos/{id}', http_method='POST')
    def updateFoo(self, request):
        pass
    @endpoints.method(FooIdResource, Foo, name='foo.delete', path='foos/{id}', http_method='DELETE')
    def deleteFoo(self, request):
        pass
    @endpoints.method(FooNResource, FooCollection, name='foo.list', path='foos', http_method='GET')
    def listFoos(self, request):
        pass
    @endpoints.method(message_types.VoidMessage, FooCollection, name='toplevel', path='foos', http_method='POST')
    def toplevel(self, request):
        pass


class Bar(messages.Message):
    name = messages.StringField(1, default='Jimothy')
    value = messages.IntegerField(2, default=42, variant=messages.Variant.INT32)
    active = messages.BooleanField(3, default=True)

BarCollection = make_collection(Bar)
BarResource = endpoints.ResourceContainer(
    Bar,
    id=messages.StringField(1, required=True),
)
BarIdResource = endpoints.ResourceContainer(
    message_types.VoidMessage,
    id=messages.StringField(1, required=True),
)
BarNResource = endpoints.ResourceContainer(
    message_types.VoidMessage,
    n = messages.IntegerField(1, required=True, variant=messages.Variant.INT32),
)

@endpoints.api(name='bar', version='v1')
class BarEndpoint(remote.Service):
    @endpoints.method(BarResource, Bar, name='bar.create', path='bars/{id}', http_method='PUT')
    def createBar(self, request):
        pass
    @endpoints.method(BarIdResource, Bar, name='bar.get', path='bars/{id}', http_method='GET')
    def getBar(self, request):
        pass
    @endpoints.method(BarResource, Bar, name='bar.update', path='bars/{id}', http_method='POST')
    def updateBar(self, request):
        pass
    @endpoints.method(BarIdResource, Bar, name='bar.delete', path='bars/{id}', http_method='DELETE')
    def deleteBar(self, request):
        pass
    @endpoints.method(BarNResource, BarCollection, name='bar.list', path='bars', http_method='GET')
    def listBars(self, request):
        pass


@endpoints.api(name='multipleparam', version='v1')
class MultipleParameterEndpoint(remote.Service):
    @endpoints.method(endpoints.ResourceContainer(
        message_types.VoidMessage,
        parent = messages.StringField(1, required=True),
        query = messages.StringField(2, required=False),
        child = messages.StringField(3, required=True),
        queryb = messages.StringField(4, required=True),
        querya = messages.StringField(5, required=True),
    ), message_types.VoidMessage, name='param', path='param/{parent}/{child}')
    def param(self, request):
        pass

@pytest.mark.parametrize('endpoint, json_filename', [
    (FooEndpoint, 'foo_endpoint.json'),
    (BarEndpoint, 'bar_endpoint.json'),
    (MultipleParameterEndpoint, 'multiple_parameter_endpoint.json'),
])
def test_discovery(endpoint, json_filename):
    generator = discovery_generator.DiscoveryGenerator()
    # JSON roundtrip so we get consistent string types
    actual = json.loads(generator.pretty_print_config_to_json(
        [endpoint], hostname='discovery-test.appspot.com'))
    expected = load_expected_document(json_filename)
    assert actual == expected
