# -*- encoding: utf-8 -*-
#
# Copyright © 2013 Freescale Semiconductor
#
# Author: Purandhar Sairam Mannidi <sairam.mp@freescale.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Storage backend management
"""


import urlparse

from oslo.config import cfg
from stevedore import driver

from nscs.ocas_utils.openstack.common import log
from nscs.nscsas import service


LOG = log.getLogger(__name__)

STORAGE_ENGINE_NAMESPACE = 'nscsas.storage'


cfg.CONF.import_opt('connection',
                    'ocas_utils.openstack.common.db.sqlalchemy.session',
                    group='database')


class StorageBadVersion(Exception):
    """Error raised when the storage backend version is not good enough."""


def get_engine(conf):
    """Load the configured engine and return an instance."""
    engine_name = urlparse.urlparse(conf.database.connection).scheme

    LOG.debug('looking for %r driver in %r',
              engine_name, STORAGE_ENGINE_NAMESPACE)
    mgr = driver.DriverManager(STORAGE_ENGINE_NAMESPACE,
                               engine_name,
                               invoke_on_load=True)
    return mgr.driver


def get_connection(conf):
    """Return an open connection to the database."""
    return get_engine(conf).get_connection(conf)


def dbsync():
    """
    This function creates/updates tables/columns if not present in the database

    @rtype : None
    """
    service.prepare_service()
    get_connection(cfg.CONF).upgrade()
