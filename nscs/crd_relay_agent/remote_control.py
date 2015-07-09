# vim: tabstop=4 shiftwidth=4 softtabstop=4
import ast
import socket
import select
import time

import eventlet

from oslo.config import cfg
from nscs.crdserver.openstack.common import log as logging
from nscs.crdserver.openstack.common.rpc import proxy
from nscs.crdserver.openstack.common import context

LOG = logging.getLogger(__name__)
INSTANCES_PATH = '/var/lib/nova/instances'


class RemoteControl(proxy.RpcProxy):
    """Relay config class

    This class is capable of managing configurations in service VMs
    and retrieving its config and stats.
    """
    RPC_API_VERSION = '1.0'

    def __init__(self):
        # LOG.debug(_('Instantiating RelayConfig'))
        super(RemoteControl, self).__init__(topic="generate_relay_config", default_version=self.RPC_API_VERSION)
        self.port_fds = {}
        self.user = cfg.CONF.NWSDRIVER.admin_user
        self.password = cfg.CONF.NWSDRIVER.admin_password
        self.tenant = cfg.CONF.NWSDRIVER.admin_tenant
        self.auth_url = cfg.CONF.NWSDRIVER.auth_url
        self.endpoint_url = cfg.CONF.NWSDRIVER.endpoint_url
        self.epoll = select.epoll()
        self.poll_fn = eventlet.spawn_n(self.poller)
        self.consumer_context = context.RequestContext('crd', 'crd',
                                                       is_admin=False)

    def poller(self):
        while True:
            time.sleep(0.25)
            events = self.epoll.poll(0.25)
            # LOG.debug(_('Polling %d events'),len(events))
            #LOG.debug('port_fds = %s' % str(self.port_fds))
            for fileno, event in events:
                if event & select.EPOLLIN:
                    self.process_config_request(fileno)

    def process_config_request(self, fileno):
        data = self.port_fds[fileno]['tmp_data'] + self.port_fds[fileno]['fd'].recv(65535)
        LOG.debug("data received from VM ......\n%s\n\n" % data)

        try:
            req = ast.literal_eval(data)
            self.port_fds[fileno]['tmp_data'] = ''
            LOG.debug("data received from VM ......\n\n%s\n\n" % data)
            if req['method'] == 'hello':
                self.port_fds[fileno]['status_up'] = True
                if self.port_fds[fileno]['conf_up_req']:
                    LOG.debug('sending data to VM............\n\n%s\n\n' % self.port_fds[fileno]['conf_up_req'])
                    for data in self.port_fds[fileno]['conf_up_req']:
                        LOG.debug('sending data to VM............\n\n%s\n\n' % data)
                        self.send_data_to_vm(self.port_fds[fileno]['instance_id'], data)
                        time.sleep(5)
                    self.port_fds[fileno]['conf_up_req'] = []
                return
            else:
                try:
                    ser_data_recv = str(
                        self.call(self.consumer_context, self.make_msg(req['method'], config=req['kwargs']),
                                  str(req['method'])))
                    LOG.debug('data received from crd  = %s\n\n' % ser_data_recv)
                    self.port_fds[fileno]['fd'].send(ser_data_recv)
                    return
                except Exception, msg:
                    LOG.error(_('Exception...\n\t%s'), msg)
        except SyntaxError:
            LOG.debug(_('Incomplete data received from VM.'))
            self.port_fds[fileno]['tmp_data'] += data
            return

    def connect_vm(self, instance_id):
        fd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            fd.connect(INSTANCES_PATH + '/%s/port' % instance_id)
        except socket.error, msg:
            # LOG.debug(_('unable to connect to virtio-serial port. Error: %s'),msg)
            return False
        self.port_fds[fd.fileno()] = {'fd': fd,
                                      'instance_id': instance_id,
                                      'status_up': False,
                                      'tmp_data': '',
                                      'conf_up_req': []}
        # LOG.debug("Successfully created virtio-serial socket.")
        self.epoll.register(fd.fileno(), select.EPOLLIN)
        return self.port_fds[fd.fileno()]

    def _get_fd_details(self, instance_id):
        for val in self.port_fds.values():
            if val['instance_id'] == instance_id:
                return val
        return False

    def send_data_to_vm(self, instance_id, data=''):
        fd = self._get_fd_details(instance_id)
        if not fd:
            # LOG.debug("no socket fd exists.creating.")
            fd = self.connect_vm(instance_id)
            if not fd:
                #LOG.debug(_('No VM virtio-serial port exists for instance instance-%s'),instance_id)
                return False
        # LOG.debug('fd details  %s' % str(fd))
        #LOG.debug('data = %s' % data)
        if data != '' and fd['status_up']:
            if not fd['fd'].send(data) == len(data):
                LOG.debug(_('Could not Send complete data. Data length = %d'), len(data))
        elif (data != '') and (not fd['status_up']):
            fd['conf_up_req'].append(data)
            #LOG.debug("VM is not up.......Storing data\n\n%s\n\n" % (fd['conf_up_req']))

    def delete_vm(self, instance_id):
        port = self._get_fd_details(instance_id)
        if not port:
            LOG.debug("no socket fd exists. Ignoring.")
            return True
        # Fetch FD from port details
        fd = port['fd']
        #Delete FD from port details
        self.port_fds[fd.fd.fileno()]['fd'] = None
        del self.port_fds[fd.fileno()]
        # De register from epoll
        self.epoll.unregister(fd.fileno())
        # Close Socket
        fd.close()
        return True
