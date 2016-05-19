#!/usr/bin/env python
import sys
import re
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
from pysnmp.hlapi import *

SNMP_PORT = 161

inventory = yaml.load(open(sys.argv[1]), Loader=AttrDictYAMLLoader)

inventory['hosts'] = []

for (
    errorIndication,
    errorStatus,
    errorIndex,
    varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget((inventory['ipaddr_mgmt_switch'], SNMP_PORT)),
        ContextData(),
        ObjectType(ObjectIdentity('IP-MIB', 'ipNetToMediaPhysAddress')),
        lexicographicMode=False):

    if errorIndication:
        print(errorIndication)
        break
    elif errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
        break
    else:
        _dict = {}
        for varBind in varBinds:
            m = re.search(
                ('^IP-MIB::ipNetToMediaPhysAddress\.\d+\.' +
                 '((\d{1,3}\.){3}\d{1,3})' +
                 ' = ' +
                 '(([\da-fA-F]{2}:){5}[\da-fA-F]{2})$'),
                str(varBind))
            ipv4 = m.group(1)
            mac = m.group(3)
            if ipv4 != inventory['ipaddr_mgmt_switch']:
                _dict['ipv4'] = ipv4
                _dict['mac'] = mac
                inventory['hosts'].append(_dict)

for (
    errorIndication,
    errorStatus,
    errorIndex,
    varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget((inventory['ipaddr_mgmt_switch'], SNMP_PORT)),
        ContextData(),
        ObjectType(ObjectIdentity('BRIDGE-MIB', 'dot1dTpFdbPort')),
        lexicographicMode=False):

    if errorIndication:
        print(errorIndication)
        break
    elif errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
        break
    else:
        for varBind in varBinds:
            m = re.search(
                ('^BRIDGE-MIB::dot1dTpFdbPort\.(' +
                 '([\da-fA-F]{2}:){5}[\da-fA-F]{2})' +
                 ' = ' +
                 '(\d+)$'),
                str(varBind))
            mac = m.group(1)
            port = m.group(3)
            for i in range(0, len(inventory['hosts'])):
                if inventory['hosts'][i]['mac'] == mac:
                    inventory['hosts'][i]['port'] = port
                    continue

yaml.dump(
    inventory,
    open(sys.argv[1], 'w'),
    default_flow_style=False)
