# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2012 OpenStack Foundation.
# All Rights Reserved.
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

import datetime
import random

import netaddr
from oslo.config import cfg
from sqlalchemy import orm
from sqlalchemy.orm import exc

from nscs.crdservice.api.v2 import attributes
from nscs.crdservice.common import constants
from nscs.crdservice.common import exceptions as q_exc
from nscs.crdservice.db import api as db
from nscs.crdservice.db import sqlalchemyutils
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import timeutils
from nscs.crdservice.openstack.common import uuidutils
from nscs.crdservice.db.nscs_db import NscsDb



LOG = logging.getLogger(__name__)

class CrdDbPluginV2(NscsDb):
    """ A class that implements the v2 crd plugin interface
        using SQLAlchemy models.  Whenever a non-read call happens
        the plugin will call an event handler class method (e.g.,
        network_created()).  The result is that this class can be
        sub-classed by other classes that add custom behaviors on
        certain events.
    """

    # This attribute specifies whether the plugin supports or not
    # bulk/pagination/sorting operations. Name mangling is used in
    # order to ensure it is qualified by class
    __native_bulk_support = True
    __native_pagination_support = True
    __native_sorting_support = True
    # Plugins, mixin classes implementing extension will register
    # hooks into the dict below for "augmenting" the "core way" of
    # building a query for retrieving objects from a model class.
    # To this aim, the register_model_query_hook and unregister_query_hook
    # from this class should be invoked
    _model_query_hooks = {}

    def __init__(self):
        # NOTE(jkoelker) This is an incomlete implementation. Subclasses
        #                must override __init__ and setup the database
        #                and not call into this class's __init__.
        #                This connection is setup as memory for the tests.
        db.configure_db()

    def _get_tenant_id_for_create(self, context, resource):
        if context.is_admin and 'tenant_id' in resource:
            tenant_id = resource['tenant_id']
        elif ('tenant_id' in resource and
              resource['tenant_id'] != context.tenant_id):
            reason = _('Cannot create resource for another tenant')
            raise q_exc.AdminRequired(reason=reason)
        else:
            tenant_id = context.tenant_id
        return tenant_id

    def _model_query(self, context, model):
        query = context.session.query(model)
        # define basic filter condition for model query
        # NOTE(jkoelker) non-admin queries are scoped to their tenant_id
        # NOTE(salvatore-orlando): unless the model allows for shared objects
        query_filter = None
        if not context.is_admin and hasattr(model, 'tenant_id'):
            if hasattr(model, 'shared'):
                query_filter = ((model.tenant_id == context.tenant_id) |
                                (model.shared))
            else:
                query_filter = (model.tenant_id == context.tenant_id)
        # Execute query hooks registered from mixins and plugins
        for _name, hooks in self._model_query_hooks.get(model,
                                                        {}).iteritems():
            query_hook = hooks.get('query')
            filter_hook = hooks.get('filter')
            if query_hook:
                query = query_hook(self, context, model, query)
            if filter_hook:
                query_filter = filter_hook(self, context, model, query_filter)

        # NOTE(salvatore-orlando): 'if query_filter' will try to evaluate the
        # condition, raising an exception
        if query_filter is not None:
            query = query.filter(query_filter)
        return query

    @classmethod
    def register_model_query_hook(cls, model, name, query_hook, filter_hook,
                                  result_filters=None):
        """ register an hook to be invoked when a query is executed.

        Add the hooks to the _model_query_hooks dict. Models are the keys
        of this dict, whereas the value is another dict mapping hook names to
        callables performing the hook.
        Each hook has a "query" component, used to build the query expression
        and a "filter" component, which is used to build the filter expression.

        Query hooks take as input the query being built and return a
        transformed query expression.

        Filter hooks take as input the filter expression being built and return
        a transformed filter expression
        """
        model_hooks = cls._model_query_hooks.get(model)
        if not model_hooks:
            # add key to dict
            model_hooks = {}
            cls._model_query_hooks[model] = model_hooks
        model_hooks[name] = {'query': query_hook, 'filter': filter_hook,
                             'result_filters': result_filters}

    def _get_by_id(self, context, model, id):
        query = self._model_query(context, model)
        return query.filter(model.id == id).one()

    def _fields(self, resource, fields):
        if fields:
            return dict(((key, item) for key, item in resource.iteritems()
                         if key in fields))
        return resource

    def _apply_filters_to_query(self, query, model, filters):
        if filters:
            for key, value in filters.iteritems():
                column = getattr(model, key, None)
                if column:
                    query = query.filter(column.in_(value))
            for _name, hooks in self._model_query_hooks.get(model,
                                                            {}).iteritems():
                result_filter = hooks.get('result_filters', None)
                if result_filter:
                    query = result_filter(self, query, filters)
        return query

    def _get_collection_query(self, context, model, filters=None,
                              sorts=None, limit=None, marker_obj=None,
                              page_reverse=False):
        collection = self._model_query(context, model)
        collection = self._apply_filters_to_query(collection, model, filters)
        if limit and page_reverse and sorts:
            sorts = [(s[0], not s[1]) for s in sorts]
        collection = sqlalchemyutils.paginate_query(collection, model, limit,
                                                    sorts,
                                                    marker_obj=marker_obj)
        return collection

    def _get_collection(self, context, model, dict_func, filters=None,
                        fields=None, sorts=None, limit=None, marker_obj=None,
                        page_reverse=False):
        query = self._get_collection_query(context, model, filters=filters,
                                           sorts=sorts,
                                           limit=limit,
                                           marker_obj=marker_obj,
                                           page_reverse=page_reverse)
        items = [dict_func(c, fields) for c in query.all()]
        if limit and page_reverse:
            items.reverse()
        return items

    def _get_collection_count(self, context, model, filters=None):
        return self._get_collection_query(context, model, filters).count()

    def _validate_shared_update(self, context, id, original, updated):
        # The only case that needs to be validated is when 'shared'
        # goes from True to False
        if updated['shared'] == original.shared or updated['shared']:
            return