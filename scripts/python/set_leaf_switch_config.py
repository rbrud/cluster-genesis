#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
import paramiko

from lib.inventory import Inventory
from lib.logger import Logger

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class LeafSwitch(object):
    def __init__(self, argv):
        SWITCHES = b'switches'
        LEAF = b'leaf'
        PORT = b'port'
        VLAN = b'vlan'
        IPV4_ADDR = b'ipv4-addr'
        USERID = b'userid'
        PASSWORD = b'password'
        NODES = b'nodes'
        HOSTNAME = b'hostname'

        self.DEBUG = b'DEBUG'
        self.INFO = b'INFO'
        self.SSH_LOG = 'leaf-switch-ssh.log'

        self.ENABLE_REMOTE_CONFIG = 'cli enable \"configure terminal\" %s'
        SET_VLAN = '\"vlan %d\"'
        INTERFACE_ETHERNET = '\"interface ethernet 1/%d\"'
        SWITCHPORT_MODE_HYBRID = '\"switchport mode hybrid\"'
        SWITCHPORT_HYBRID_ALLOWED_VLAN = \
            '\"switchport hybrid allowed-vlan add %d\"'

        inv = Inventory()
        self.log = Logger(__file__)

        ARGV_MAX = 3
        argv_count = len(argv)
        if argv_count > ARGV_MAX:
            try:
                raise Exception()
            except:
                self.log.log_error('Invalid argument count')
                exit(1)

        INV_FILE = argv[1]
        self.LOG_LEVEL = None
        if len(argv) == ARGV_MAX:
            self.LOG_LEVEL = argv[2].upper()
            self.log.set_level(self.LOG_LEVEL)

        inventory = inv.load(INV_FILE, self.log)

        switch_inv = inventory[SWITCHES]
        self.SWITCH_IPV4_ADDR = switch_inv[LEAF][IPV4_ADDR]
        self.SWITCH_PORT = 22
        self.SWITCH_USERID = switch_inv[LEAF][USERID]
        self.SWITCH_PASSWORD = switch_inv[LEAF][PASSWORD]

        vlans = []
        node_inv = inventory[NODES]
        for inv_key in node_inv:
            node_index = 0
            for i in range(0, len(node_inv[inv_key])):
                if LEAF in node_inv[inv_key][i]:
                    if (PORT in node_inv[inv_key][i][LEAF] and
                            VLAN in node_inv[inv_key][i][LEAF]):
                        port = node_inv[inv_key][i][LEAF][PORT]
                        cmd = (
                            INTERFACE_ETHERNET % (port) +
                            ' ' +
                            SWITCHPORT_MODE_HYBRID)
                        self.log.info(
                            'Enable hybrid mode for port %d' % (port))
                        self.issue_cmd(cmd)
                        for vlan in node_inv[inv_key][i][LEAF][VLAN]:
                            if vlan in vlans:
                                self.log.info('Existing vlan %d' % (vlan))
                            else:
                                self.log.info('Create vlan %d' % (vlan))
                                self.issue_cmd(SET_VLAN % (vlan))
                                vlans.append(vlan)
                            cmd = (
                                INTERFACE_ETHERNET % (port) +
                                ' ' +
                                SWITCHPORT_HYBRID_ALLOWED_VLAN % (vlan))
                            self.log.info(
                                'In hybrid mode add vlan %d to port %d'
                                % (vlan, port))
                            self.issue_cmd(cmd)

    def issue_cmd(self, cmd):
        if self.LOG_LEVEL == self.DEBUG or self.LOG_LEVEL == self.INFO:
            paramiko.util.log_to_file(self.SSH_LOG)
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(
            self.SWITCH_IPV4_ADDR,
            self.SWITCH_PORT,
            self.SWITCH_USERID,
            self.SWITCH_PASSWORD)
        stdin, stdout, stderr = s.exec_command(
            self.ENABLE_REMOTE_CONFIG % (cmd))
        # print(stdout.read())
        s.close()


def main(argv):
    ipmi_data = LeafSwitch(argv)

if __name__ == '__main__':
    main(sys.argv)
