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

from nscs.crd_consumer.client.common import utils

class DummyCommands():
    """"""
    
    COMMANDS = {
        ###Networks
        'list-dummys': utils.import_class(
            'nscs_dummy.crdconsumer.client.sdnofcfg.v1.dummy.ListDummy'),
        'create-dummy' : utils.import_class(
            'nscs_dummy.crdconsumer.client.sdnofcfg.v1.dummy.CreateDummy'),
        'delete-dummy' : utils.import_class(
            'nscs_dummy.crdconsumer.client.sdnofcfg.v1.dummy.DeleteDummy'),
        'show-dummy' : utils.import_class(
            'nscs_dummy.crdconsumer.client.sdnofcfg.v1.dummy.ShowDummy'),
        'update-dummy' : utils.import_class(
            'nscs_dummy.crdconsumer.client.sdnofcfg.v1.dummy.UpdateDummy'),
    }
