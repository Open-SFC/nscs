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

from nscs.crd_consumer.client.common import rm_exceptions
from nscs.crd_consumer.client.common import utils

import configparser

config=configparser.ConfigParser()
crdclient_conf = "/usr/local/etc/nscsas/consumer.conf"
config.read(crdclient_conf)
try:
    classes=str(config.get('SDNOFCFG', 'application_classes'))
except:
    classes=''

APP_CLASSES = {}
classes_list = classes.split(',')
for clas in classes_list:
    if clas:
        clas_details = clas.split(':')
        APP_CLASSES[clas_details[0]] = clas_details[1]
#API_NAME = 'sdnofcfg'
#API_VERSIONS = {
#    '2.0': 'crd_consumer.client.ocas_client.Client',
#}


def make_client(instance):
    """Returns OCAS client.
    """
    rm_client = utils.get_client_class(
        instance._app_name,
        instance._app_name,
        APP_CLASSES,
    )
    instance.initialize()
    url = instance._url
    #url = url.rstrip("/")
    client = rm_client()
    return client


def Client(api_version, *args, **kwargs):
    """Return an OCAS client.
    @param api_version: only 2.0 is supported now
    """
    rm_client = utils.get_client_class(
        API_NAME,
        api_version,
        API_VERSIONS,
    )
    return rm_client(*args, **kwargs)
