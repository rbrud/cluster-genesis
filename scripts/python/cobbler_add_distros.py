#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import xmlrpclib

from lib.logger import Logger

COBBLER_USER = 'cobbler'
COBBLER_PASS = 'cobbler'


class CobblerAddDistros(object):
    def __init__(self, log_level, path, name):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        name_list = name.split('-')

        if 'ubuntu' in name_list:
            breed = 'ubuntu'
            for item in name_list:
                if item.lower() == 'amd64':
                    arch = 'x86_64'
                    kernel = (
                        "%s/install/netboot/ubuntu-installer/amd64/linux" %
                        path)
                    initrd = (
                        "%s/install/netboot/ubuntu-installer/amd64/initrd.gz" %
                        path)
                elif item.lower() == 'ppc64el':
                    arch = 'ppc64le'
                    kernel = "%s/install/netboot/vmlinux" % path
                    initrd = "%s/install/netboot/initrd.gz" % path
                elif item.lower().startswith('14.04'):
                    os_version = 'trusty'
            kernel_options = (
                "netcfg/dhcp_timeout=1024 "
                "netcfg/choose_interface=auto "
                "ipv6.disable=1")
            kickstart = "/var/lib/cobbler/kickstarts/%s.seed" % name

        elif ('CentOS' in name_list) or ('RHEL' in name_list):
            breed = 'redhat'
            for item in name_list:
                if item.lower() == 'x86_64':
                    arch = 'x86_64'
                    kernel = "%s/images/pxeboot/vmlinuz" % path
                    initrd = "%s/images/pxeboot/initrd.img" % path
                elif item.lower() == 'ppc64le':
                    arch = 'ppc64le'
                    kernel = "%s/ppc/ppc64/vmlinuz" % path
                    initrd = "%s/ppc/ppc64/initrd.img" % path
                elif item.lower().startswith('7'):
                    os_version = 'rhel7'
            kernel_options = "text"
            kickstart = "/var/lib/cobbler/kickstarts/%s.cfg" % name

        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)

        new_distro_create = cobbler_server.new_distro(token)
        cobbler_server.modify_distro(
            new_distro_create,
            "name",
            name,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "arch",
            arch,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "kernel",
            kernel,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "initrd",
            initrd,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "breed",
            breed,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "os_version",
            os_version,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "kernel_options",
            kernel_options,
            token)
        cobbler_server.save_distro(new_distro_create, token)

        log.info(
            "Cobbler Add Distro: name=%s, path=%s" %
            (name, path))

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
            kickstart,
            token)
        cobbler_server.save_profile(new_profile_create, token)

        log.info(
            "Cobbler Add Profile: name=%s, distro=%s" %
            (name, name))

        cobbler_server.sync(token)
        log.info("Running Cobbler sync")


if __name__ == '__main__':
    """
    Arg1: path to install files
    Arg2: distro name
    Arg3: log level
    """
    log = Logger(__file__)

    ARGV_MAX = 4
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    path = sys.argv[1]
    name = sys.argv[2]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[3]
    else:
        log_level = None

    cobbler_output = CobblerAddDistros(log_level, path, name)
