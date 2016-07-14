#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
from orderedattrdict import AttrDict
import netaddr

from lib.inventory import Inventory
from lib.logger import Logger
from get_mgmt_switch_config import GetMgmtSwitchConfig

INV_IPV4_PXE = 'ipv4-pxe'


class InventoryModifyIPv4Pxe(object):
    def __init__(self, log_level, inv_file, cfg_file, node_mgmt_ipv4_start):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        inv = Inventory(log_level, inv_file, cfg_file)
        new_ip = netaddr.IPNetwork(node_mgmt_ipv4_start)

        i = 0
        for inventory, INV_NODES, key, index, node in inv.yield_nodes():
            inv.add_to_node(key, index, INV_IPV4_PXE, str(new_ip.ip + i))
            i += 1

        for rack, mac, ip in inv.yield_node_pxe():
            log.info(
                'PXE node IP modified - Rack: %s - MAC: %s - IP: %s' %
                (rack, mac, ip))

if __name__ == '__main__':
    """
    Arg1: config file
    Arg2: inventory file
    Arg3: node_mgmt_ipv4_start
    Arg4: log level
    """
    log = Logger(__file__)

    ARGV_MAX = 5
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    cfg_file = sys.argv[1]
    inv_file = sys.argv[2]
    node_mgmt_ipv4_start = sys.argv[3]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[4]
    else:
        log_level = None

    ipmi_data = InventoryModifyIPv4Pxe(
        log_level, inv_file, cfg_file, node_mgmt_ipv4_start)
