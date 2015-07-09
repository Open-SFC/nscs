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
from nscs.crdserver.openstack.common import log as logging
from nscs.crdserver.openstack.common import context
from nscs.crdserver import context as crd_context
from nscs.crdserver.openstack.common import rpc
from nscs.crdserver.openstack.common.rpc import dispatcher
from nscs.crdserver.openstack.common.rpc import proxy

import re
import socket
import time

LOG = logging.getLogger(__name__)

class DummyDispatcher(proxy.RpcProxy):
    """
    Handling Sending Notification to OF COntroller CRD Cosumer
    """
    RPC_API_VERSION = '1.0'
    
    def send_fanout(self,context,method,payload):
        LOG.info(_("Payload in Send Fanout %s\n"), payload)
        self.consumer_topic = "crd-consumer"
        self.fanout_cast(context,self.make_msg(method,payload=payload),self.consumer_topic,version=self.RPC_API_VERSION)
        
    
