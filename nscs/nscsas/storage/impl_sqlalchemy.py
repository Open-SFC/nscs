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
import os
import sys

from nscs.ocas_utils.openstack.common.db.sqlalchemy import session as sa_session
from nscs.ocas_utils.openstack.common import log
from nscs.nscsas.storage import base
from nscs.nscsas.storage.sqlalchemy.models import Base
from nscs.nscsas.api import resources


LOG = log.getLogger(__name__)


class SQLAlchemyStorage(base.StorageEngine):
    """Put the data into a SQLAlchemy database.

    TODO: Need to add table information.
    Tables::
    """

    @staticmethod
    def get_connection(conf):
        """Return a Connection instance based on the configuration settings.
        """
        return Connection(conf)


class Connection(base.Connection):
    """SqlAlchemy connection."""

    def __init__(self, conf):
        url = conf.database.connection
        if url == 'sqlite://':
            conf.database.connection = \
                os.environ.get('OCAS_TEST_SQL_URL', url)
        engine = sa_session.get_session().get_bind()

        dbase = os.path.dirname(os.path.abspath(resources.__file__))
        sys.path.insert(0, dbase)
        for res in os.listdir(dbase):
            if os.path.isdir(dbase + '/' + res) and \
                    os.path.exists(dbase + '/' + res + '/__init__.py') and\
                    os.path.exists(dbase + '/' + res + '/db.py'):
                __import__(res + '.db', fromlist=['*'])

        Base.metadata.create_all(engine)
        sys.path = sys.path[1:]

    def upgrade(self):
        #TODO: Database migration scripts and Schema Upgradation
        pass

    def clear(self):
        session = sa_session.get_session()
        engine = session.get_bind()
        for table in reversed(Base.metadata.sorted_tables):
            engine.execute(table.delete())

