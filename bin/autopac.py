#!/usr/bin/env python

import ConfigParser
import os
import re
import subprocess
import sys

CONF_PATH_LIST = [
    '~/.autopac.ini',
    '~/.autopac/autopac.ini',
    '/etc/autopac.ini',
    '/etc/autopac/autopac.ini',
    '/autopac.ini',
]


class CommandFailed(Exception):

    MESSAGE_TMPL = (
        ">>> Error occurred while executing command: %(command)r\n"
        ">>> Return code: %(return_code)d\n"
        ">>> Outputs:\n"
        "%(output)s"
    )

    def __init__(self, command, return_code, output):
        self.command = command
        self.return_code = return_code
        self.output = output

    def print_exc(self):
        sys.stderr.write(self.MESSAGE_TMPL % {
            'command': self.command,
            'return_code': self.return_code,
            'output': self.output,
        })


class NetworkSetup(object):

    BASE_COMMAND = 'networksetup'

    DEFAULT_SECTION = 'AutopacDefaults'
    PAC_URL_COLUMN = 'pac_url'
    STATIC_ADDR_COLUMN = 'static_addr'

    RE_GET_AIRPORT_NETWORK = re.compile(
        r'Current\sWi-Fi\sNetwork:\s(?P<airport_network>[^\n]+)',
        re.I)
    RE_GET_STATUS = re.compile(
        r'Port:\s*(?P<network_service>[^\n]*)\nDevice:\s*(?P<device>[^\n]*)',
        re.I)

    def __init__(self, config_parser):
        self.cp = config_parser

        # set default values
        self.default_pac_url = None
        self.default_static_addr = None

        if self.cp.has_section(self.DEFAULT_SECTION):
            self.default_pac_url = self.cp.get(self.DEFAULT_SECTION,
                                               self.PAC_URL_COLUMN)
            self.default_static_addr = self.cp.get(self.DEFAULT_SECTION,
                                                   self.STATIC_ADDR_COLUMN)

    def _execute(self, command, *args):
        cmd = [
            self.BASE_COMMAND,
            '-%s' % command
        ]
        cmd.extend(args)

        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        retval = p.wait()
        output = p.stdout.read()

        if retval == 0:
            return output
        else:
            raise CommandFailed(" ".join(cmd), retval, output)

    def _get_airport_network(self, device):
        output = self._execute('getairportnetwork', device)
        match_result = self.RE_GET_AIRPORT_NETWORK.match(output)
        if match_result:
            return match_result.groupdict().get('airport_network')

    def get_status(self):
        output = self._execute('listallhardwareports')
        for network_service, device in self.RE_GET_STATUS.findall(output):
            try:
                airport_network = self._get_airport_network(device)
            except CommandFailed:
                continue
            else:
                return network_service, device, airport_network

        return None, None, None

    def get_target_conf(self, airport_network):
        pac_url = self.default_pac_url
        static_addr = self.default_static_addr
        if self.cp.has_section(airport_network):
            pac_url = self.cp.get(airport_network, self.PAC_URL_COLUMN)
            static_addr = self.cp.get(airport_network, self.STATIC_ADDR_COLUMN)
        return pac_url, static_addr

    def set_autoproxy_state(self, network_service, state):
        """
        networksetup -setautoproxystate $network_service $state
        """
        self._execute('setautoproxystate', network_service, state)
        sys.stdout.write(">>> Set autoproxy state of %r to %r\n"
                         % (network_service, state))

    def setautoproxyurl(self, network_service, pac_url):
        """
        networksetup -setautoproxyurl $network_service $pac_url
        """
        self._execute('setautoproxyurl', network_service, pac_url)
        sys.stdout.write(">>> Set autoproxy url of %r to %r\n"
                         % (network_service, pac_url))

    def set_dhcp(self, network_service):
        """
        networksetup -setdhcp $network_service
        """
        self._execute('setdhcp', network_service)
        sys.stdout.write(">>> Set dhcp for %r\n" % network_service)

    def set_manual_with_dhcp_router(self, network_service, static_addr):
        """
        networksetup -setmanualwithdhcprouter $network_service $static_addr
        """
        self._execute('setmanualwithdhcprouter', network_service, static_addr)
        sys.stdout.write(">>> Set static addr for %r to %r\n"
                         % (network_service, static_addr))

    def auto_setup(self):
        network_service, _, airport_network = self.get_status()
        if airport_network is None:
            return False, 'Airport device not found.'
        else:
            pac_url, static_addr = self.get_target_conf(airport_network)

            if pac_url:
                self.setautoproxyurl(network_service, pac_url)
            else:
                self.set_autoproxy_state(network_service, 'off')

            if static_addr:
                self.set_manual_with_dhcp_router(network_service, static_addr)
            else:
                self.set_dhcp(network_service)

            return True, None


if __name__ == '__main__':
    conf_abspath_list = map(lambda x: os.path.expanduser(x),
                            CONF_PATH_LIST)

    cp = ConfigParser.ConfigParser()
    cp.read(conf_abspath_list)

    networksetup = NetworkSetup(cp)
    try:
        is_succeeded, message = networksetup.auto_setup()
    except CommandFailed as e:
        e.print_exc()
        sys.exit(1)
    else:
        if not is_succeeded:
            sys.stderr.write('>>> Error: %s\n' % message)
            sys.exit(1)
