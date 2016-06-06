#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
import xmlrpclib

from lib.logger import Logger

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

class Ipmi(object):
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
        
        X86_PROFILE = "ubuntu-14.04.4-server-x86_64"
        
        DOMAIN = 'aus.stglabs.ibm.com'
        
        YAML_CHASSIS_SERIAL_NUMBER = 'chassis-serial-number'
        YAML_IPV4_IPMI             = 'ipv4_ipmi'
        YAML_USERID_IPMI           = 'userid-ipmi'
        YAML_PASSWORD_IPMI         = 'password-ipmi'
        
        inventory = yaml.load(open(sys.argv[1]), Loader=AttrDictYAMLLoader)
        
        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER,COBBLER_PASS)
        
        node_inv = inventory['nodes']
        
        for inv_key in node_inv:
            for i in range(0, len(node_inv[inv_key])):
                NAME           = inv_key + "{0:0=2d}".format(i+1)
                HOSTNAME       = NAME + "." + DOMAIN
                SERIAL_NUMBER  = node_inv[inv_key][i][YAML_CHASSIS_SERIAL_NUMBER]
                IPV4_ADDR_IPMI = node_inv[inv_key][i][YAML_IPV4_IPMI]
                USERID_IPMI    = node_inv[inv_key][i][YAML_USERID_IPMI]
                PASSWORD_IPMI  = node_inv[inv_key][i][YAML_PASSWORD_IPMI]
        
                new_system_create = cobbler_server.new_system(token)
        
                cobbler_server.modify_system(new_system_create,"name",NAME,token)
                cobbler_server.modify_system(new_system_create,"hostname",HOSTNAME,token)
                cobbler_server.modify_system(new_system_create,'modify_interface', {
                        "macaddress-eth0"   : "01:02:03:04:05:0" + str(i),
                        "ipaddress-eth0"    : "192.168.3." + str(10 + i),
                        "dnsname-eth0"      : HOSTNAME,
                }, token)
                cobbler_server.modify_system(new_system_create,"profile",X86_PROFILE,token)
        
                cobbler_server.save_system(new_system_create, token)
        
                self.log.info(
                    "Cobbler Add System: " +
                    "name=" + SERIAL_NUMBER + ", " +
                    "hostname=" + HOSTNAME
                    )
        
        cobbler_server.sync(token)

def main(argv):
    ipmi_data = Ipmi(argv)

if __name__ == '__main__':
    main(sys.argv)
