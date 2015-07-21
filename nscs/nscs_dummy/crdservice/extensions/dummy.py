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
from nscs.crdservice.api import extensions
from nscs.crdservice.api.v2 import base
from nscs.crdservice import manager
LOG = logging.getLogger(__name__)

#RESOURCE_NAME = "dummy"
#COLLECTION_NAME = "%ss" % RESOURCE_NAME

DUMMY_PLURALS = {
    'dummys': 'dummy',
}

# Attribute Map for dummy resource
RESOURCE_ATTRIBUTE_MAP = {
    'dummys': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True,
                      'is_visible': True},
    }
}


class Dummy(object):

    @classmethod
    def get_name(cls):
        return "dummy"

    @classmethod
    def get_alias(cls):
        return "dummy"

    @classmethod
    def get_description(cls):
        return "Dummy stuff"

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/crd/dummy/api/v1.0"

    @classmethod
    def get_updated(cls):
        return "2012-11-20T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        resources = []
        plugin = manager.CrdManager.get_plugin()
        for collection_name in RESOURCE_ATTRIBUTE_MAP:
            resource_name = DUMMY_PLURALS[collection_name]
            parents = None
            path_prefix=""
            parent = None
            if RESOURCE_ATTRIBUTE_MAP[collection_name].has_key('parameters'):
                params = RESOURCE_ATTRIBUTE_MAP[collection_name].get('parameters')
                parent = RESOURCE_ATTRIBUTE_MAP[collection_name].get('parent')
                parents = []
                path_prefix=[]
                def generate_parent(parent_attr):
                    parents.append(parent_attr)
                    if parent_attr != parent:
                        path_prefix.insert(0,"/%s/{%s_id}" % (parent_attr['collection_name'],parent_attr['member_name']))
                    if RESOURCE_ATTRIBUTE_MAP[parent_attr['collection_name']].has_key('parent'):
                        generate_parent(RESOURCE_ATTRIBUTE_MAP[parent_attr['collection_name']].get('parent'))
                generate_parent(parent)
                path_prefix= ''.join(path_prefix)
            else :
                params = RESOURCE_ATTRIBUTE_MAP[collection_name]

            member_actions = {}
            controller = base.create_resource(collection_name,
                                              resource_name,
                                              plugin, params,
                                              member_actions=member_actions,
                                              parent=parents)

            resource = extensions.ResourceExtension(
                collection_name,
                controller,
                parent=parent,
                path_prefix=path_prefix,
                member_actions=member_actions,
                attr_map=params)
            resources.append(resource)

        return resources
    #def get_resources(cls):
    #    """Returns Extended Resource for dummy management."""
    #    dummy_inst = manager.CrdManager.get_plugin()
    #    controller = base.create_resource(
    #        COLLECTION_NAME, RESOURCE_NAME, dummy_inst,
    #        RESOURCE_ATTRIBUTE_MAP[COLLECTION_NAME])
    #    return [extensions.ResourceExtension(COLLECTION_NAME,
    #                                         controller)]