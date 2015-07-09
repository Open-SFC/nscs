"""Version 1 of the API.
"""
import os
import sys
from pecan import expose, abort
import wsmeext.pecan as wsme_pecan
from pecan.rest import RestController

from nscs.ocas_utils.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class V1Controller(RestController):
    """Version 1 API controller root."""

    @expose()
    def _lookup(self, res, *remainder):
        base = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, base)
        if res in os.listdir(base):
            if os.path.isdir(base + '/' + res) and os.path.exists(base + '/' + res+'/__init__.py'):
                if res in sys.modules:
                    del sys.modules[res]
                pkg = __import__(res)
                if hasattr(pkg, res.upper()+'Controller'):
                    control = getattr(pkg, res.upper()+'Controller')
                    sys.path = sys.path[1:]
                    return control(), remainder
                else:
                    abort(404)
        else:
            abort(404)

    @expose('json')
    def get(self):
        LOG.debug(_("Aborting on Get"))
        abort(401)

    @expose()
    def post(self):
        abort(401)
