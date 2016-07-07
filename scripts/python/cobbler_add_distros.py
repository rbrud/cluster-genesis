#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
import xmlrpclib

from lib.logger import Logger

COBBLER_USER = 'cobbler'
COBBLER_PASS = 'cobbler'


class CobblerAddDistros(object):
    def __init__(self, log_level, path, name, arch):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)

        new_distro_create = cobbler_server.new_distro(token)
        cobbler_server.modify_distro(
            new_distro_create,
            "name",
            name,
            token)
        if arch == "ppc64el":
            cobbler_server.modify_distro(
                new_distro_create,
                "kernel",
                path + "/install/netboot/vmlinux",
                token)
            cobbler_server.modify_distro(
                new_distro_create,
                "initrd",
                path + "/install/netboot/initrd.gz",
                token)
            cobbler_server.modify_distro(
                new_distro_create,
                "arch",
                "ppc64le",
                token)
        elif arch == "amd64":
            cobbler_server.modify_distro(
                new_distro_create,
                "kernel",
                path + "/install/netboot/ubuntu-installer/amd64/linux",
                token)
            cobbler_server.modify_distro(
                new_distro_create,
                "initrd",
                path + "/install/netboot/ubuntu-installer/amd64/initrd.gz",
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
            name,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "distro",
            name,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "enable_menu",
            "True",
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "kickstart",
            "/var/lib/cobbler/kickstarts/" + name + ".cfg",
            token)
        if arch == "ppc64el":
            cobbler_server.modify_profile(
                new_profile_create,
                "kernel_options",
                "console=netcfg/dhcp_timeout=1024 netcfg/choose_interface=auto ipv6.disable=1",
                token)
        elif arch == "amd64":
            cobbler_server.modify_profile(
                new_profile_create,
                "kernel_options",
                "console=tty2 console=ttyS2,115200n8 netcfg/dhcp_timeout=1024 netcfg/choose_interface=auto ipv6.disable=1",
                token)
        cobbler_server.save_profile(new_profile_create, token)
        cobbler_server.sync(token)
        log.info("Running Cobbler sync")


if __name__ == '__main__':
    """
    Arg1: path to install files
    Arg2: distro name
    Arg3: distro architecture
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

    path = sys.argv[1]
    name = sys.argv[2]
    arch = sys.argv[3]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[4]
    else:
        log_level = None

    cobbler_output = CobblerAddDistros(log_level, path, name, arch)
