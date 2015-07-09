# Server Specific Configurations
server = {
    'port': '20202',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'nscsas.api.resources.root.RootController',
    'modules': ['nscsas.api'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/nscsas/api/templates',
    'debug': False,
}
