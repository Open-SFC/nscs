# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright 2012 OpenStack Foundation
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

from oslo.config import cfg
import webob.dec
import webob.exc

from nscs.crdservice import context
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import jsonutils
from nscs.crdservice import wsgi

LOG = logging.getLogger(__name__)


class CrdKeystoneContext(wsgi.Middleware):
    """Make a request context from keystone headers."""

    @webob.dec.wsgify
    def __call__(self, req):
        # Determine the user ID
        user_id = req.headers.get('X_USER_ID', req.headers.get('X_USER'))
        if not user_id:
            LOG.debug(_("Neither X_USER_ID nor X_USER found in request"))
            return webob.exc.HTTPUnauthorized()

        # Determine the tenant
        tenant_id = req.headers.get('X_TENANT_ID', req.headers.get('X_TENANT'))

        # Suck Authentication token
        auth_token=req.headers.get('X_AUTH_TOKEN')

        # Suck User Name
        user_name=req.headers.get('X_USER_NAME')

        # Suck Service Catalog
        service_catalog = jsonutils.loads(req.headers.get('X_SERVICE_CATALOG'))

        # Suck out the roles
        roles = [r.strip() for r in req.headers.get('X_ROLE', '').split(',')]

        # Create a context with the authentication data
        ctx = context.Context(user_id, tenant_id, roles=roles, auth_token=auth_token, user_name=user_name, service_catalog=service_catalog)

        # Inject the context...
        req.environ['crdservice.context'] = ctx

        return self.application


def pipeline_factory(loader, global_conf, **local_conf):
    """Create a paste pipeline based on the 'auth_strategy' config option."""
    pipeline = local_conf[cfg.CONF.auth_strategy]
    pipeline = pipeline.split()
    filters = [loader.get_filter(n) for n in pipeline[:-1]]
    app = loader.get_app(pipeline[-1])
    filters.reverse()
    for filter in filters:
        app = filter(app)
    return app
