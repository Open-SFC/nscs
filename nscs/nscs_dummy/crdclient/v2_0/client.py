# Copyright 2013 Freescale Semiconductor, Inc.
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

import logging
from nscs.crdclient.v2_0 import client as crd_client

_logger = logging.getLogger(__name__)

class Client(object):
    """
    Dummy related Client Functions in CRD
    """
    ##Firewall URLs
    dummys_path = "/dummys"
    dummy_path =  "/dummys/%s"
    
    ################################################################
    ##              Dummy Management                   ##
    ################################################################
    @crd_client.APIParamsCall
    def create_dummy(self, body=None):
        """
        create Dummy record
        """
        return self.crdclient.post(self.dummys_path,body=body)

    @crd_client.APIParamsCall
    def list_dummys(self, retrieve_all=True, **_params):
        """
        Fetches a list of all dummys
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.dummys_path,params = _params)

    @crd_client.APIParamsCall
    def update_dummy(self, dummy, body=None):
        """
        Updates Dummy record
        """
        return self.crdclient.put(self.dummy_path % (dummy), body=body)

    @crd_client.APIParamsCall
    def show_dummy(self, dummy, body=None):
        """
        Display a dummy record
        """
        return self.crdclient.get(self.dummy_path % (dummy), body=body)

    @crd_client.APIParamsCall
    def delete_dummy(self, dummy, body=None):
        """
        Delete dummy
        """
        return self.crdclient.delete(self.dummy_path % (dummy), body=body)

    
    ################################## Dummy Management End####################################
        
    def __init__(self, **kwargs):
        self.crdclient = crd_client.Client(**kwargs)
        #self.crdclient.EXTED_PLURALS.update(self.FW_EXTED_PLURALS)
        self.format = 'json'
    
