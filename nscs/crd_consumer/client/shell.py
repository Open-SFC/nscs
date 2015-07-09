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

"""
Command-line interface to the OCAS APIs
"""

import argparse
import gettext
import logging
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from nscs.crd_consumer.client.common import clientmanager
from common import rm_exceptions as exc
from common import utils

import configparser

VERSION = '2.0'
CRM_API_VERSION = '2.0'
config=configparser.ConfigParser()
crdclient_conf = "/usr/local/etc/nscsas/consumer.conf"
config.read(crdclient_conf)
try:
    applications=str(config.get('SDNOFCFG', 'applications'))
except:
    applications=''

def run_command(cmd, cmd_parser, sub_argv):
    _argv = sub_argv
    index = -1
    values_specs = []
    if '--' in sub_argv:
        index = sub_argv.index('--')
        _argv = sub_argv[:index]
        values_specs = sub_argv[index:]
    known_args, _values_specs = cmd_parser.parse_known_args(_argv)
    cmd.values_specs = (index == -1 and _values_specs or values_specs)
    return cmd.run(known_args)


def env(*_vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.

    """
    for v in _vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


COMMAND_V2 = {}
app_list = applications.split(',')
for app in app_list:
    if app:
        cls = None
        cls = utils.import_class(app)
        COMMAND_V2.update(cls.COMMANDS)

COMMANDS = {'2.0': COMMAND_V2}


class HelpAction(argparse.Action):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        outputs = []
        max_len = 0
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands for API v%s:\n' % app.api_version)
        command_manager = app.command_manager
        for name, ep in sorted(command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)
        for (name, one_liner) in outputs:
            app.stdout.write('  %s  %s\n' % (name.ljust(max_len), one_liner))
        sys.exit(0)


class CrmShell(App):

    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    DEBUG_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'
    log = logging.getLogger(__name__)

    def __init__(self, apiversion):
        super(CrmShell, self).__init__(
            description=__doc__.strip(),
            version=VERSION,
            command_manager=CommandManager('sdnofcfg.cli'), )
        self.commands = COMMANDS
        for k, v in self.commands[apiversion].items():
            self.command_manager.add_command(k, v)

        # This is instantiated in initialize_app() only when using
        # password flow auth
        self.auth_client = None
        self.api_version = apiversion

    def build_option_parser(self, description, version):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        """
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False, )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version), )
        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.', )
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='suppress output except warnings and errors', )
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="show this help message and exit", )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='show tracebacks on errors', )
        return parser

    def _bash_completion(self):
        """
        Prints all of the commands and options to stdout so that the
        resource manager's bash-completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for option, _action in self.parser._option_string_actions.items():
            options.add(option)
        for command_name, command in self.command_manager:
            commands.add(command_name)
            cmd_factory = command.load()
            cmd = cmd_factory(self, None)
            cmd_parser = cmd.get_parser('')
            for option, _action in cmd_parser._option_string_actions.items():
                options.add(option)
        print ' '.join(commands | options)

    def run(self, argv):
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            index = 0
            command_pos = -1
            help_pos = -1
            help_command_pos = -1
            for arg in argv:
                if arg == 'bash-completion':
                    self._bash_completion()
                    return 0
                if arg in self.commands[self.api_version]:
                    if command_pos == -1:
                        command_pos = index
                elif arg in ('-h', '--help'):
                    if help_pos == -1:
                        help_pos = index
                elif arg == 'help':
                    if help_command_pos == -1:
                        help_command_pos = index
                index = index + 1
            if command_pos > -1 and help_pos > command_pos:
                argv = ['help', argv[command_pos]]
            if help_command_pos > -1 and command_pos == -1:
                argv[help_command_pos] = '--help'
            self.options, remainder = self.parser.parse_known_args(argv)
            self.configure_logging()
            self.interactive_mode = not remainder
            self.initialize_app(remainder)
        except Exception as err:
            if self.options.debug:
                self.log.exception(err)
                raise
            else:
                self.log.error(err)
            return 1
        result = 1
        if self.interactive_mode:
            _argv = [sys.argv[0]]
            sys.argv = _argv
            result = self.interact()
        else:
            result = self.run_subcommand(remainder)
        return result

    def run_subcommand(self, argv):
        subcommand = self.command_manager.find_command(argv)
        cmd_factory, cmd_name, sub_argv = subcommand
        cmd = cmd_factory(self, self.options)
        err = None
        result = 1
        try:
            self.prepare_to_run_command(cmd)
            full_name = (cmd_name
                         if self.interactive_mode
                         else ' '.join([self.NAME, cmd_name])
                         )
            cmd_parser = cmd.get_parser(full_name)
            return run_command(cmd, cmd_parser, sub_argv)
        except Exception as err:
            if self.options.debug:
                self.log.exception(err)
            else:
                self.log.error(err)
            try:
                self.clean_up(cmd, result, err)
            except Exception as err2:
                if self.options.debug:
                    self.log.exception(err2)
                else:
                    self.log.error('Could not clean up: %s', err2)
            if self.options.debug:
                raise
        else:
            try:
                self.clean_up(cmd, result, None)
            except Exception as err3:
                if self.options.debug:
                    self.log.exception(err3)
                else:
                    self.log.error('Could not clean up: %s', err3)
        return result
    
    def authenticate_user(self):
        """Make sure the user has provided all of the authentication
        info we need.
        """
        print "###################"
        print self.command_name
        temp1 = str(COMMANDS['2.0'][self.command_name])
        temp2 = temp1.split("'")
        app_class = str(temp2[1])
        app_name = str(app_class.split('.')[0])
        print app_name
        print "###################"
        self.app_name = app_name
        self.api_version = {app_name: self.api_version}
        self.client_manager = clientmanager.ClientManager(app_name=self.app_name)
        return

    def initialize_app(self, argv):
        """Global app init bits:

        * set up API versions
        * validate authentication info
        """

        super(CrmShell, self).initialize_app(argv)

        self.api_version = {'network': self.api_version}

        # If the user is not asking for help, make sure they
        # have given us auth.
        cmd_name = None
        self.command_name = None
        self.app_name = None
        if argv:
            cmd_info = self.command_manager.find_command(argv)
            cmd_factory, cmd_name, sub_argv = cmd_info
            self.command_name = cmd_name
        if self.interactive_mode or cmd_name != 'help':
            self.authenticate_user()

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

    def configure_logging(self):
        """Create logging handlers for any log output.
        """
        root_logger = logging.getLogger('')

        # Set up logging to a file
        root_logger.setLevel(logging.DEBUG)

        # Send higher-level messages to the console via stderr
        console = logging.StreamHandler(self.stderr)
        console_level = {0: logging.WARNING,
                         1: logging.INFO,
                         2: logging.DEBUG,
                         }.get(self.options.verbose_level, logging.DEBUG)
        console.setLevel(console_level)
        if logging.DEBUG == console_level:
            formatter = logging.Formatter(self.DEBUG_MESSAGE_FORMAT)
        else:
            formatter = logging.Formatter(self.CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)
        return


def main(argv=sys.argv[1:]):
    gettext.install('client', unicode=1)
    try:
        return CrmShell(CRM_API_VERSION).run(argv)
    except exc.UCMClientException:
        return 1
    except Exception as e:
        print e
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
