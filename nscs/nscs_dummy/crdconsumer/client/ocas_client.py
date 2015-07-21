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

import logging
from crd_consumer.client import ocas_client

_logger = logging.getLogger(__name__)

class Client(object):
    """
    Dummy related OCAS Client Functions in CRD Consumer 
    """
    
    def __init__(self, **kwargs):
        self.ocasclient = ocas_client.Client(**kwargs)
        #self.crdclient.EXTED_PLURALS.update(self.FW_EXTED_PLURALS)
        self.format = 'json'
        url = self.ocasclient.url
        dummys = 'dummy'
        
        #Dummy URLs
        self.dummys_path = "%s/%s" % (url, dummys)
        self.dummy_path = "%s/%s" % (url, dummys) + "/%s"
    
    def create_dummy(self, body=None):
        """
        Creates a new Dummy
        """
        return self.ocasclient.post(self.dummys_path, body=body)
        
    def delete_dummy(self, dummy):
        """
        Deletes the specified dummy
        """
        return self.ocasclient.delete(self.dummy_path % (dummy))
        
    def update_dummy(self, dummy, body=None):
        """
        Updates the specified Dummy
        """
        return self.ocasclient.put(self.dummy_path % (dummy), body=body)
        
    def list_dummys(self, **_params):
        """
        Fetches a list of all Dummys
        """
        return self.ocasclient.list('dummys', self.dummys_path, True, **_params)
        
    def show_dummy(self, dummy, **_params):
        """
        Fetches information of a Dummy
        """
        return self.ocasclient.get(self.dummy_path % (dummy), params=_params)