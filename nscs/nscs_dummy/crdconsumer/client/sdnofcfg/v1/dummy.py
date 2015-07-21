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

import argparse
import logging

from crd_consumer.client.common import utils
from crd_consumer.client.sdnofcfg.v1 import CreateCommand
from crd_consumer.client.sdnofcfg.v1 import DeleteCommand
from crd_consumer.client.sdnofcfg.v1 import ListCommand
from crd_consumer.client.sdnofcfg.v1 import ShowCommand
from crd_consumer.client.sdnofcfg.v1 import UpdateCommand


class ListDummy(ListCommand):
    """List Dummys that belong to a given tenant."""
    resource = 'dummy'
    log = logging.getLogger(__name__ + '.ListDummy')
    list_columns = ['id', 'name', 'tenant_id']
    pagination_support = True
    sorting_support = True
    
class CreateDummy(CreateCommand):
    """Create a Dummy for a given tenant."""

    resource = 'dummy'
    log = logging.getLogger(__name__ + '.CreateDummy')

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Network to create')
        
    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.state.lower() == 'true':
            state = True
        else:
            state = False
        body = {'dummy':
                {
                    'name': parsed_args.name,
                }
            }
        if parsed_args.tenant_id:
            body['dummy'].update({'tenant' : parsed_args.tenant_id})

        return body
    
class DeleteDummy(DeleteCommand):
    """Delete Dummy information."""

    log = logging.getLogger(__name__ + '.DeleteDummy')
    resource = 'dummy'
    
class ShowDummy(ShowCommand):
    """Show information of a given CRM Dummy."""

    resource = 'dummy'
    log = logging.getLogger(__name__ + '.ShowDummy')
    
class UpdateDummy(UpdateCommand):
    """Update Dummy information."""

    log = logging.getLogger(__name__ + '.UpdateDummy')
    resource = 'dummy'