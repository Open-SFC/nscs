# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Nicira Networks, Inc.
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

"""
Routines for configuring Neutron
"""

import os

from oslo.config import cfg

from nscs.ocas_utils.openstack.common import log as logging
from nscs.ocas_utils.openstack.common.gettextutils import _

from nscs.nscsas.version import version as nscsas_version

LOG = logging.getLogger(__name__)

core_opts = [
    cfg.StrOpt('bind_host', default='0.0.0.0',
               help=_("The host IP to bind to")),
    cfg.IntOpt('bind_port', default=20202,
               help=_("The port to bind to")),
]

# Register the configuration options
cfg.CONF.register_opts(core_opts)


def parse(args):
    cfg.CONF(args=args, project='nscsas',
             version='%%prog %s' % nscsas_version)


def setup_logging(conf):
    """Sets up the logging options for a log with supplied name.

    :param conf: a cfg.ConfOpts object
    """
    product_name = "nscsas"
    logging.setup(product_name)
    LOG.info(_("Logging enabled!"))

