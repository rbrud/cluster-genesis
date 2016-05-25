#!/usr/bin/env python
import sys
import re
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
from pyghmi.ipmi import command as ipmi_command

import os

SNMP_PORT = 161

SYSTEM = 'System'
NODE1 = 'NODE 1'
IPMI_CHASSIS_PART_NUMBER = 'Chassis part number'
IPMI_CHASSIS_SERIAL_NUMBER = 'Chassis serial number'
IPMI_MODEL = 'Model'

YAML_CHASSIS_PART_NUMBER = 'chassis-part-number'
YAML_CHASSIS_SERIAL_NUMBER = 'chassis-serial-number'
YAML_MODEL = 'model'
YAML_IPV4_ADDR = 'ipv4_addr'
YAML_USERID_IPMI = 'userid-ipmi'
YAML_PASSWORD_IPMI = 'password-ipmi'

inventory = yaml.load(open(sys.argv[1]), Loader=AttrDictYAMLLoader)

node_inv = inventory['nodes']
for inv_key in node_inv:
    for i in range(0, len(node_inv[inv_key])):
        ipmi_cmd = ipmi_command.Command(
            bmc=node_inv[inv_key][i][YAML_IPV4_ADDR],
            userid=node_inv[inv_key][i][YAML_USERID_IPMI],
            password=node_inv[inv_key][i][YAML_PASSWORD_IPMI])
        for ipmi_key, ipmi_value in ipmi_cmd.get_inventory():
            if ipmi_key == SYSTEM or ipmi_key == NODE1:
                ipmi_key_str = str(ipmi_key)
                if IPMI_CHASSIS_PART_NUMBER in ipmi_value:
                    node_inv[inv_key][i][YAML_CHASSIS_PART_NUMBER] = \
                        str(ipmi_value[IPMI_CHASSIS_PART_NUMBER])
                if IPMI_CHASSIS_SERIAL_NUMBER in ipmi_value:
                    node_inv[inv_key][i][YAML_CHASSIS_SERIAL_NUMBER] = \
                        str(ipmi_value[IPMI_CHASSIS_SERIAL_NUMBER])
                if IPMI_MODEL in ipmi_value:
                    node_inv[inv_key][i][YAML_MODEL] = \
                        str(ipmi_value[IPMI_MODEL])
                if ipmi_key == NODE1:
                    break
yaml.dump(
    inventory,
    open(sys.argv[1], 'w'),
    indent=4,
    default_flow_style=False)
