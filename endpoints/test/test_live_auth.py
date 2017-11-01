# Copyright 2017 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tempfile
import os
import cStringIO
import zipfile
import sys
import importlib
import shutil
import base64
import subprocess

import pytest
import requests  # provided by endpoints-management-python
import yaml

JSON_HEADERS = {'content-type': 'application/json'}
TESTDIR = os.path.dirname(os.path.realpath(__file__))

def _find_setup_py(some_path):
    while not os.path.isfile(os.path.join(some_path, 'setup.py')):
        some_path = os.path.dirname(some_path)
    return some_path

PKGDIR = _find_setup_py(TESTDIR)

@pytest.fixture(scope='session')
def integration_project_id():
    if 'INTEGRATION_PROJECT_ID' not in os.environ:
        raise KeyError('INTEGRATION_PROJECT_ID required in environment. Set it to the appropriate project id.')
    return os.environ['INTEGRATION_PROJECT_ID']

@pytest.fixture(scope='session')
def service_account_keyfile():
    if 'SERVICE_ACCOUNT_KEYFILE' not in os.environ:
        raise KeyError('SERVICE_ACCOUNT_KEYFILE required in environment. Set it to the path to the service account key.')
    value = os.environ['SERVICE_ACCOUNT_KEYFILE']
    if not os.path.isfile(value):
        raise ValueError('SERVICE_ACCOUNT_KEYFILE must point to a file containing the service account key.')
    return value

@pytest.fixture(scope='session')
def api_key():
    if 'PROJECT_API_KEY' not in os.environ:
        raise KeyError('PROJECT_API_KEY required in environment. Set it to a valid api key for the specified project.')
    return os.environ['PROJECT_API_KEY']

@pytest.fixture(scope='session')
def gcloud_driver_module(request):
    """This fixture provides the gcloud test driver. It is not normally installable, since it lacks a setup.py"""
    cache_key = 'live_auth/driver_zip'
    driver_zip_data = request.config.cache.get(cache_key, None)
    if driver_zip_data is None:
        url = "https://github.com/GoogleCloudPlatform/cloudsdk-test-driver/archive/master.zip"
        driver_zip_data = requests.get(url).content
        request.config.cache.set(cache_key, base64.b64encode(driver_zip_data))
    else:
        driver_zip_data = base64.b64decode(driver_zip_data)
    extract_path = tempfile.mkdtemp()
    with zipfile.ZipFile(cStringIO.StringIO(driver_zip_data)) as driver_zip:
        driver_zip.extractall(path=extract_path)
    # have to rename the subfolder
    os.rename(os.path.join(extract_path, 'cloudsdk-test-driver-master'), os.path.join(extract_path, 'cloudsdk_test_driver'))
    sys.path.append(extract_path)
    driver_module = importlib.import_module('cloudsdk_test_driver.driver')
    yield driver_module
    sys.path.pop()
    shutil.rmtree(extract_path)

@pytest.fixture(scope='session')
def gcloud_driver(gcloud_driver_module):
    with gcloud_driver_module.Manager(additional_components=['app-engine-python']):
        yield gcloud_driver_module

@pytest.fixture(scope='session')
def gcloud_sdk(gcloud_driver, integration_project_id, service_account_keyfile):
    return gcloud_driver.SDKFromArgs(project=integration_project_id, service_account_keyfile=service_account_keyfile)

class TestAppManager(object):
    # This object will manage the test app. It needs to be told what
    # kind of app to make; such methods are named `become_*_app`,
    # because they mutate the manager object rather than returning
    # some new object.

    def __init__(self):
        self.cleanup_path = tempfile.mkdtemp()
        self.app_path = os.path.join(self.cleanup_path, 'app')

    def cleanup(self):
        shutil.rmtree(self.cleanup_path)

    def become_apikey_app(self, project_id):
        source_path = os.path.join(TESTDIR, 'testdata', 'sample_app')
        shutil.copytree(source_path, self.app_path)
        self.update_app_yaml(project_id)

    def update_app_yaml(self, project_id, version=None):
        yaml_path = os.path.join(self.app_path, 'app.yaml')
        app_yaml = yaml.load(open(yaml_path))
        env = app_yaml['env_variables']
        env['ENDPOINTS_SERVICE_NAME'] = '{}.appspot.com'.format(project_id)
        if version is not None:
            env['ENDPOINTS_SERVICE_VERSION'] = version
        with open(yaml_path, 'w') as outfile:
            yaml.dump(app_yaml, outfile, default_flow_style=False)


@pytest.fixture(scope='class')
def apikey_app(gcloud_sdk, integration_project_id):
    app = TestAppManager()
    app.become_apikey_app(integration_project_id)
    path = app.app_path
    os.mkdir(os.path.join(path, 'lib'))
    # Install the checked-out endpoints repo
    subprocess.check_call(['python', '-m', 'pip', 'install', '-t', 'lib', PKGDIR, '--ignore-installed'], cwd=path)
    print path
    subprocess.check_call(['python', 'lib/endpoints/endpointscfg.py', 'get_openapi_spec', 'main.IataApi', '--hostname', '{}.appspot.com'.format(integration_project_id)], cwd=path)
    out, err, code = gcloud_sdk.RunGcloud(['endpoints', 'services', 'deploy', os.path.join(path, 'iatav1openapi.json')])
    assert code == 0
    version = out['serviceConfig']['id'].encode('ascii')
    app.update_app_yaml(integration_project_id, version)

    out, err, code = gcloud_sdk.RunGcloud(['app', 'deploy', os.path.join(path, 'app.yaml')])
    assert code == 0

    base_url = 'https://{}.appspot.com/_ah/api/iata/v1'.format(integration_project_id)
    yield base_url
    app.cleanup()


@pytest.fixture()
def clean_apikey_app(apikey_app, api_key):
    url = '/'.join([apikey_app, 'reset'])
    r = requests.post(url, params={'key': api_key})
    assert r.status_code == 204
    return apikey_app

@pytest.mark.livetest
class TestApikeyRequirement(object):
    def test_get_airport(self, clean_apikey_app):
        url = '/'.join([clean_apikey_app, 'airport', 'YYZ'])
        r = requests.get(url, headers=JSON_HEADERS)
        actual = r.json()
        expected = {u'iata': u'YYZ', u'name': u'Lester B. Pearson International Airport'}
        assert actual == expected

    def test_list_airports(self, clean_apikey_app):
        url = '/'.join([clean_apikey_app, 'airports'])
        r = requests.get(url, headers=JSON_HEADERS)
        raw = r.json()
        assert 'airports' in raw
        actual = {a['iata']: a['name'] for a in raw['airports']}
        assert actual[u'YYZ'] == u'Lester B. Pearson International Airport'
        assert u'ZZT' not in actual

    def test_create_airport(self, clean_apikey_app, api_key):
        url = '/'.join([clean_apikey_app, 'airport'])
        r = requests.get('/'.join([url, 'ZZT']), headers=JSON_HEADERS)
        assert r.status_code == 404
        data = {u'iata': u'ZZT', u'name': u'Town Airport'}
        r = requests.post(url, json=data, params={'key': api_key})
        assert data == r.json()
        r = requests.get('/'.join([url, 'ZZT']), headers=JSON_HEADERS)
        assert r.status_code == 200
        assert data == r.json()

    def test_create_airport_key_required(self, clean_apikey_app):
        url = '/'.join([clean_apikey_app, 'airport'])
        data = {u'iata': u'ZZT', u'name': u'Town Airport'}
        r = requests.post(url, json=data)
        assert r.status_code == 401
        r = requests.get('/'.join([url, 'ZZT']), headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_modify_airport(self, clean_apikey_app, api_key):
        url = '/'.join([clean_apikey_app, 'airport', 'YYZ'])
        r = requests.get(url, headers=JSON_HEADERS)
        actual = r.json()
        expected = {u'iata': u'YYZ', u'name': u'Lester B. Pearson International Airport'}
        assert actual == expected

        data = {u'iata': u'YYZ', u'name': u'Torontoland'}
        r = requests.post(url, json=data, params={'key': api_key})
        assert data == r.json()

        r = requests.get(url, headers=JSON_HEADERS)
        assert data == r.json()

    def test_modify_airport_key_required(self, clean_apikey_app):
        url = '/'.join([clean_apikey_app, 'airport', 'YYZ'])
        data = {u'iata': u'YYZ', u'name': u'Torontoland'}
        r = requests.post(url, json=data)
        assert r.status_code == 401

        r = requests.get(url, headers=JSON_HEADERS)
        actual = r.json()
        expected = {u'iata': u'YYZ', u'name': u'Lester B. Pearson International Airport'}
        assert actual == expected

    def test_delete_airport(self, clean_apikey_app, api_key):
        url = '/'.join([clean_apikey_app, 'airport', 'YYZ'])
        r = requests.delete(url, headers=JSON_HEADERS, params={'key': api_key})
        assert r.status_code == 204

        r = requests.get(url, headers=JSON_HEADERS)
        assert r.status_code == 404

    def test_delete_airport_key_required(self, clean_apikey_app):
        url = '/'.join([clean_apikey_app, 'airport', 'YYZ'])
        r = requests.delete(url, headers=JSON_HEADERS)
        assert r.status_code == 401

        r = requests.get(url, headers=JSON_HEADERS)
        actual = r.json()
        expected = {u'iata': u'YYZ', u'name': u'Lester B. Pearson International Airport'}
        assert actual == expected
