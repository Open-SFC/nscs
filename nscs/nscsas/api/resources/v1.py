"""Version 1 of the API.
"""
import configparser
import os
import sys
from pecan import expose, abort
import wsmeext.pecan as wsme_pecan
from pecan.rest import RestController

from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _
from oslo_utils import importutils

LOG = logging.getLogger(__name__)


class V1Controller(RestController):
    """Version 1 API controller root."""

    @expose()
    def _lookup(self, res, *remainder):

        modconf = configparser.ConfigParser()
        confbase = os.path.dirname(cfg.CONF.config_file[0])
        for cnf in os.listdir(confbase + '/modules'):
            if '.conf' in cnf:
                modconf.read(str(confbase + '/modules/' + cnf))
                mod = modconf.get("DEFAULT","resource_module").split(":")
                if mod[0] == res:
                    pkg = importutils.try_import(mod[1])
                    if pkg and hasattr(pkg, res.upper()+'Controller'):
                        control = getattr(pkg, res.upper()+'Controller')
                        return control(), remainder
                    else:
                        abort(404)

    @expose('json')
    def get(self):
        LOG.debug(_("Aborting on Get"))
        abort(401)

    @expose()
    def post(self):
        abort(401)
