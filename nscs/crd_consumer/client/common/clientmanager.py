# Copyright 2012 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""Manage access to the clients, including authenticating when needed.
"""

import logging

from nscs.crd_consumer.client.ocas_client import HTTPClient
from nscs.crd_consumer.client.common import rm_exceptions as exc
from nscs.crd_consumer.client.sdnofcfg import client as rm_client


LOG = logging.getLogger(__name__)


class ClientCache(object):
    """Descriptor class for caching created client handles.
    """

    def __init__(self, factory):
        self.factory = factory
        self._handle = None

    def __get__(self, instance, owner):
        # Tell the ClientManager to login to keystone
        if self._handle is None:
            self._handle = self.factory(instance)
        return self._handle


class ClientManager(object):
    """Manages access to API clients, including authentication.
    """
    rm = ClientCache(rm_client.make_client)
    
    def __init__(self,
                 api_version=None,
                 url=None,
                 app_name=None
                 ):
        self._api_version = api_version
        self._url = url
        self._app_name = app_name
        return

    def initialize(self):
        if not self._url:
            httpclient = HTTPClient()
