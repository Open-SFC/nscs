#!/usr/bin/env python
# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import eventlet
import logging
from oslo.config import cfg
import sys
import socket
import time

from nscs.crdserver.common import config as logging_config
from nscs.crdserver.common import topics
from nscs.crdserver.openstack.common import context
from nscs.crdserver.openstack.common import rpc
from nscs.crdserver.openstack.common.rpc import dispatcher
import remote_control

logging.basicConfig()
LOG = logging.getLogger(__name__)

agent_opts = [
    cfg.IntOpt('polling_interval', default=2),
    cfg.IntOpt('reconnect_interval', default=2),
    cfg.StrOpt('root_helper', default='sudo'),
    cfg.BoolOpt('rpc', default=True),
    cfg.StrOpt('integration_bridge', default='br-int'),
]

relay_opts = [
    cfg.StrOpt('admin_user', default="crd"),
    cfg.StrOpt('admin_password', default="password"),
    cfg.StrOpt('admin_tenant', default="service"),
    cfg.StrOpt('auth_url'),
    cfg.StrOpt('endpoint_url'),
]

cfg.CONF.register_opts(relay_opts, "NWSDRIVER")
cfg.CONF.register_opts(agent_opts, "RAGENT")


class CrdRelayAgent(object):
    """
    CRD Relay Agent is used to relay all configuration related to Service VMs
    """
    # Set RPC API version to 1.0 by default.
    RPC_API_VERSION = '1.0'

    def __init__(self, root_helper,
                 polling_interval, reconnect_interval, rpc):
        """Initialization Routine.

        :param root_helper: utility to use when running shell cmds.
        :param rpc: if True use RPC interface to interface with plugin.
        """
        self.root_helper = root_helper
        self.polling_interval = polling_interval
        self.reconnect_interval = reconnect_interval
        self.com = remote_control.RemoteControl()

        self.rpc = rpc
        if rpc:
            self.setup_rpc()

    def setup_rpc(self):
        self.host = get_hostname()
        self.topic = '%s.%s' % (topics.RELAY_AGENT, self.host)

        # RPC network init
        self.context = context.RequestContext('crd', 'crd',
                                              is_admin=False)
        # Handle updates from service
        self.dispatcher = self.create_rpc_dispatcher()
        # Define the listening consumers for the agent
        self.conn = rpc.create_connection(new=True)
        LOG.info(_('connection is created......'
                   'creating consumer with topic %s....\n'), self.topic)
        self.conn.create_consumer(self.topic,
                                  self.dispatcher, fanout=False)
        self.conn.consume_in_thread()

    def config_update(self, context, **kwargs):
        LOG.info(_('Config Update Message received\n'))
        LOG.info(_('msg received is %s\n'), str(kwargs))
        LOG.info(_('context token id= %s\n'), str(context.to_dict()))
        self.com.send_data_to_vm(kwargs.get('instance_id'),
                                 str(kwargs.get('config_request')))

    def instance_deleted(self, context, **kwargs):
        LOG.info(_('Instance Deleted Message received\n'))
        LOG.info(_('msg received is %s\n'), str(kwargs))
        LOG.info(_('context token id= %s\n'), str(context.to_dict()))
        self.com.delete_vm(kwargs.get('instance_id'))

    def create_rpc_dispatcher(self):
        """Get the rpc dispatcher for this manager.

        If a manager would like to set an rpc API version, or support more than
        one class as the target of rpc messages, override this method.
        """
        return dispatcher.RpcDispatcher([self])

    def rpc_loop(self):
        while True:
            try:
                start = time.time()
            except:
                LOG.exception("Error in agent event loop")

            # sleep till end of polling interval
            elapsed = (time.time() - start)
            if elapsed < self.polling_interval:
                time.sleep(self.polling_interval - elapsed)
            else:
                LOG.info("Loop iteration exceeded interval (%s vs. %s)!",
                         self.polling_interval, elapsed)

    def daemon_loop(self):
        if self.rpc:
            self.rpc_loop()


def get_hostname():
    return '%s' % socket.gethostname()


def main():
    eventlet.monkey_patch()
    cfg.CONF(project='crd')
    logging_config.setup_logging(cfg.CONF)

    root_helper = cfg.CONF.RAGENT.root_helper
    polling_interval = cfg.CONF.RAGENT.polling_interval
    reconnect_interval = cfg.CONF.RAGENT.reconnect_interval
    rpc = cfg.CONF.RAGENT.rpc
    LOG.debug(_("username= %s,password=%s,auth_url=%s"),
             cfg.CONF.NWSDRIVER.admin_user,
             cfg.CONF.NWSDRIVER.admin_password, cfg.CONF.NWSDRIVER.auth_url)

    plugin = CrdRelayAgent(root_helper, polling_interval,
                           reconnect_interval, rpc)

    # Start everything.
    LOG.info(_("Relay Agent initialized successfully, now running... "))
    plugin.daemon_loop()

    sys.exit(0)


if __name__ == "__main__":
    main()
