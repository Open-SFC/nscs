# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
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

from nscs.crdservice.openstack.common import log as logging
LOG = logging.getLogger(__name__)

DUMMY_PLUGIN_NAME = "dummy_plugin"

from nscs.crdservice.common import exceptions
from nscs.crdservice.openstack.common import uuidutils
from nscs.crdservice.plugins.services import service_base
from nscs.nscs_dummy.crdservice.extensions import dummy
from nscs.nscs_dummy.crdservice.dispatcher.ofcontroller.dummy import DummyDispatcher

DUMMY_PLUGIN_NAME = "dummy_plugin"


class DummyPlugin(service_base.ServicePluginBase,
                  DummyDispatcher):
    """This is a simple plugin for managing instantes of a fictional 'dummy'
        service. This plugin is provided as a proof-of-concept of how
        advanced service might leverage the service type extension.
        Ideally, instances of real advanced services, such as load balancing
        or VPN will adopt a similar solution.
    """

    supported_extension_aliases = ['dummy']

    def __init__(self):
        self.dummys = {}

    def get_plugin_type(self):
        return "DUMMY"

    def get_plugin_name(self):
        return DUMMY_PLUGIN_NAME

    def get_plugin_description(self):
        return "CRD Dummy Service Plugin"

    def get_dummys(self, context, filters, fields):
        return self.dummys.values()

    def get_dummy(self, context, id, fields):
        try:
            return self.dummys[id]
        except KeyError:
            raise exceptions.NotFound()

    def create_dummy(self, context, dummy):
        d = dummy['dummy']
        d['id'] = uuidutils.generate_uuid()
        self.dummys[d['id']] = d
        fanoutmsg = {}
        fanoutmsg.update({'method':'create_dummy','payload':self.dummys})
        delta={}
        version = 0
        delta[version] = fanoutmsg
        self.send_fanout(context,'call_consumer',delta)
        return d

    def update_dummy(self, context, id, dummy):
        pass

    def delete_dummy(self, context, id):
        try:
            del self.dummys[id]
            
        except KeyError:
            raise exceptions.NotFound()
