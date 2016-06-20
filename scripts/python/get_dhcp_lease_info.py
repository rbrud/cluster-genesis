#!/usr/bin/env python
import sys
import os.path
import re
from orderedattrdict import AttrDict

from lib.logger import Logger


class GetDhcpLeases(object):
    def __init__(self, dhcp_leases_file, log_level):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)
        dhcp_leases_file = os.path.abspath(
            os.path.dirname(os.path.abspath(dhcp_leases_file)) +
            os.path.sep +
            os.path.basename(dhcp_leases_file))

        try:
            f = open(dhcp_leases_file, 'r')
        except:
            log.error('DHCP leases file not found: %s' % (dhcp_leases_file))
            sys.exit(1)
        self.mac_ip = AttrDict()
        for line in f:
            m = re.search(
                '^\S+\s+(\S+)\s+(\S+)',
                line)
            mac = m.group(1)
            ip = m.group(2)
            self.mac_ip[mac] = ip
            log.info('Lease found - MAC: %s - IP: %s' % (mac, ip))

    def get_mac_ip(self):
        return self.mac_ip
