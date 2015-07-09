import logging
import os
from oslo.config import cfg
import pecan

#TODO: Implement ACL functionality if required
#from nscsas.api import acl
from nscs.nscsas.api import config as api_config
from nscs.nscsas.api import hooks
from nscs.nscsas.api import middleware
from nscs.nscsas import service
from nscs.nscsas import storage
#TODO: replace with oslo.i18n
from nscs.ocas_utils.openstack.common import log
from wsgiref import simple_server

LOG = log.getLogger(__name__)


def get_pecan_config():
    # Set up the pecan configuration
    filename = api_config.__file__
    if os.path.splitext(filename)[1] == '.pyc':
        filename = filename.replace('.pyc', '.py')
    elif os.path.splitext(filename)[1] == '.pyo':
        filename = filename.replace('.pyo', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None, extra_hooks=None):
    storage_engine = storage.get_engine(cfg.CONF)
    # FIXME: Replace DBHook with a hooks.TransactionHook
    app_hooks = [hooks.ConfigHook(),
                 hooks.DBHook(
                     storage_engine,
                     storage_engine.get_connection(cfg.CONF),
                 ),
                 hooks.TranslationHook()]
    if extra_hooks:
        app_hooks.extend(extra_hooks)

    if not pecan_config:
        pecan_config = get_pecan_config()

    pecan.configuration.set_config(dict(pecan_config), overwrite=True)

    app = pecan.make_app(
        pecan_config.app.root,
        static_root=pecan_config.app.static_root,
        template_path=pecan_config.app.template_path,
        debug=cfg.CONF.debug,
        force_canonical=getattr(pecan_config.app, 'force_canonical', True),
        hooks=app_hooks,
        wrap_app=middleware.ParsableErrorMiddleware,
        guess_content_type_from_ext=False
    )

    return app


class VersionSelectorApplication(object):
    def __init__(self):
        pc = get_pecan_config()
        self.v1 = setup_app(pecan_config=pc)
        
    def __call__(self, environ, start_response):
        return self.v1(environ, start_response)


def start():
    service.prepare_service()

    # Build the WSGI app
    root = VersionSelectorApplication()
    
    # Create the WSGI server and start it
    host, port = cfg.CONF.api.host, cfg.CONF.api.port
    srv = simple_server.make_server(host, port, root)
    
    LOG.info('Starting server in PID %s' % os.getpid())

    LOG.info("Configuration:")
    cfg.CONF.log_opt_values(LOG, logging.INFO)
    
    if host == '0.0.0.0':
        LOG.info('serving on 0.0.0.0:%s, view at http://127.0.0.1:%s' % (port, port))
    else:
        LOG.info("serving on http://%s:%s" % (host, port))
        
    srv.serve_forever()
