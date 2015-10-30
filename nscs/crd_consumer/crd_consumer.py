#!/usr/bin/env python

# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
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
#
#
#
#

#import logging
import sys
import socket
import time
import os
import re

import eventlet

from oslo.config import cfg
from nscs.ocas_utils.openstack.common.gettextutils import _
from nscs.ocas_utils.openstack.common import context
from nscs.ocas_utils.openstack.common import rpc as os_rpc
from nscs.ocas_utils.openstack.common.rpc import dispatcher
from nscs.ocas_utils.openstack.common.rpc import proxy
from nscs.ocas_utils.openstack.common import log as logging

from nscs.ocas_utils.openstack.common import importutils
from nscs.ocas_utils.openstack.common import lockutils

from client.common import rm_exceptions as exceptions

from client import ocas_client
import configparser

LOG = logging.getLogger(__name__)

crd_consumer_opts = [
    cfg.StrOpt('ip_address', default="127.0.0.1"),
    cfg.StrOpt('ofc_port', default="8999"),
    cfg.StrOpt('cluster_id', default=''),
    cfg.StrOpt('cell'),
]

cfg.CONF.register_opts(crd_consumer_opts, "CRDCONSUMER")

consumer_app_opts = [
    cfg.StrOpt('application_plugins', default=""),
]

cfg.CONF.register_opts(consumer_app_opts, "APPLICATIONS")


class CRDConsumer(proxy.RpcProxy):
    '''
    '''

    # Set RPC API version to 1.0 by default.
    RPC_API_VERSION = '1.0'

    def __init__(self, polling_interval, reconnect_interval, rpc):
        '''Constructor.
        :param rpc: if True use RPC interface to interface with plugin.
        '''
        super(CRDConsumer, self).__init__(topic="crd-service-queue", default_version=self.RPC_API_VERSION)
        self.polling_interval = polling_interval
        self.reconnect_interval = reconnect_interval
        self.uc = ocasclient()

        ###Loading Application Plugins of CRD Consumer
        self.application_plugins = {}
        self._load_application_plugins()

        self.rpc = rpc
        if self.rpc:
            self.setup_rpc()

    def setup_rpc(self):
        """
        Create a 'crd-consumer' Fanout Queue and listen for delta configuration messages. 
        sends init_consumer message to crd-listener to update the consumer in CRD database
        """
        self.host = get_hostname()
        self.consumer_topic = "crd-consumer"
        self.listener_topic = 'crd-listener'
        # RPC network init
        self.consumer_context = context.RequestContext('crd', 'crd',
                                                       is_admin=False)

        # Handle updates from service
        self.dispatcher = self.create_rpc_dispatcher()
        # Define the listening consumers for the agent
        self.conn = os_rpc.create_connection(new=True)

        LOG.info(_("Creating CONSUMER with topic %s...."), self.consumer_topic)
        self.conn.create_consumer(self.consumer_topic, self.dispatcher, fanout=True)
        self._init_consumer()
        self.conn.consume_in_thread()

    def close_queue_connection(self):
        self.conn.close()

    def _load_application_plugins(self):
        modconf = configparser.ConfigParser()
        confpath = cfg.CONF.config_file[0]
        confpath = confpath.replace('nscs.conf', 'consumer_modules/')
        confbase = os.path.dirname(confpath)
        moduleconfs =  os.listdir(confbase)
        paths = ''

        for cnf in sorted(moduleconfs):
          if re.search(r'(\.conf)$', cnf):
                cnf = str(confpath+cnf)
                modconf.read(cnf)
                ext = str(modconf.get("APPLICATIONS","application_plugins"))
                paths = paths+ext+','
        #app_plugins = str(cfg.CONF.APPLICATIONS.application_plugins).split(',')
        LOG.debug(_("Paths: %s"), str(paths))
        app_plugins = paths.split(',')
        LOG.debug(_("Loading Applications plugins: %s"), app_plugins)
        for provider in app_plugins:
            LOG.debug(_("Provider: %s"), str(provider))
            if provider == '':
                continue
            try:
                LOG.info(_("Loading Plugin: %s"), provider)
                plugin_class = importutils.import_class(provider)
            except:
                LOG.exception(_("Error loading plugin"))
                raise Exception(_("Plugin not found."))
            plugin_inst = plugin_class()

            # only one implementation of svc_type allowed
            # specifying more than one plugin
            # for the same type is a fatal exception
            if plugin_inst.get_plugin_type() in self.application_plugins:
                raise Exception(_("Multiple plugins for application "
                                  "%s were configured"),
                                plugin_inst.get_plugin_type())

            self.application_plugins[plugin_inst.get_plugin_type()] = plugin_inst

            LOG.debug(_("Successfully loaded %(type)s plugin. "),
                      {"type": plugin_inst.get_plugin_type(), })

    def get_key(self, key):
        try:
            return int(key)
        except ValueError:
            return key

    def _init_consumer(self):
        ###Need to take version from UCM WSGI
        current_version = 0
        consumer = self.build_message(current_version)
        #delta_msg = self.call(self.consumer_context,self.make_msg('init_consumer',
        # consumer=consumer),self.listener_topic)
        delta_msg = {}
        init_method = 'init_consumer'
        for app_plugin in self.application_plugins:
            try:
                app_delta = {}
                obj = None
                obj = getattr(self.application_plugins[app_plugin], init_method)
            except:
                continue

            try:
                if obj:
                    LOG.info(_("Getting Delta for INIT message running in Application: %s...."), str(app_plugin))
                    app_delta = obj(consumer=consumer)
                    #app_delta = obj()
                    LOG.info(_("Delta in Application %s = %s...."), str(app_plugin), str(app_delta))
                    delta_msg.update(app_delta)
                    time.sleep(1)
            except BaseException, msg1:
                LOG.error(_("Exception raised when running method - %s with msg %s"), str(init_method), msg1)

        LOG.info(_("Final Delta: %s...."), str(delta_msg))
        for k in sorted(delta_msg, key=self.get_key):
            msg = delta_msg[k]
            #LOG.info(_("Version - %s.........Method - %s"),str(k),str(msg['method']))
            try:
                obj = None
                for app_plugin in self.application_plugins:
                    try:
                        obj = getattr(self.application_plugins[app_plugin], msg['method'])
                    except:
                        continue
            except:
                LOG.error(_("No Method defined with the name - %s"), str(msg['method']))
                LOG.info(
                    "-----------------------------------------------------------------------------------------------")
                continue

            try:
                LOG.info(_("Version - %s........Method - %s.........Payload - %s"), str(k), str(msg['method']),
                         str(msg['payload']))
                if obj:
                    obj(self.consumer_context, payload=msg['payload'])
                    time.sleep(3)
            except BaseException, msg1:
                LOG.error(_("Exception raised when running method - %s with msg %s"), str(msg['method']), msg1)
            LOG.info("-----------------------------------------------------------------------------------------------")

    def call_consumer(self, context, **kwargs):
        delta_msg = kwargs['payload']
        for k in sorted(delta_msg, key=self.get_key):
            msg = delta_msg[k]
            #LOG.info(_("Version - %s.........Method - %s"),str(k),str(msg['method']))
            try:
                obj = None
                for app_plugin in self.application_plugins:
                    try:
                        obj = getattr(self.application_plugins[app_plugin], msg['method'])
                    except:
                        continue
            except:
                LOG.error(_("No Method defined with the name - %s"), str(msg['method']))
                LOG.info(
                    "-----------------------------------------------------------------------------------------------")
                continue

            try:
                LOG.info(_("Version - %s........Method - %s.........Payload - %s"), str(k), str(msg['method']),
                         str(msg['payload']))
                if obj:
                    obj(self.consumer_context, payload=msg['payload'])
                    time.sleep(3)
            except BaseException, msg1:
                LOG.error(_("Exception raised when running method - %s with msg %s"), str(msg['method']), msg1)
            LOG.info("-----------------------------------------------------------------------------------------------")

    def build_message(self, version):
        msg = {}
        payload = {}
        payload.update({'hostname': get_hostname(),
                        'ip_address': cfg.CONF.CRDCONSUMER.ip_address,
                        'ofc_port': cfg.CONF.CRDCONSUMER.ofc_port,
                        'cluster_id': cfg.CONF.CRDCONSUMER.cluster_id,
                        'cell': cfg.CONF.CRDCONSUMER.cell,
                        'version': version})
        msg.update({'payload': payload})
        return msg

    def create_rpc_dispatcher(self):
        '''Get the rpc dispatcher for this manager.

        If a manager would like to set an rpc API version, or support more than
        one class as the target of rpc messages, override this method.
        '''
        return dispatcher.RpcDispatcher([self])

    def daemon_loop(self):
        if self.rpc:
            self.rpc_loop()

    def rpc_loop(self):
        while True:
            try:
                start = time.time()
                #Need to take version from UCM WSGI
                consumer = self.build_message(0)
                #self.cast(self.consumer_context,self.make_msg('update_consumer',consumer=consumer),self.listener_topic)
            except:
                LOG.error("Error in agent event loop")

            # sleep till end of polling interval
            elapsed = (time.time() - start)
            if elapsed < self.polling_interval:
                time.sleep(self.polling_interval - elapsed)
            else:
                LOG.info(_("Loop iteration exceeded interval (%s vs. %s)!"), (self.polling_interval, elapsed))

    @classmethod
    @lockutils.synchronized("qmlock", "qml-")
    def _create_instance(cls):
        if cls._instance is None:
            cls._instance = cls()

    @classmethod
    def get_instance(cls):
        # double checked locking
        if cls._instance is None:
            cls._create_instance()
        return cls._instance

    @classmethod
    def get_service_plugins(cls):
        return cls.get_instance().application_plugins


def get_hostname():
    return '%s' % socket.gethostname()


def ocasclient():
    c = ocas_client.Client()
    return c


def setup_logging(conf):
    """Sets up the logging options for a log with supplied name.

    :param conf: a cfg.ConfOpts object
    """
    product_name = "crdconsumer"
    logging.setup(product_name)
    LOG.info(_("Logging enabled!"))


def main():
    eventlet.monkey_patch()
    cfg.CONF(project='crdconsumer')
    setup_logging(cfg.CONF)
    polling_interval = 30
    reconnect_interval = 2
    rpc = True
    plugin = CRDConsumer(polling_interval, reconnect_interval, rpc)
    # Start everything.
    LOG.info("CRD Consumer initialized successfully, now running... ")
    plugin.daemon_loop()
    sys.exit(0)


if __name__ == "__main__":
    main()
