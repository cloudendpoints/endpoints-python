# Copyright 2016 Google Inc. All Rights Reserved.
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

"""API serving config collection service implementation.
"""

# pylint: disable=g-statement-before-imports,g-import-not-at-top
from __future__ import absolute_import

import logging

from . import api_exceptions

from protorpc import message_types

__all__ = [
    'ApiConfigRegistry',
]


class ApiConfigRegistry(object):
  """Registry of active APIs"""

  def __init__(self):
    # Set of API classes that have been registered.
    self.__registered_classes = set()
    # Set of API config contents served by this App Engine AppId/version
    self.__api_configs = []
    # Map of API method name to ProtoRPC method name.
    self.__api_methods = {}

  # pylint: disable=g-bad-name
  def register_backend(self, config_contents):
    """Register a single API and its config contents.

    Args:
      config_contents: Dict containing API configuration.
    """
    if config_contents is None:
      return
    self.__register_class(config_contents)
    self.__api_configs.append(config_contents)
    self.__register_methods(config_contents)

  def __register_class(self, parsed_config):
    """Register the class implementing this config, so we only add it once.

    Args:
      parsed_config: The JSON object with the API configuration being added.

    Raises:
      ApiConfigurationError: If the class has already been registered.
    """
    methods = parsed_config.get('methods')
    if not methods:
      return

    # Determine the name of the class that implements this configuration.
    service_classes = set()
    for method in methods.itervalues():
      rosy_method = method.get('rosyMethod')
      if rosy_method and '.' in rosy_method:
        method_class = rosy_method.split('.', 1)[0]
        service_classes.add(method_class)

    for service_class in service_classes:
      if service_class in self.__registered_classes:
        raise api_exceptions.ApiConfigurationError(
            'API class %s has already been registered.' % service_class)
      self.__registered_classes.add(service_class)

  def __register_methods(self, parsed_config):
    """Register all methods from the given api config file.

    Methods are stored in a map from method_name to rosyMethod,
    the name of the ProtoRPC method to be called on the backend.
    If no rosyMethod was specified the value will be None.

    Args:
      parsed_config: The JSON object with the API configuration being added.
    """
    methods = parsed_config.get('methods')
    if not methods:
      return

    for method_name, method in methods.iteritems():
      self.__api_methods[method_name] = method.get('rosyMethod')

  def lookup_api_method(self, api_method_name):
    """Looks an API method up by name to find the backend method to call.

    Args:
      api_method_name: Name of the method in the API that was called.

    Returns:
      Name of the ProtoRPC method called on the backend, or None if not found.
    """
    return self.__api_methods.get(api_method_name)

  def all_api_configs(self):
    """Return a list of all API configration specs as registered above."""
    return self.__api_configs
