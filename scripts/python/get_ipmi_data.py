#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
from pyghmi.ipmi import command as ipmi_command

from lib.inventory import Inventory
from lib.logger import Logger

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class Ipmi(object):
    def __init__(self, argv):
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
        if len(argv) == ARGV_MAX:
            LOG_LEVEL = argv[2]
            self.log.set_level(LOG_LEVEL)

        SNMP_PORT = 161

        IPMI_SYSTEM = 'System'
        IPMI_NODE1 = 'NODE 1'
        self.IPMI_CHASSIS_PART_NUMBER = 'Chassis part number'
        self.IPMI_CHASSIS_SERIAL_NUMBER = 'Chassis serial number'
        self.IPMI_MODEL = 'Model'
        self.IPMI_SERIAL_NUMBER = 'Serial Number'
        self.INV_IPV4_ADDR = inv.INV_IPV4_ADDR

        inventory = inv.load(INV_FILE, self.log)

        node_inv = inventory['nodes']
        for inv_key in node_inv:
            for i in range(0, len(node_inv[inv_key])):
                ipmi_cmd = ipmi_command.Command(
                    bmc=node_inv[inv_key][i][inv.INV_IPV4_ADDR],
                    userid=node_inv[inv_key][i][inv.INV_USERID_IPMI],
                    password=node_inv[inv_key][i][inv.INV_PASSWORD_IPMI])
                for ipmi_key, ipmi_value in ipmi_cmd.get_inventory():
                    if ipmi_key == IPMI_SYSTEM or ipmi_key == IPMI_NODE1:
                        self.get_ipmi(
                            node_inv[inv_key][i],
                            inv.INV_CHASSIS_PART_NUMBER,
                            ipmi_key,
                            ipmi_value,
                            self.IPMI_CHASSIS_PART_NUMBER)
                        self.get_ipmi(
                            node_inv[inv_key][i],
                            inv.INV_CHASSIS_SERIAL_NUMBER,
                            ipmi_key,
                            ipmi_value,
                            self.IPMI_CHASSIS_SERIAL_NUMBER)
                        self.get_ipmi(
                            node_inv[inv_key][i],
                            inv.INV_MODEL,
                            ipmi_key,
                            ipmi_value,
                            self.IPMI_MODEL)
                        self.get_ipmi(
                            node_inv[inv_key][i],
                            inv.INV_SERIAL_NUMBER,
                            ipmi_key,
                            ipmi_value,
                            self.IPMI_SERIAL_NUMBER)
                        if ipmi_key == IPMI_NODE1:
                            break

        inv.dump(inventory, self.log)

    def get_ipmi(self, inv, inv_field, ipmi_key, ipmi_value, ipmi_field):
        if ipmi_field in ipmi_value:
            self.log.info(
                inv[self.INV_IPV4_ADDR] +
                ": '" +
                ipmi_key + '[' + ipmi_field + ']' +
                "' = " +
                str(ipmi_value[ipmi_field]))
            inv[inv_field] = str(ipmi_value[ipmi_field])
        else:
            self.log.info(
                inv[self.INV_IPV4_ADDR] +
                ": '" +
                ipmi_key + '[' + ipmi_field + ']' +
                "' not found")


def main(argv):
    ipmi_data = Ipmi(argv)

if __name__ == '__main__':
    main(sys.argv)
