# Copyright 2012 OpenStack LLC.
# All Rights Reserved
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

from nscs.crdclient.common import exceptions
from nscs.crdclient.common import utils

import configparser

config=configparser.ConfigParser()
crdclient_conf = "/usr/local/etc/crd/nscsclient.conf"
config.read(crdclient_conf)
try:
    classes=str(config.get('application_classes', 'classes'))
except:
    classes=''

APP_CLASSES = {}
classes_list = classes.split(',')
for clas in classes_list:
    if clas:
        clas_details = clas.split(':')
        APP_CLASSES[clas_details[0]] = clas_details[1]
#API_NAME = 'network'
#API_VERSIONS = {
#    '2.0': 'crdclient.v2_0.client.Client',
#}

def make_client(instance):
    """Returns an crd client.
    """
    crd_client = utils.get_client_class(
        instance._app_name,
        instance._app_name,
        APP_CLASSES,
    )
    instance.initialize()
    url = instance._url
    url = url.rstrip("/")
    #if '2.0' == instance._api_version[API_NAME]:
    if APP_CLASSES[instance._app_name]:
        client = crd_client(username=instance._username,
                                tenant_name=instance._tenant_name,
                                password=instance._password,
                                region_name=instance._region_name,
                                auth_url=instance._auth_url,
                                endpoint_url=url,
                                token=instance._token,
                                auth_strategy=instance._auth_strategy)
        return client
    else:
        raise exceptions.UnsupportedVersion("API version %s is not supported" %
                                            instance._api_version[API_NAME])


def Client(api_version, *args, **kwargs):
    """Return an crd client.
    @param api_version: only 2.0 is supported now
    """
    crd_client = utils.get_client_class(
        API_NAME,
        api_version,
        API_VERSIONS,
    )
    return crd_client(*args, **kwargs)
