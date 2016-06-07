#!/usr/bin/env python
import sys
import re
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
from pysnmp.hlapi import *

SNMP_PORT = 161

inventory = yaml.load(open(sys.argv[1]), Loader=AttrDictYAMLLoader)
SWITCHES_MGMT_IPV4_ADDR = inventory['switches']['mgmt']['ipv4-addr']

for (
    errorIndication,
    errorStatus,
    errorIndex,
    varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget((SWITCHES_MGMT_IPV4_ADDR, SNMP_PORT)),
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
            port = int(m.group(3))
            for key, value in inventory['nodes'].iteritems():
                for i in range(0, len(inventory['nodes'][key])):
                    if inventory['nodes'][key][i]['port-ipmi'] == port:
                        inventory['nodes'][key][i]['mac-ipmi'] = mac
                        continue

yaml.dump(
    inventory,
    open(sys.argv[1], 'w'),
    indent=4,
    default_flow_style=False)
