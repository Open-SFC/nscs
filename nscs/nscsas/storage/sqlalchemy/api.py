# -*- encoding: utf-8 -*-
#
# Author: John Tran <jhtran@att.com>
#         Julien Danjou <julien@danjou.info>
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

"""SQLAlchemy storage backend."""

from __future__ import absolute_import
import configparser
import os
import sys

from oslo_config import cfg
from oslo_db.sqlalchemy import session as sa_session
from oslo_log import log
from oslo_log._i18n import _
from nscs.nscsas.storage import base
from nscs.nscsas.storage.sqlalchemy.models import Base
from nscs.nscsas.api import resources


LOG = log.getLogger(__name__)


_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(cfg.CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


class SQLAlchemyStorage(base.StorageEngine):
    """Put the data into a SQLAlchemy database.

    TODO: Need to add table information.
    Tables::
    """

    @staticmethod
    def get_session():
        return get_session()

    @staticmethod
    def get_connection():
        """Return a Connection instance based on the configuration settings.
        """
        return Connection()


class Connection(base.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        engine = get_engine()

        modconf = configparser.ConfigParser()
        confbase = os.path.dirname(cfg.CONF.config_file[0])
        res_modules = list()
        for cnf in os.listdir(confbase + '/modules'):
            if '.conf' in cnf:
                modconf.read(str(confbase + '/modules/' + cnf))
                mod = modconf.get("DEFAULT","resource_module")
                res_modules.append(str(mod.split(':')[1]))

        for res in res_modules:
            try:
                __import__(res + '.db', fromlist=['*'])
            except ImportError:
                LOG.info(_("Invalid Resource. No DB schema found."))

        Base.metadata.create_all(engine)

    def upgrade(self):
        #TODO: Database migration scripts and Schema Upgradation
        pass

    def clear(self):
        session = get_session()
        engine = session.get_bind()
        for table in reversed(Base.metadata.sorted_tables):
            engine.execute(table.delete())

