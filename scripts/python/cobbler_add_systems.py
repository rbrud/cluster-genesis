#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
import xmlrpclib

from lib.logger import Logger

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class CobblerAddSystems(object):
    def __init__(self, argv):

        self.log = Logger(__file__)

        ARGV_MAX = 3
        argv_count = len(argv)
        if argv_count > ARGV_MAX:
            try:
                raise Exception()
            except:
                self.log.log_error('Invalid argument count')
                exit(1)

        INV_FILE = argv[1]
        if len(argv) == ARGV_MAX:
            LOG_LEVEL = argv[2]
            self.log.set_level(LOG_LEVEL)

        COBBLER_USER = 'cobbler'
        COBBLER_PASS = 'cobbler'

        YAML_HOSTNAME = 'hostname'
        YAML_IPV4_IPMI = 'ipv4-ipmi'
        YAML_USERID_IPMI = 'userid-ipmi'
        YAML_PASSWORD_IPMI = 'password-ipmi'
        YAML_IPV4_PXE = 'ipv4-pxe'
        YAML_MAC_PXE = 'mac-pxe'

        YAML_COBBLER_PROFILE = 'cobbler-profile'
        YAML_ARCH = 'architecture'
        COBBLER_PROFILE_X86_64 = 'ubuntu-14.04.4-server-amd64'
        COBBLER_PROFILE_PPC64 = 'ubuntu-14.04.4-server-ppc64el'

        inventory = yaml.load(open(sys.argv[1]), Loader=AttrDictYAMLLoader)

        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)

        node_inv = inventory['nodes']

        for inv_key in node_inv:
            for i in range(0, len(node_inv[inv_key])):

                HOSTNAME = node_inv[inv_key][i][YAML_HOSTNAME]
                IPV4_IPMI = node_inv[inv_key][i][YAML_IPV4_IPMI]
                USERID_IPMI = node_inv[inv_key][i][YAML_USERID_IPMI]
                PASSWORD_IPMI = node_inv[inv_key][i][YAML_PASSWORD_IPMI]
                IPV4_PXE = node_inv[inv_key][i][YAML_IPV4_PXE]
                MAC_PXE = node_inv[inv_key][i][YAML_MAC_PXE]

                if YAML_COBBLER_PROFILE in node_inv[inv_key][i]:
                    COBBLER_PROFILE = \
                        node_inv[inv_key][i][YAML_COBBLER_PROFILE]
                elif (YAML_ARCH in node_inv[inv_key][i] and
                        node_inv[inv_key][i][YAML_ARCH] is not None):
                    if node_inv[inv_key][i][YAML_ARCH].lower() == 'x86_64':
                        COBBLER_PROFILE = COBBLER_PROFILE_X86_64
                    elif node_inv[inv_key][i][YAML_ARCH].lower() == 'ppc64':
                        COBBLER_PROFILE = COBBLER_PROFILE_PPC64
                    else:
                        self.log.log_error(
                            'Inventory: Invalid architecture set for ' +
                            HOSTNAME)
                else:
                    COBBLER_PROFILE = COBBLER_PROFILE_X86_64

                new_system_create = cobbler_server.new_system(token)

                cobbler_server.modify_system(
                    new_system_create,
                    "name",
                    HOSTNAME,
                    token)
                cobbler_server.modify_system(
                    new_system_create,
                    "hostname",
                    HOSTNAME,
                    token)
                cobbler_server.modify_system(
                    new_system_create,
                    "power_address",
                    IPV4_IPMI,
                    token)
                cobbler_server.modify_system(
                    new_system_create,
                    "power_user",
                    USERID_IPMI,
                    token)
                cobbler_server.modify_system(
                    new_system_create,
                    "power_pass",
                    PASSWORD_IPMI,
                    token)
                cobbler_server.modify_system(
                    new_system_create,
                    "power_type",
                    "ipmilan",
                    token)
                cobbler_server.modify_system(
                    new_system_create,
                    "profile",
                    COBBLER_PROFILE,
                    token)
                cobbler_server.modify_system(
                    new_system_create,
                    'modify_interface',
                    {
                        "macaddress-eth0": MAC_PXE,
                        "ipaddress-eth0": IPV4_PXE,
                        "dnsname-eth0": HOSTNAME},
                    token)

                cobbler_server.save_system(new_system_create, token)

                self.log.info(
                    "Cobbler Add System: " +
                    "name=" + HOSTNAME + ", " +
                    "profile=" + COBBLER_PROFILE
                    )

        cobbler_server.sync(token)


def main(argv):
    cobbler_output = CobblerAddSystems(argv)

if __name__ == '__main__':
    main(sys.argv)
