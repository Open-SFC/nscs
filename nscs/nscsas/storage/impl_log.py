# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
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
"""Simple logging storage backend.
"""

from oslo_log import log
from nscs.nscsas.storage import base

LOG = log.getLogger(__name__)


class LogStorage(base.StorageEngine):
    """Log the data
    """

    def get_connection(self, conf):
        """Return a Connection instance based on the configuration settings.
        """
        return Connection(conf)


class Connection(base.Connection):
    """Base class for storage system connections.
    """

    def __init__(self, conf):
        pass

    def upgrade(self):
        pass

    def clear(self):
        pass
