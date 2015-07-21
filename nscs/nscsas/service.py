import eventlet
import socket
import sys

from oslo_config import cfg

from oslo_log import log


cfg.CONF.register_opts([
    cfg.StrOpt('host', default=socket.gethostname(),
               help='Name of this node.  This can be an opaque identifier.  '
                    'It is not necessarily a hostname, FQDN, or IP address. '
                    'However, the node name must be valid within '
                    'an AMQP key, and if using ZeroMQ, a valid '
                    'hostname, FQDN, or IP address'),
])


def prepare_service(argv=None):
    eventlet.monkey_patch()
    log.register_options(cfg.CONF)
    log.set_defaults(default_log_levels=['amqplib=WARN',
                                         'qpid.messaging=INFO',
                                         'sqlalchemy=WARN',
                                         'stevedore=INFO',
                                         'eventlet.wsgi.server=WARN'
                                         ])
    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='nscsas')
    log.setup(cfg.CONF, 'nscsas')
