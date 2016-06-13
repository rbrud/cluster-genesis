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
        self.log = Logger(__file__)

        ARGV_MAX = 4
        argv_count = len(argv)
        if argv_count > ARGV_MAX:
            try:
                raise Exception()
            except:
                self.log.log_error('Invalid argument count')
                exit(1)

        CFG_FILE = argv[1]
        INV_FILE = argv[2]
        if len(argv) == ARGV_MAX:
            LOG_LEVEL = argv[3]
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
        self.PPC64 = b'ppc64'

        self.inv_obj = Inventory(CFG_FILE, INV_FILE, self.log)

        for inv, key, _key, index, self.node in self.inv_obj.yield_nodes():
            ipmi_cmd = ipmi_command.Command(
                bmc=self.node[self.inv_obj.INV_IPV4_IPMI],
                userid=self.node[self.inv_obj.INV_USERID_IPMI],
                password=self.node[self.inv_obj.INV_PASSWORD_IPMI])
            fw = ipmi_cmd.get_inventory_of_component(
                self.IPMI_SYSTEM_FIRMWARE)
            try:
                if self.IPMI_PRODUCT_NAME in fw.keys():
                    if (fw[self.IPMI_PRODUCT_NAME] ==
                            self.IPMI_OPENPOWER_FW):
                        pass
                        value = self.get_ipmi(
                            self.IPMI_SYSTEM_FIRMWARE,
                            self.IPMI_PRODUCT_NAME,
                            fw,
                            self.PPC64)
                        if value is not None:
                            self.inv_obj.add_to_node(
                                _key,
                                index,
                                self.inv_obj.INV_ARCHITECTURE,
                                value)
            except AttributeError:
                pass
            for ipmi_key, ipmi_value in ipmi_cmd.get_inventory():
                self.log.debug('%s: %s' % (ipmi_key, ipmi_value))
                if ipmi_key == IPMI_SYSTEM or ipmi_key == IPMI_NODE1:
                    value = self.get_ipmi(
                        ipmi_key,
                        self.IPMI_CHASSIS_PART_NUMBER,
                        ipmi_value)
                    if value is not None:
                        self.inv_obj.add_to_node(
                            _key,
                            index,
                            self.inv_obj.INV_CHASSIS_PART_NUMBER,
                            value)
                    value = self.get_ipmi(
                        ipmi_key,
                        self.IPMI_CHASSIS_SERIAL_NUMBER,
                        ipmi_value)
                    if value is not None:
                        self.inv_obj.add_to_node(
                            _key,
                            index,
                            self.inv_obj.INV_CHASSIS_SERIAL_NUMBER,
                            value)
                    value = self.get_ipmi(
                        ipmi_key,
                        self.IPMI_MODEL,
                        ipmi_value)
                    if value is not None:
                        self.inv_obj.add_to_node(
                            _key,
                            index,
                            self.inv_obj.INV_MODEL,
                            value)
                    value = self.get_ipmi(
                        ipmi_key,
                        self.IPMI_SERIAL_NUMBER,
                        ipmi_value)
                    if value is not None:
                        self.inv_obj.add_to_node(
                            _key,
                            index,
                            self.inv_obj.INV_SERIAL_NUMBER,
                            value)
                    if ipmi_key == IPMI_NODE1:
                        break

        self.inv_obj.dump()

    def get_ipmi(
        self,
            ipmi_key, ipmi_field, ipmi_value, inv_value=None):
        if ipmi_field in ipmi_value:
            self.log.info(
                self.node[self.inv_obj.INV_IPV4_IPMI] +
                ": '" +
                ipmi_key + '[' + ipmi_field + ']' +
                "' = " +
                ipmi_value[ipmi_field])
            if inv_value:
                return inv_value
            else:
                return str(ipmi_value[ipmi_field])
        else:
            self.log.info(
                self.node[self.inv_obj.INV_IPV4_IPMI] +
                ": '" +
                ipmi_key + '[' + ipmi_field + ']' +
                "' not found")
            return None


def main(argv):
    ipmi_data = Ipmi(argv)

if __name__ == '__main__':
    main(sys.argv)
