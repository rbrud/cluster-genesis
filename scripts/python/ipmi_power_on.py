#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
from pyghmi.ipmi import command as ipmi_command
from pyghmi import exceptions as pyghmi_exception

from lib.inventory import Inventory
from lib.logger import Logger

WAIT = True
ON = 'on'
POWERSTATE = 'powerstate'


class IpmiPowerOn(object):
    def __init__(self, log_level, inv_file):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        inv = Inventory(log_level, inv_file)
        for rack_id, ipv4, _userid, _password in inv.yield_ipmi_access_info():
            ipmi_cmd = ipmi_command.Command(
                bmc=ipv4,
                userid=_userid,
                password=_password)

            try:
                rc = ipmi_cmd.get_power()
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'Power status failed - Rack: %s - IP: %s, %s' %
                    (rack_id, ipv4, str(error)))
                sys.exit(1)

            if rc.get(POWERSTATE) == ON:
                log.info(
                    'Already powered on - Rack: %s - IP: %s' % (rack_id, ipv4))
                continue

            try:
                rc = ipmi_cmd.set_power(ON, WAIT)
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'Power on failed - Rack: %s - IP: %s, %s' %
                    (rack_id, ipv4, str(error)))
                sys.exit(1)

            if rc.get(POWERSTATE) != ON:
                log.error(
                    'Power on did not occur - Rack: %s - IP: %s' %
                    (rack_id, ipv4))
                sys.exit(1)

            log.info('Power on - Rack: %s - IP: %s' % (rack_id, ipv4))

if __name__ == '__main__':
    log = Logger(__file__)
    ARGV_MAX = 3
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    inv_file = sys.argv[1]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[2]
    else:
        log_level = None
    ipmi_data = IpmiPowerOn(log_level, inv_file)
