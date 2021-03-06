# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011, Nicira Networks, Inc.
# All Rights Reserved.
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
# Borrowed from nova code base, more utilities will be added/borrowed as and
# when needed.
# @author: Somik Behera, Nicira Networks, Inc.

"""Utilities and helper functions."""

import logging as std_logging
import os
import signal
import socket

from eventlet.green import subprocess
from oslo.config import cfg

from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import lockutils


TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LOG = logging.getLogger(__name__)
SYNCHRONIZED_PREFIX = 'crd-'
synchronized = lockutils.synchronized_with_prefix(SYNCHRONIZED_PREFIX)

def read_cached_file(filename, cache_info, reload_func=None):
    """Read from a file if it has been modified.

    :param cache_info: dictionary to hold opaque cache.
    :param reload_func: optional function to be called with data when
                        file is reloaded due to a modification.

    :returns: data from file

    """
    mtime = os.path.getmtime(filename)
    if not cache_info or mtime != cache_info.get('mtime'):
        LOG.debug(_("Reloading cached file %s"), filename)
        with open(filename) as fap:
            cache_info['data'] = fap.read()
        cache_info['mtime'] = mtime
        if reload_func:
            reload_func(cache_info['data'])
    return cache_info['data']


def find_config_file(options, config_file):
    """
    Return the first config file found.

    We search for the paste config file in the following order:
    * If --config-file option is used, use that
    * Search for the configuration files via common cfg directories
    :retval Full path to config file, or None if no config file found
    """
    fix_path = lambda p: os.path.abspath(os.path.expanduser(p))
    if options.get('config_file'):
        if os.path.exists(options['config_file']):
            return fix_path(options['config_file'])

    dir_to_common = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(dir_to_common, '..', '..', '..', '..')
    # Handle standard directory search for the config file
    config_file_dirs = [fix_path(os.path.join(os.getcwd(), 'etc')),
                        fix_path(os.path.join('~', '.crd-venv', 'etc',
                                              'crd')),
                        fix_path('~'),
                        os.path.join(cfg.CONF.state_path, 'etc'),
                        os.path.join(cfg.CONF.state_path, 'etc', 'crd'),
                        fix_path(os.path.join('~', '.local',
                                              'etc', 'crd')),
                        '/usr/etc/crd',
                        '/usr/local/etc/crd',
                        '/etc/crd/',
                        '/etc']

    if 'plugin' in options:
        config_file_dirs = [
            os.path.join(x, 'crd', 'plugins', options['plugin'])
            for x in config_file_dirs
        ]

    if os.path.exists(os.path.join(root, 'plugins')):
        plugins = [fix_path(os.path.join(root, 'plugins', p, 'etc'))
                   for p in os.listdir(os.path.join(root, 'plugins'))]
        plugins = [p for p in plugins if os.path.isdir(p)]
        config_file_dirs.extend(plugins)

    for cfg_dir in config_file_dirs:
        cfg_file = os.path.join(cfg_dir, config_file)
        if os.path.exists(cfg_file):
            return cfg_file


def _subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually not what
    # non-Python subprocesses expect.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def subprocess_popen(args, stdin=None, stdout=None, stderr=None, shell=False,
                     env=None):
    return subprocess.Popen(args, shell=shell, stdin=stdin, stdout=stdout,
                            stderr=stderr, preexec_fn=_subprocess_setup,
                            close_fds=True, env=env)


def parse_mappings(mapping_list, unique_values=True):
    """Parse a list of of mapping strings into a dictionary.

    :param mapping_list: a list of strings of the form '<key>:<value>'
    :param unique_values: values must be unique if True
    :returns: a dict mapping keys to values
    """
    mappings = {}
    for mapping in mapping_list:
        mapping = mapping.strip()
        if not mapping:
            continue
        split_result = mapping.split(':')
        if len(split_result) != 2:
            raise ValueError(_("Invalid mapping: '%s'") % mapping)
        key = split_result[0].strip()
        if not key:
            raise ValueError(_("Missing key in mapping: '%s'") % mapping)
        value = split_result[1].strip()
        if not value:
            raise ValueError(_("Missing value in mapping: '%s'") % mapping)
        if key in mappings:
            raise ValueError(_("Key %(key)s in mapping: '%(mapping)s' not "
                               "unique") % locals())
        if unique_values and value in mappings.itervalues():
            raise ValueError(_("Value %(value)s in mapping: '%(mapping)s' "
                               "not unique") % locals())
        mappings[key] = value
    return mappings


def get_hostname():
    return socket.getfqdn()


def compare_elements(a, b):
    """ compare elements if a and b have same elements

    This method doesn't consider ordering
    """
    if a is None:
        a = []
    if b is None:
        b = []
    return set(a) == set(b)


def dict2str(dic):
    return ','.join("%s=%s" % (key, val)
                    for key, val in sorted(dic.iteritems()))


def str2dict(string):
    res_dict = {}
    for keyvalue in string.split(',', 1):
        (key, value) = keyvalue.split('=', 1)
        res_dict[key] = value
    return res_dict


def diff_list_of_dict(old_list, new_list):
    new_set = set([dict2str(l) for l in new_list])
    old_set = set([dict2str(l) for l in old_list])
    added = new_set - old_set
    removed = old_set - new_set
    return [str2dict(a) for a in added], [str2dict(r) for r in removed]


def is_extension_supported(plugin, ext_alias):
    return ext_alias in getattr(
        plugin, "supported_extension_aliases", [])


def log_opt_values(log):
    cfg.CONF.log_opt_values(log, std_logging.DEBUG)
