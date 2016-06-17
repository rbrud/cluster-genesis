#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path

from lib.inventory import Inventory
from lib.logger import Logger


class InventoryAddSwitches(object):
    def __init__(self, log_level, inv_file, cfg_file):
        log = Logger(__file__)

        inv = Inventory(log_level, inv_file, cfg_file)
        inv.add_switches()

if __name__ == '__main__':
    """
    Arg1: config file
    Arg2: inventory file
    Arg3: log level
    """
    log = Logger(__file__)

    ARGV_MAX = 4
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    cfg_file = sys.argv[1]
    inv_file = sys.argv[2]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[3]
    else:
        log_level = None

    ipmi_data = InventoryAddSwitches(log_level, inv_file, cfg_file)
