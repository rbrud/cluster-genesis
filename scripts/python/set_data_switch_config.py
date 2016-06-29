#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
import paramiko

from lib.inventory import Inventory
from lib.logger import Logger

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class ConfigureDataSwitch(object):
    def __init__(self, log_level, cfg_file):
        self.SWITCH_PORT = 22

        self.DEBUG = b'DEBUG'
        self.INFO = b'INFO'
        self.SSH_LOG = 'leaf-switch-ssh.log'

        self.ENABLE_REMOTE_CONFIG = 'cli enable \"configure terminal\" %s'
        SET_VLAN = '\"vlan %d\"'
        INTERFACE_ETHERNET = '\"interface ethernet 1/%s\"'
        SWITCHPORT_MODE_HYBRID = '\"switchport mode hybrid\"'
        SWITCHPORT_HYBRID_ALLOWED_VLAN = \
            '\"switchport hybrid allowed-vlan add %d\"'

        self.log = Logger(__file__)
        self.log_level = log_level
        if log_level is not None:
            log.set_level(log_level)

        inv = Inventory(log_level, None, cfg_file)

        for self.ipv4, self.userid, self.password, vlans \
                in inv.yield_data_vlans():
            for vlan in vlans:
                self.log.info('Create vlan %s' % (vlan))
                self.issue_cmd(SET_VLAN % (vlan))

        for self.ipv4, self.userid, self.password, ports \
                in inv.yield_data_switch_ports():
            for port, vlans in ports.items():
                self.log.info(
                    'Enable hybrid mode for port %s' % (port))
                self.issue_cmd(
                    INTERFACE_ETHERNET % (port) +
                    ' ' +
                    SWITCHPORT_MODE_HYBRID)
                for vlan in vlans:
                    self.log.info(
                        'In hybrid mode add vlan %s to port %s' %
                        (vlan, port))
                    self.issue_cmd(
                        INTERFACE_ETHERNET % (port) +
                        ' ' +
                        SWITCHPORT_HYBRID_ALLOWED_VLAN % (vlan))

    def issue_cmd(self, cmd):
        if self.log_level == self.DEBUG or self.log_level == self.INFO:
            paramiko.util.log_to_file(self.SSH_LOG)
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(
            self.ipv4,
            self.SWITCH_PORT,
            self.userid,
            self.password)
        stdin, stdout, stderr = s.exec_command(
            self.ENABLE_REMOTE_CONFIG % (cmd))
        # print(stdout.read())
        s.close()

if __name__ == '__main__':
    log = Logger(__file__)

    ARGV_MAX = 3
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    cfg_file = sys.argv[1]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[2]
    else:
        log_level = None

    ipmi_data = ConfigureDataSwitch(log_level, cfg_file)
