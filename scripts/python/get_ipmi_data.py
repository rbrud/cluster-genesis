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

        IPMI_SYSTEM = b'System'
        IPMI_NODE1 = b'NODE 1'
        self.IPMI_CHASSIS_PART_NUMBER = b'Chassis part number'
        self.IPMI_CHASSIS_SERIAL_NUMBER = b'Chassis serial number'
        self.IPMI_MODEL = b'Model'
        self.IPMI_SERIAL_NUMBER = b'Serial Number'
        self.IPMI_SYSTEM_FIRMWARE = b'System Firmware'
        self.IPMI_PRODUCT_NAME = b'Product name'
        self.IPMI_OPENPOWER_FW = b'OpenPOWER Firmware'
        self.INV_IPV4_IPMI = inv.INV_IPV4_IPMI
        self.PPC64 = b'ppc64'

        inventory = inv.load(INV_FILE, self.log)

        node_inv = inventory['nodes']
        for inv_key in node_inv:
            for i in range(0, len(node_inv[inv_key])):
                ipmi_cmd = ipmi_command.Command(
                    bmc=node_inv[inv_key][i][inv.INV_IPV4_IPMI],
                    userid=node_inv[inv_key][i][inv.INV_USERID_IPMI],
                    password=node_inv[inv_key][i][inv.INV_PASSWORD_IPMI])
                fw = ipmi_cmd.get_inventory_of_component(
                    self.IPMI_SYSTEM_FIRMWARE)
                try:
                    if self.IPMI_PRODUCT_NAME in fw.keys():
                        if (fw[self.IPMI_PRODUCT_NAME] ==
                                self.IPMI_OPENPOWER_FW):
                            self.get_ipmi(
                                self.IPMI_SYSTEM_FIRMWARE,
                                self.IPMI_PRODUCT_NAME,
                                fw,
                                node_inv[inv_key][i],
                                inv.INV_ARCHITECTURE,
                                self.PPC64)
                except AttributeError:
                    pass
                for ipmi_key, ipmi_value in ipmi_cmd.get_inventory():
                    self.log.debug('%s: %s' % (ipmi_key, ipmi_value))
                    if ipmi_key == IPMI_SYSTEM or ipmi_key == IPMI_NODE1:
                        self.get_ipmi(
                            ipmi_key,
                            self.IPMI_CHASSIS_PART_NUMBER,
                            ipmi_value,
                            node_inv[inv_key][i],
                            inv.INV_CHASSIS_PART_NUMBER)
                        self.get_ipmi(
                            ipmi_key,
                            self.IPMI_CHASSIS_SERIAL_NUMBER,
                            ipmi_value,
                            node_inv[inv_key][i],
                            inv.INV_CHASSIS_SERIAL_NUMBER)
                        self.get_ipmi(
                            ipmi_key,
                            self.IPMI_MODEL,
                            ipmi_value,
                            node_inv[inv_key][i],
                            inv.INV_MODEL)
                        self.get_ipmi(
                            ipmi_key,
                            self.IPMI_SERIAL_NUMBER,
                            ipmi_value,
                            node_inv[inv_key][i],
                            inv.INV_SERIAL_NUMBER)
                        if ipmi_key == IPMI_NODE1:
                            break

        inv.dump(inventory, self.log)

    def get_ipmi(
        self,
        ipmi_key, ipmi_field, ipmi_value,
            inv, inv_field, inv_value=None):
        if ipmi_field in ipmi_value:
            self.log.info(
                inv[self.INV_IPV4_IPMI] +
                ": '" +
                ipmi_key + '[' + ipmi_field + ']' +
                "' = " +
                ipmi_value[ipmi_field])
            if inv_value:
                inv[inv_field] = inv_value
            else:
                inv[inv_field] = str(ipmi_value[ipmi_field])
        else:
            self.log.info(
                inv[self.INV_IPV4_IPMI] +
                ": '" +
                ipmi_key + '[' + ipmi_field + ']' +
                "' not found")


def main(argv):
    ipmi_data = Ipmi(argv)

if __name__ == '__main__':
    main(sys.argv)
