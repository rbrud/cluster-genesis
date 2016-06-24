#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
import time
from pyghmi.ipmi import command as ipmi_command
from pyghmi import exceptions as pyghmi_exception

from lib.inventory import Inventory
from lib.logger import Logger


class IpmiSetBootdev(object):
    def __init__(self, log_level, inv_file, bootdev, persist=False):
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
                rc = ipmi_cmd.set_bootdev(bootdev, persist)
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'set_bootdev failed (device=%s persist=%s) - Rack: %s - IP: %s, %s' %
                    (bootdev, persist, rack_id, ipv4, str(error)))
                sys.exit(1)
            if 'error' in rc:
                log.error(
                    'set_bootdev failed (device=%s persist=%s) - Rack: %s - IP: %s, %s' %
                    (bootdev, persist, rack_id, ipv4, str(rc['error'])))
                sys.exit(1)

            log.info(
                    'bootdev set to (device=%s persist=%s) - Rack: %s - IP: %s' %
                    (bootdev, persist, rack_id, ipv4))
            time.sleep(30)


if __name__ == '__main__':
    log = Logger(__file__)
    ARGV_MAX = 5
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    inv_file = sys.argv[1]
    bootdev = sys.argv[2]
    persist = sys.argv[3]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[4]
    else:
        log_level = None
    ipmi_data = IpmiSetBootdev(log_level, inv_file, bootdev, persist)
