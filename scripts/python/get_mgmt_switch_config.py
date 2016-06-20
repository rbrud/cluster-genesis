#!/usr/bin/env python
import sys
import re
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
from orderedattrdict import AttrDict
from pysnmp.hlapi import *

from lib.utilities import *
from lib.logger import Logger

SNMP_PORT = 161
PUBLIC = 'public'
BRIDGE_MIB = 'BRIDGE-MIB'
DOT_1D_TP_FDB_PORT = 'dot1dTpFdbPort'


class GetMgmtSwitchConfig(object):
    def __init__(self, log_level):
        self.log = Logger(__file__)
        if log_level is not None:
            self.log.set_level(log_level)

    def get_port_mac(self, rack, switch_mgmt_ipv4):
        self.mac_port = []
        for (
            errorIndication,
            errorStatus,
            errorIndex,
            varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData(PUBLIC),
                UdpTransportTarget((switch_mgmt_ipv4, SNMP_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity(BRIDGE_MIB, DOT_1D_TP_FDB_PORT)),
                lexicographicMode=False):

            if errorIndication:
                self.log.error(errorIndication)
                sys.exit(1)
            elif errorStatus:
                self.log.error('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
                sys.exit(1)
            else:
                _dict = AttrDict()
                for varBind in varBinds:
                    m = re.search(
                        ('^%s::%s\.(' +
                         '(%s)' +
                         ' = ' +
                         '(\d+)$') % (
                             BRIDGE_MIB, DOT_1D_TP_FDB_PORT, PATTERN_MAC),
                        str(varBind))
                    mac = m.group(1)
                    port = int(m.group(3))
                    _dict[port] = mac
                    self.log.info(
                        'Rack: %s - MAC: %s - port: %d' % (rack, mac, port))
                    self.mac_port.append(_dict)
        return self.mac_port
