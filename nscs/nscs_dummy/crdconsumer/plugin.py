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
import time

from nscs.ocas_utils.openstack.common.gettextutils import _
from nscs.ocas_utils.openstack.common import log as logging
from nscs.nscs_dummy.crdconsumer.client import ocas_client
from nscs.ocas_utils.openstack.common import context
from nscs.ocas_utils.openstack.common.rpc import proxy

LOG = logging.getLogger(__name__)

class DummyConsumerPlugin(proxy.RpcProxy):
    """
    Implementation of the Crd Consumer Dummy Application.
    """
    RPC_API_VERSION = '1.0'
    
    def __init__(self):
        super(DummyConsumerPlugin,self).__init__(topic="crd-service-queue",default_version=self.RPC_API_VERSION)
        self.uc = ocasclient()
        self.listener_topic = 'crd-listener'
        self.consumer_context = context.RequestContext('crd', 'crd',
                                                       is_admin=False)
        
    def get_plugin_type(self):
        return "DUMMY"
    
    def init_consumer(self, consumer=None):
        delta_msg = {}
        return delta_msg
    
    def create_dummy(self, context, **kwargs):
        LOG.info(_("Create Dummy Body - %s"), str(kwargs))
        body = kwargs['payload']
        self.uc.create_dummy(body=body)
        
    def delete_dummy(self, context, **kwargs):
        payload = kwargs['payload']
        name = payload.get('id')
        LOG.info(_("Delete Dummy - %s"), str(payload))
        self.uc.delete_dummy(name)
        
    def update_dummy(self, context, **kwargs):
        payload = kwargs['payload']
        name = payload.get('id')
        body = {}
        LOG.info(_("Update Dummy - %s"), str(name))
        self.uc.update_dummy(name, body=body)
        
    def get_dummys(self, context, **params):
        LOG.info(_("List Dummys"))
        self.uc.list_dummys(**params)
        
    def get_dummy(self, payload, **params):
        name = payload.get('id')
        LOG.info(_("Show Dummy Details for - %s"), str(name))
        self.uc.show_dummy(nwname, **params)
        
def ocasclient():
    c = ocas_client.Client()
    return c
