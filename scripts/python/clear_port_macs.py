#!/usr/bin/env python
# Copyright 2016, IBM US, Inc.

import sys
from lib import inventory
from lib.logger import Logger
import mellanox_switch


def main(log_level, inv_file):

    inv = inventory.Inventory(log_level, inv_file, inv_file)
    switch = mellanox_switch.MellanoxSwitch(log_level)
    switch.clear_mac_address_table(inv)

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

    inv_file = sys.argv[1]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[2]
    else:
        log_level = None

    main(log_level, inv_file)
