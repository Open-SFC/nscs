from oslo_config import cfg
# Server Specific Configurations
server = {
    'port': '20202',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'nscs.nscsas.api.resources.root.RootController',
    'modules': ['nscs.nscsas.api'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/nscsas/api/templates',
}
