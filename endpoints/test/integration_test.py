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

"""Tests against fully-constructed apps"""

import pytest
import webtest
import urllib

import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote


class FileResponse(messages.Message):
    path = messages.StringField(1)
    payload = messages.StringField(2)

FILE_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    path=messages.StringField(1)
)

FILES = {
    u'/': u'4aa7fda4-8853-4946-946e-aab5dada1152',
    u'foo': u'719eeb0a-de5e-4f17-8ab0-1567974d75c1',
    u'foo/bar': u'da6e0dfe-8c74-4a46-9696-b08b58e03e79',
    u'foo/bar/baz/': u'2543e3cf-0ae1-4278-9a76-8d1e2ee90de7',
    u'/hello': u'80e3d7ee-d289-4aa7-b0ef-eb3a8232f33f',
}

def _quote_slash(part):
    return urllib.quote(part, safe='')

def _make_app(api_use, method_use):
    @endpoints.api(name='filefetcher', version='1.0.0', use_request_uri=api_use)
    class FileFetcherApi(remote.Service):
        @endpoints.method(FILE_RESOURCE, FileResponse, path='get_file/{path}',
                          http_method='GET', name='get_file', use_request_uri=method_use)
        def get_file(self, request):
            if request.path not in FILES:
                raise endpoints.NotFoundException()
            val = FileResponse(path=request.path, payload=FILES[request.path])
            return val
    return webtest.TestApp(endpoints.api_server([FileFetcherApi]), lint=False)

def _make_request(app, url, expect_status):
    kwargs = {}
    if expect_status:
        kwargs['status'] = expect_status
    return app.get(url, extra_environ={'REQUEST_URI': url}, **kwargs)


@pytest.mark.parametrize('api_use,method_use,expect_404', [
    (True, True, False),
    (True, False, True),
    (False, True, False),
    (False, False, True),
])
class TestSlashVariable(object):
    def test_missing_file(self, api_use, method_use, expect_404):
        app = _make_app(api_use, method_use)
        url = '/_ah/api/filefetcher/v1/get_file/missing'
        # This _should_ return 404, but https://github.com/cloudendpoints/endpoints-python/issues/138
        # the other methods actually return 404 because protorpc doesn't rewrite it there
        _make_request(app, url, expect_status=400)

    def test_no_slash(self, api_use, method_use, expect_404):
        app = _make_app(api_use, method_use)
        url = '/_ah/api/filefetcher/v1/get_file/foo'
        _make_request(app, url, expect_status=None)

    def test_mid_slash(self, api_use, method_use, expect_404):
        app = _make_app(api_use, method_use)
        url = '/_ah/api/filefetcher/v1/get_file/{}'.format(_quote_slash('foo/bar'))
        actual = _make_request(app, url, expect_status=404 if expect_404 else 200)
        if not expect_404:
            expected = {'path': 'foo/bar', 'payload': 'da6e0dfe-8c74-4a46-9696-b08b58e03e79'}
            assert actual.json == expected

    def test_ending_slash(self, api_use, method_use, expect_404):
        app = _make_app(api_use, method_use)
        url = '/_ah/api/filefetcher/v1/get_file/{}'.format(_quote_slash('foo/bar/baz/'))
        actual = _make_request(app, url, expect_status=404 if expect_404 else 200)
        if not expect_404:
            expected = {'path': 'foo/bar/baz/', 'payload': '2543e3cf-0ae1-4278-9a76-8d1e2ee90de7'}
            assert actual.json == expected

    def test_beginning_slash(self, api_use, method_use, expect_404):
        app = _make_app(api_use, method_use)
        url = '/_ah/api/filefetcher/v1/get_file/{}'.format(_quote_slash('/hello'))
        actual = _make_request(app, url, expect_status=404 if expect_404 else 200)
        if not expect_404:
            expected = {'path': '/hello', 'payload': '80e3d7ee-d289-4aa7-b0ef-eb3a8232f33f'}
            assert actual.json == expected
