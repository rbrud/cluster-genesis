#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
import xmlrpclib

from lib.logger import Logger


class CobblerAddDistro(object):
    def __init__(self, argv):
        self.log = Logger(__file__)

        ARGV_MAX = 5
        argv_count = len(sys.argv)
        if argv_count > ARGV_MAX:
            try:
                raise Exception()
            except:
                self.log.error('Invalid argument count')
                exit(1)

        PATH = sys.argv[1]
        NAME = sys.argv[2]
        ARCH = sys.argv[3]

        if len(sys.argv) == ARGV_MAX:
            LOG_LEVEL = sys.argv[4]
            self.log.set_level(LOG_LEVEL)

        COBBLER_USER = 'cobbler'
        COBBLER_PASS = 'cobbler'

        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)

        new_distro_create = cobbler_server.new_distro(token)
        cobbler_server.modify_distro(
            new_distro_create,
            "name",
            NAME,
            token)
        if ARCH == "ppc64el":
            cobbler_server.modify_distro(
                new_distro_create,
                "kernel",
                PATH + "/install/netboot/vmlinux",
                token)
            cobbler_server.modify_distro(
                new_distro_create,
                "initrd",
                PATH + "/install/netboot/initrd.gz",
                token)
        elif ARCH == "amd64":
            cobbler_server.modify_distro(
                new_distro_create,
                "kernel",
                PATH + "/install/netboot/ubuntu-installer/amd64/linux",
                token)
            cobbler_server.modify_distro(
                new_distro_create,
                "initrd",
                PATH + "/install/netboot/ubuntu-installer/amd64/initrd.gz",
                token)
        cobbler_server.modify_distro(
            new_distro_create,
            "arch",
            "x86_64",
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "breed",
            "ubuntu",
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "os_version",
            "trusty",
            token)
        cobbler_server.save_distro(new_distro_create, token)
        new_profile_create = cobbler_server.new_profile(token)
        cobbler_server.modify_profile(
            new_profile_create,
            "name",
            NAME,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "distro",
            NAME,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "enable_menu",
            "True",
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "kickstart",
            "/var/lib/cobbler/kickstarts/" + NAME + ".cfg",
            token)
        if ARCH == "ppc64el":
            cobbler_server.modify_profile(
                new_profile_create,
                "kernel_options",
                "console=netcfg/dhcp_timeout=1024 netcfg/choose_interface=auto ipv6.disable=1",
                token)
        elif ARCH == "amd64":
            cobbler_server.modify_profile(
                new_profile_create,
                "kernel_options",
                "console=tty2 console=ttyS2,115200n8 netcfg/dhcp_timeout=1024 netcfg/choose_interface=auto ipv6.disable=1",
                token)
        cobbler_server.save_profile(new_profile_create, token)
        cobbler_server.sync(token)
        self.log.info("Running Cobbler sync")


def main(argv):
    cobbler_output = CobblerAddDistro(argv)

if __name__ == '__main__':
    main(sys.argv)
