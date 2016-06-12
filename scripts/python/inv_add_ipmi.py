#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
from orderedattrdict import AttrDict

from lib.inventory import Inventory
from lib.logger import Logger
from get_mgmt_switch_config import GetMgmtSwitchConfig
from get_dhcp_lease_info import GetDhcpLeases

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class InventoryAddIpmi(object):
    def __init__(self, argv):
        """
        Arg1: config file
        Arg2: inventory file
        Arg3: DHCP leases file
        Arg4: log level
        """
        self.log = Logger(__file__)

        ARGV_MAX = 5
        argv_count = len(argv)
        if argv_count > ARGV_MAX:
            try:
                raise Exception()
            except:
                self.log.error('Invalid argument count')
                exit(1)

        CFG_FILE = argv[1]
        INV_FILE = argv[2]
        DHCP_LEASES_FILE = argv[3]
        if len(argv) == ARGV_MAX:
            LOG_LEVEL = argv[4]
            self.log.set_level(LOG_LEVEL)

        dhcp_leases = GetDhcpLeases(DHCP_LEASES_FILE, self.log)
        dhcp_mac_ip = dhcp_leases.get_mac_ip()

        inv = Inventory(CFG_FILE, INV_FILE, self.log)
        mgmt_switch_config = GetMgmtSwitchConfig(self.log)
        mgmt_sw_cfg = AttrDict()
        for rack, ipv4 in inv.yield_mgmt_rack_ipv4():
            mgmt_sw_cfg[rack] = mgmt_switch_config.get_port_mac(rack, ipv4)

        inv.create_nodes(dhcp_mac_ip, mgmt_sw_cfg)


def main(argv):
    ipmi_data = InventoryAddIpmi(argv)

if __name__ == '__main__':
    main(sys.argv)
