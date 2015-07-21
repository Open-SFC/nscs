from oslo_config import cfg

# Register options for the service
API_SERVICE_OPTS = [
    cfg.IntOpt('port',
               default=20202,
               help='The port for the OCAS API server',),
    cfg.StrOpt('host',
               default='0.0.0.0',
               help='The listen IP for the OCAS API server',),
    cfg.BoolOpt('ucm_support',
                default=True,
                help='UCM Support for OCAS',),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='api',
                         title='Options for the nscsas-server service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)
