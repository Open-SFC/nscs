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

import sqlalchemy as sa
from nscs.crdserver.db import model_base
from nscs.crdserver.openstack.common import log as logging
from sqlalchemy.orm import exc, relationship, backref
from nscs.crdserver.common import exceptions as q_exc
from nscs.crdserver.openstack.common import uuidutils
import datetime
LOG = logging.getLogger(__name__)


class HasTenant(object):
    """Tenant mixin, add to subclasses that have a tenant."""
    # NOTE(jkoelker) tenant_id is just a free form string ;(
    tenant_id = sa.Column(sa.String(255))


class HasId(object):
    """id mixin, add to subclasses that have an id."""
    id = sa.Column(sa.String(36), primary_key=True, default=uuidutils.generate_uuid)  

class crd_version(model_base.BASEV2):
    tenant_id = sa.Column(sa.String(36), nullable=False)
    runtime_version = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    
#class ns_networkfunction(model_base.BASEV2, HasId, HasTenant):
#    """Represents a v2 crd FSL service."""
#    name = sa.Column(sa.String(50), nullable=False)
#    description = sa.Column(sa.String(255))
#    shared = sa.Column(sa.Boolean)
    
    
###Networkfunctions table for delta
#class ns_networkfunctions_delta(model_base.BASEV2, HasId, HasTenant):
#    """Represents a v2 crd FSL service."""
#    networkfunction_id = sa.Column(sa.String(36), nullable=False)
#    name = sa.Column(sa.String(50))
#    description = sa.Column(sa.String(255))
#    shared = sa.Column(sa.Boolean)
#    operation = sa.Column(sa.String(255), nullable=False)
#    user_id = sa.Column(sa.String(36),nullable=False)
#    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
#    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
#class ns_config_handle(model_base.BASEV2, HasId, HasTenant):
#    """Represents a v2 crd FSL service."""
#    name = sa.Column(sa.String(50))
#    networkfunction_id = sa.Column(sa.String(36), sa.ForeignKey('ns_networkfunctions.id'), nullable=False) 
#    status = sa.Column(sa.Boolean)
#    slug = sa.Column(sa.String(255))
#    config_mode = sa.Column(sa.String(50))
    

#class ns_config_handles_delta(model_base.BASEV2, HasId, HasTenant):
#    """Represents a v2 crd FSL service."""
#    config_handle_id = sa.Column(sa.String(36))
#    name = sa.Column(sa.String(50))
#    networkfunction_id = sa.Column(sa.String(36)) 
#    status = sa.Column(sa.Boolean)
#    slug = sa.Column(sa.String(255))
#    operation = sa.Column(sa.String(255), nullable=False)
#    user_id = sa.Column(sa.String(36),nullable=False)
#    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
#    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
   
class NscsDb(object):
    ##########Version
    def _make_version_dict(self, version, fields=None):
        res = {'tenant_id': version['tenant_id'],
               'runtime_version': version['runtime_version']}
        return self._fields(res, fields)
        
    def create_version(self, context, tenant_id):
        with context.session.begin(subtransactions=True):
            version = crd_version(tenant_id=tenant_id)
            context.session.add(version)
            
        version_details = self._make_version_dict(version)
        version_id = version_details['runtime_version']
        return version_id
    
    def get_versions(self, context, filters=None, fields=None):
        return self._get_collection(context, crd_version,
                                    self._make_version_dict,
                                    filters=filters, fields=fields)
        
        
    #Network Function Table   
    def _make_networkfunction_dict(self, networkfunction, fields=None):
        res = {'id': networkfunction['id'],
               'name': networkfunction['name'],
               'tenant_id': networkfunction['tenant_id'],
               'description': networkfunction['description'],
               'shared': networkfunction['shared']}
        return self._fields(res, fields)
    
    def get_networkfunction(self, context, id, fields=None):
        networkfunction = self._get_networkfunction(context, id)
        return self._make_networkfunction_dict(networkfunction, fields)
        
    def get_networkfunctions(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_networkfunction,
                                    self._make_networkfunction_dict,
                                    filters=filters, fields=fields)
        
    def create_networkfunction(self, context, networkfunction):
        n = networkfunction['networkfunction']
        tenant_id = self._get_tenant_id_for_create(context, n)
               
        with context.session.begin(subtransactions=True):
            networkfunction = ns_networkfunction(tenant_id=tenant_id,
                                        id=n.get('id') or uuidutils.generate_uuid(),
                                        name=n['name'],
                                        description=n['description'],
                                        shared=n['shared'])
            context.session.add(networkfunction)
            ####  Delta Start ###########################
            data = self._make_networkfunction_dict(networkfunction)
            delta = {}
            data.update({'operation':'create'})
            delta.update({'networkfunctions_delta': data})
            self.create_networkfunctions_delta(context, delta)
            ####  Delta End ###########################
        return self._make_networkfunction_dict(networkfunction)
    
    def _get_networkfunction(self, context, id):
        try:
            networkfunction = self._get_by_id(context, ns_networkfunction, id)
        except exc.NoResultFound:
            raise q_exc.NetworkfunctionNotFound(networkfunction_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Networkfunctions match for %s' % id)
            raise q_exc.NetworkfunctionNotFound(networkfunction_id=id)
        return networkfunction
    
    def delete_networkfunction(self, context, id):
        networkfunction = self._get_networkfunction(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(networkfunction)
            ####  Delta Start ###########################
            data = self._make_networkfunction_dict(networkfunction)
            delta = {}
            data.update({'operation':'delete'})
            delta.update({'networkfunctions_delta': data})
            ####  Delta End ###########################
            self.create_networkfunctions_delta(context, delta)
          
            
    def update_networkfunction(self, context, id, networkfunction):
        n = networkfunction['networkfunction']
        with context.session.begin(subtransactions=True):
            networkfunction = self._get_networkfunction(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, networkfunction, n)
            networkfunction.update(n)
            ####  Delta Start ###########################
            data = self._make_networkfunction_dict(networkfunction)
            delta = {}
            data.update({'operation':'update'})
            delta.update({'networkfunctions_delta': data})
            self.create_networkfunctions_delta(context, delta)
            ####  Delta End ###########################
        return self._make_networkfunction_dict(networkfunction)
        
        
    #############Config handle Table
    
    def _make_config_handle_dict(self, config_handle, fields=None):
        res = {'id': config_handle['id'],
               'name': config_handle['name'],
               'tenant_id': config_handle['tenant_id'],
               'networkfunction_id': config_handle['networkfunction_id'],
               'status': config_handle['status'],
               'slug': config_handle['slug'],
               'config_mode': config_handle['config_mode']}

        return self._fields(res, fields)
    
    def get_config_handle(self, context, id, fields=None):
        config_handle = self._get_config_handle(context, id)
        return self._make_config_handle_dict(config_handle, fields)
        
    def get_config_handles(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_config_handle,
                                    self._make_config_handle_dict,
                                    filters=filters, fields=fields)
        
        
    def create_config_handle(self, context, config_handle):
        n = config_handle['config_handle']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            config_handle = ns_config_handle(tenant_id=tenant_id,
                                        id=n.get('id') or uuidutils.generate_uuid(),
                                        name=n['name'],
                                        networkfunction_id=n['networkfunction_id'],
                                        status=n['status'],
                                        slug=n['slug'],
                                        config_mode=n['config_mode'])
            context.session.add(config_handle)
            ####  Delta Start ###########################
            data = self._make_config_handle_dict(config_handle)
            delta = {}
            data.update({'operation':'create'})
            delta.update({'config_handles_delta': data})
            self.create_config_handles_delta(context, delta)
            ####  Delta End ###########################
        return self._make_config_handle_dict(config_handle)
    
    def _get_config_handle(self, context, id):
        try:
            config_handle = self._get_by_id(context, ns_config_handle, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.Config_handleNotFound(config_handle_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Config_handles match for %s' % id)
            raise q_exc.Config_handleNotFound(config_handle_id=id)
        return config_handle
    
    def delete_config_handle(self, context, id):
        config_handle = self._get_config_handle(context, id)
        with context.session.begin(subtransactions=True):
            ####  Delta Start ###########################
            data = self._make_config_handle_dict(config_handle)
            delta = {}
            data.update({'operation':'delete'})
            delta.update({'config_handles_delta': data})
            self.create_config_handles_delta(context, delta)
            ####  Delta End ###########################
            context.session.delete(config_handle)
            
            
    def update_config_handle(self, context, id, config_handle):
        n = config_handle['config_handle']
        with context.session.begin(subtransactions=True):
            config_handle = self._get_config_handle(context, id)
            config_handle.update(n)
            ####  Delta Start ###########################
            data = self._make_config_handle_dict(config_handle)
            delta = {}
            data.update({'operation':'update'})
            delta.update({'config_handles_delta': data})
            self.create_config_handles_delta(context, delta)
            ####  Delta End ###########################
        return self._make_config_handle_dict(config_handle)
        
        
        
        
    ######################### NetworkFunction Delta ###############################   
    def _make_networkfunctions_delta_dict(self, networkfunctions_delta, fields=None):
        res = {'id': networkfunctions_delta['id'],
               'networkfunction_id': networkfunctions_delta['networkfunction_id'],
               'name': networkfunctions_delta['name'],
               'tenant_id': networkfunctions_delta['tenant_id'],
               'description': networkfunctions_delta['description'],
               'shared': networkfunctions_delta['shared'],
               'operation': networkfunctions_delta['operation'],
               'user_id': networkfunctions_delta['user_id'],
               'logged_at': networkfunctions_delta['logged_at'],
               'version_id': networkfunctions_delta['version_id']}
        return self._fields(res, fields)
    
    def get_networkfunctions_delta(self, context, id, fields=None):
        networkfunctions_delta = self._get_networkfunctions_delta(context, id)
        return self._make_networkfunctions_delta_dict(networkfunctions_delta, fields)
        
    def get_networkfunctions_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_networkfunctions_delta,
                                    self._make_networkfunctions_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_networkfunctions_delta(self, context, networkfunctions_delta):
        n = networkfunctions_delta['networkfunctions_delta']
        
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            networkfunctions_delta = ns_networkfunctions_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         networkfunction_id=n['id'],
                                         name=n['name'],
                                         description=n['description'],
                                         shared=n['shared'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(networkfunctions_delta)
        payload = self._make_networkfunctions_delta_dict(networkfunctions_delta)
        method = n['operation']+"_networkfunction"
        return self._make_networkfunctions_delta_dict(networkfunctions_delta)
    
    def _get_networkfunctions_delta(self, context, id):
        try:
            networkfunctions_delta = self._get_by_id(context, ns_networkfunctions_delta, id)
        except exc.NoResultFound:
            raise q_exc.networkfunctions_deltaNotFound(networkfunctions_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple networkfunctions_deltas match for %s' % id)
            raise q_exc.networkfunctions_deltaNotFound(networkfunctions_delta_id=id)
        return networkfunctions_delta
    
    ######################### Config Handle Delta ###############################   
    def _make_config_handles_delta_dict(self, config_handles_delta, fields=None):
        res = {'id': config_handles_delta['id'],
               'config_handle_id': config_handles_delta['config_handle_id'],
               'name': config_handles_delta['name'],
               'tenant_id': config_handles_delta['tenant_id'],
               'networkfunction_id': config_handles_delta['networkfunction_id'],
               'status': config_handles_delta['status'],
               'slug': config_handles_delta['slug'],
               'operation': config_handles_delta['operation'],
               'user_id': config_handles_delta['user_id'],
               'logged_at': config_handles_delta['logged_at'],
               'version_id': config_handles_delta['version_id']}
        return self._fields(res, fields)
    
    def get_config_handles_delta(self, context, id, fields=None):
        config_handles_delta = self._get_config_handles_delta(context, id)
        return self._make_config_handles_delta_dict(config_handles_delta, fields)
        
    def get_config_handles_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_config_handles_delta,
                                    self._make_config_handles_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_config_handles_delta(self, context, config_handles_delta):
        n = config_handles_delta['config_handles_delta']
        LOG.error('Delta %s' % str(n))
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            config_handles_delta = ns_config_handles_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         config_handle_id = n['id'],
                                         name=n['name'],
                                         networkfunction_id=n['networkfunction_id'],
                                         status=n['status'],
                                         slug=n['slug'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(config_handles_delta)
        payload = self._make_config_handles_delta_dict(config_handles_delta)
        method = n['operation']+"_config_handle"
        return self._make_config_handles_delta_dict(config_handles_delta)
    
    def _get_config_handles_delta(self, context, id):
        try:
            config_handles_delta = self._get_by_id(context, ns_config_handles_delta, id)
        except exc.NoResultFound:
            raise q_exc.config_handles_deltaNotFound(config_handles_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple config_handles_deltas match for %s' % id)
            raise q_exc.config_handles_deltaNotFound(config_handles_delta_id=id)
        return config_handles_delta
    
