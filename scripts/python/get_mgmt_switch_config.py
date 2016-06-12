#!/usr/bin/env python
import sys
import re
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
from orderedattrdict import AttrDict
from pysnmp.hlapi import *

from lib.utilities import *

SNMP_PORT = 161
PUBLIC = 'public'
BRIDGE_MIB = 'BRIDGE-MIB'
DOT_1D_TP_FDB_PORT = 'dot1dTpFdbPort'


class GetMgmtSwitchConfig(object):
    def __init__(self, log):
        self.log = log

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


def main(argv):
    from lib.logger import Logger
    log = Logger(__file__)

    ARGV_MAX = 3
    argv_count = len(argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    switch_mgmt_ipv4 = argv[1]
    if len(argv) == ARGV_MAX:
        log_level = argv[2]
        log.set_level(log_level)

    mac_port = GetMgmtSwitchConfig(switch_mgmt_ipv4, log)

if __name__ == '__main__':
    main(sys.argv)
