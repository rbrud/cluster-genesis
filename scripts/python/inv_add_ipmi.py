#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path

from lib.inventory import Inventory
from lib.logger import Logger
from get_mgmt_switch_config import GetMgmtSwitchConfig

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class InventoryAddIpmi(object):
    def __init__(self, argv):
        """
        Arg1: config file
        Arg2: inventory file
        Arg3: log level
        """
        self.log = Logger(__file__)

        ARGV_MAX = 4
        argv_count = len(argv)
        if argv_count > ARGV_MAX:
            try:
                raise Exception()
            except:
                self.log.error('Invalid argument count')
                exit(1)

        CFG_FILE = argv[1]
        INV_FILE = argv[2]
        if len(argv) == ARGV_MAX:
            LOG_LEVEL = argv[3]
            self.log.set_level(LOG_LEVEL)

        inv = Inventory(CFG_FILE, INV_FILE, self.log)
        mgmt_switch_config = GetMgmtSwitchConfig('192.168.3.5', self.log)
        print(mgmt_switch_config.get_mac_port())

def main(argv):
    ipmi_data = InventoryAddIpmi(argv)

if __name__ == '__main__':
    main(sys.argv)
