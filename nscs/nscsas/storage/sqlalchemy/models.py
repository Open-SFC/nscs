# -*- encoding: utf-8 -*-
#
# Author: Purandhar Sairam Mannidi <sairam.mp@freescale.com>
#
"""
SQLAlchemy models for NSCSAS data.
"""

import json
import urlparse

from oslo_config import cfg
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, DATETIME
from oslo_db.sqlalchemy import session as sa_session
import uuid

from nscs.nscsas import utils

sql_opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine')
]

cfg.CONF.register_opts(sql_opts)

_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = sa_session.EngineFacade.from_config(cfg.CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def table_args():
    engine_name = urlparse.urlparse(cfg.CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': cfg.CONF.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class PreciseTimestamp(TypeDecorator):
    """Represents a timestamp precise to the microsecond."""

    impl = DATETIME

    def load_dialect_impl(self, dialect):
        if dialect.name == 'mysql':
            return dialect.type_descriptor(DECIMAL(precision=20,
                                                   scale=6,
                                                   asdecimal=True))
        return dialect.type_descriptor(DATETIME())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'mysql':
            return utils.dt_to_decimal(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'mysql':
            return utils.decimal_to_dt(value)
        return value


class NSCSASBase(object):
    """Base class for NSCSAS Models."""
    __table_args__ = table_args()
    __table_initialized__ = False

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def update(self, values):
        """Make the model object behave like a dict."""
        for k, v in values.iteritems():
            setattr(self, k, v)


Base = declarative_base(cls=NSCSASBase)
