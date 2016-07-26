#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import xmlrpclib

from lib.logger import Logger

COBBLER_USER = 'cobbler'
COBBLER_PASS = 'cobbler'


class CobblerAddProfiles(object):
    def __init__(self, log_level, distro, name, kopts):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        if kopts == "none":
            kopts = ""

        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)

        new_profile_create = cobbler_server.new_profile(token)
        cobbler_server.modify_profile(
            new_profile_create,
            "name",
            name,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "distro",
            distro,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "enable_menu",
            "True",
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "kickstart",
            "/var/lib/cobbler/kickstarts/%s.seed" % name,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "kernel_options",
            kopts,
            token)
        cobbler_server.save_profile(new_profile_create, token)

        log.info(
            "Cobbler Add Profile: name=%s, distro=%s" %
            (name, distro))

        cobbler_server.sync(token)
        log.info("Running Cobbler sync")


if __name__ == '__main__':
    """
    Arg1: name of parent distro
    Arg2: profile name
    Arg3: kernel options
    Arg4: log level
    """
    log = Logger(__file__)

    ARGV_MAX = 5
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    distro = sys.argv[1]
    name = sys.argv[2]
    kopts = sys.argv[3]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[4]
    else:
        log_level = None

    cobbler_output = CobblerAddProfiles(log_level, distro, name, kopts)
