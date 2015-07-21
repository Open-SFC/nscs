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

from oslo_config import cfg
from oslo_db.sqlalchemy import session as sa_session
from oslo_log import log
from oslo_i18n._i18n import _
from stevedore import driver

from nscs.nscsas import service


LOG = log.getLogger(__name__)

STORAGE_ENGINE_NAMESPACE = 'nscsas.storage'

_FACADE = None
_IMPL = None

class StorageBadVersion(Exception):
    """Error raised when the storage backend version is not good enough."""

def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = sa_session.EngineFacade.from_config(cfg.CONF)
    return _FACADE


def get_engine():
    """Load the configured engine and return an instance."""
    facade = _create_facade_lazily()
    return facade.get_engine()

def get_backend():
    global _IMPL
    if not _IMPL:
        engine_name = urlparse.urlparse(cfg.CONF.database.connection).scheme
        LOG.debug('looking for %r driver in %r',
                engine_name, STORAGE_ENGINE_NAMESPACE)
        _IMPL = driver.DriverManager(STORAGE_ENGINE_NAMESPACE,
                                     engine_name,
                                     invoke_on_load=True).driver
    return _IMPL


def get_connection():
    """Return an open connection to the database."""
    engine = get_engine()
    return get_backend().get_connection(engine)


def get_session(**kwargs):
    """Return an session to the database."""
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)
