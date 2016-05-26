#!/usr/bin/env python
import sys
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
import xmlrpclib

COBBLER_USER = 'cobbler'
COBBLER_PASS = 'cobbler'

X86_PROFILE = "ubuntu-14.04.4-server-x86_64"

DOMAIN = 'aus.stglabs.ibm.com'

YAML_CHASSIS_SERIAL_NUMBER = 'chassis-serial-number'
YAML_IPV4_ADDR = 'ipv4_addr'
YAML_USERID_IPMI = 'userid-ipmi'
YAML_PASSWORD_IPMI = 'password-ipmi'

inventory = yaml.load(open(sys.argv[1]), Loader=AttrDictYAMLLoader)

cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
token = cobbler_server.login(COBBLER_USER,COBBLER_PASS)

node_inv = inventory['nodes']
for inv_key in node_inv:
    for i in range(0, len(node_inv[inv_key])):
        SERIAL_NUMBER  = node_inv[inv_key][i][YAML_CHASSIS_SERIAL_NUMBER]
        HOSTNAME       = SERIAL_NUMBER + "." + DOMAIN
        IPV4_ADDR_IPMI = node_inv[inv_key][i][YAML_IPV4_ADDR]
        USERID_IPMI    = node_inv[inv_key][i][YAML_USERID_IPMI]
        PASSWORD_IPMI  = node_inv[inv_key][i][YAML_PASSWORD_IPMI]

        new_system_create = cobbler_server.new_system(token)

        cobbler_server.modify_system(new_system_create,"name",SERIAL_NUMBER,token)
        cobbler_server.modify_system(new_system_create,"hostname",HOSTNAME,token)
        cobbler_server.modify_system(new_system_create,'modify_interface', {
                "macaddress-eth0"   : "01:02:03:04:05:0" + str(i),
                "ipaddress-eth0"    : "192.168.3." + str(10 + i),
                "dnsname-eth0"      : HOSTNAME,
        }, token)
        cobbler_server.modify_system(new_system_create,"profile",X86_PROFILE,token)

        cobbler_server.save_system(new_system_create, token)

cobbler_server.sync(token)
