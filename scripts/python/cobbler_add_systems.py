#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
import xmlrpclib

from lib.logger import Logger

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


class CobblerAddSystems(object):
    def __init__(self, log_level, inv_file, cfg_file):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)

        inv = Inventory(log_level, inv_file, cfg_file)

        for node_inv, INV_NODES, key, index, node in inv.yield_nodes():
           hostname = node_inv[key][index][YAML_HOSTNAME]
           ipv4_ipmi = node_inv[key][index][YAML_IPV4_IPMI]
           userid_ipmi = node_inv[key][index][YAML_USERID_IPMI]
           password_ipmi = node_inv[key][index][YAML_PASSWORD_IPMI]
           ipv4_pxe = node_inv[key][index][YAML_IPV4_PXE]
           mac_pxe = node_inv[key][index][YAML_MAC_PXE]

           if YAML_COBBLER_PROFILE in node_inv[key][index]:
               COBBLER_PROFILE = \
                   node_inv[key][index][YAML_COBBLER_PROFILE]
           elif (YAML_ARCH in node_inv[key][index] and
                   node_inv[key][index][YAML_ARCH] is not None):
               if node_inv[key][index][YAML_ARCH].lower() == 'x86_64':
                   COBBLER_PROFILE = COBBLER_PROFILE_X86_64
               elif node_inv[key][index][YAML_ARCH].lower() == 'ppc64':
                   COBBLER_PROFILE = COBBLER_PROFILE_PPC64
               else:
                   self.log.log_error(
                       'Inventory: Invalid architecture set for ' +
                       hostname)
           else:
               COBBLER_PROFILE = COBBLER_PROFILE_X86_64

           new_system_create = cobbler_server.new_system(token)

           cobbler_server.modify_system(
               new_system_create,
               "name",
               hostname,
               token)
           cobbler_server.modify_system(
               new_system_create,
               "hostname",
               hostname,
               token)
           cobbler_server.modify_system(
               new_system_create,
               "power_address",
               ipv4_ipmi,
               token)
           cobbler_server.modify_system(
               new_system_create,
               "power_user",
               userid_ipmi,
               token)
           cobbler_server.modify_system(
               new_system_create,
               "power_pass",
               password_ipmi,
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
                   "macaddress-eth0": mac_pxe,
                   "ipaddress-eth0": ipv4_pxe,
                   "dnsname-eth0": hostname},
               token)

           cobbler_server.save_system(new_system_create, token)

           self.log.info(
               "Cobbler Add System: " +
               "name=" + hostname + ", " +
               "profile=" + COBBLER_PROFILE
               )

        cobbler_server.sync(token)

if __name__ == '__main__':
    """
    Arg1: config file
    Arg2: inventory file
    Arg3: log level
    """
    log = Logger(__file__)

    ARGV_MAX = 3
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    cfg_file = sys.argv[1]
    inv_file = sys.argv[2]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[3]
    else:
        log_level = None

    cobbler_output = CobblerAddSystems(log_level, inv_file, cfg_file)
