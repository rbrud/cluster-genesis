#!/usr/bin/python
# Copyright 2016, IBM US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is an ansible dynamic inventory module which loads an inventory file
# describing networks, nodes, and their relationships and outputs ansible
# inventory containing the hosts and network information required to
# allow the configuration of the network interfaces on the nodes.
# An example output of this generation is:
# {
#     "mygroup": {
#         "hosts": [
#             "localhost"
#         ],
#         "vars": {
#             "networks": {
#                 "stg-net": {
#                     "description": "OS storage network description",
#                     "bridge": "br-storage",
#                     "method": "static",
#                     "vlan": 30,
#                     "eth-port": "eth10",
#                     "netmask": "255.255.255.252",
#                     "tcp_segmentation_offload": "off"
#                 },
#                 "mgmt-net": {
#                     "description": "OS mgmt network description",
#                     "bridge": "br-mgmt",
#                     "method": "static",
#                     "vlan": 10,
#                     "eth-port": "eth10",
#                     "netmask": "255.255.255.252",
#                     "tcp_segmentation_offload": "off"
#                 },
#                 "br-vlan": {
#                     "description": "OS vxlan network description",
#                     "bridge": "br-vlan",
#                     "method": "static",
#                     "eth-port": "eth11"
#                 },
#                 "external1": {
#                     "description": "OS storage network description",
#                     "network": "10.5.1.0",
#                     "method": "static",
#                     "eth-port": "eth10",
#                     "netmask": "255.255.255.0",
#                     "dns-search": "myco.domain.com",
#                     "dns-nameservers": "10.5.1.200",
#                     "gateway": "10.5.1.1",
#                     "broadcast": "10.5.1.255"
#                 },
#                 "external2": {
#                     "description": "eth11 10gbit network",
#                     "method": "static",
#                     "eth-port": "eth11"
#                 }
#             }
#         }
#     },
#     "_meta": {
#         "hostvars": {
#             "localhost": {
#                 "host_networks": {
#                     "mgmt-net": {
#                         "addr": "172.244.5.10"
#                     },
#                     "stg-net": {
#                         "addr": "172.270.200.10"
#                     },
#                     "br-vlan": {
#                         "addr": "0.0.0.0"
#                     },
#                     "external1": {
#                         "addr": "10.5.1.7"
#                     },
#                     "external2": {}
#                 },
#                 'template': 'compute',
#                 'name_interfaces': {'eth0': 'mac1',
#                                     'eth1': 'mac2',
#                                     'eth3': 'mac3'}
#             }
#         }
#     }
# }


import argparse
import copy
import json
import netaddr
import sys
import yaml

# The key in on nodes in the source inventory file that contains
# the IP address ansible should use for the host.
HOST_IP_KEY = 'ipv4-pxe'
# The IP address value used when a node needs an interface on the network
# without an IP address assigned.
INPUT_FILE = '/var/oprc/inventory.yml'


def load_input_file():
    with open(INPUT_FILE, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as ex:
            print(ex)
            sys.exit(1)


def get_host_ip_to_node(inventory_source):
    # Process the inventory file and make a map of the IP address ansible
    # will use for the host communication to the node dictionary from
    # the input inventory.
    ip_to_node = {}

    # Flatten the nodes from the inventory into a single list
    nodes = [node for sublist in inventory_source['nodes'].values() for node
             in sublist]
    for node in nodes:
        if HOST_IP_KEY in node:
            ip_to_node[node[HOST_IP_KEY]] = node
    return ip_to_node


def populate_hosts(inventory, hosts):
    # Add the hosts to the all group and add empty dictionaries for host vars
    # host networks
    inventory['all']['hosts'] = hosts
    host_vars = inventory['_meta']['hostvars']
    for host in hosts:
        host_vars[host] = {'host_networks': {}}


def populate_network_variables(inventory, inventory_source):
    # Add the networks from the inventory source into the host_vars
    networks = copy.deepcopy(inventory_source['networks'])
    for network in networks.values():
        # Take the addr out and replace it with the network and the netmask
        addr = network.pop('addr', None)
        if addr:
            ip = netaddr.IPNetwork(addr)
            if ip.prefixlen != 1:
                # We don't put networks in with prefix length == 1 because
                # the inventory file uses this to note that while the host
                # has an interface connected to this network, that interface
                # does not directly get an IP address and the address goes
                # on a bridge.
                network['network'] = str(ip.network)
                network['netmask'] = str(ip.netmask)
    inventory['all']['vars'] = {'networks': networks}


def populate_host_networks(inventory, net_list, ip_to_node):
    hostvars = inventory['_meta']['hostvars']
    for ip, node in ip_to_node.iteritems():
        for net in net_list:
            node_ip_addr = node.get(net+'-addr')
            # If the node is connected to this network
            if node_ip_addr is not None:
                net_addr = {'addr': node_ip_addr}
                # The IP address may be the empty string if the system
                # must have the interface but does not have an IP on the
                # interface, and bridges have the IPs.
                if not net_addr['addr']:
                    net_addr = {}
                hostvars[ip]['host_networks'][net] = net_addr


def populate_name_interfaces(inventory, inventory_source, ip_to_node):
    for ip, node in ip_to_node.iteritems():
        template = inventory_source['node-templates'][node['template']]
        if_name_to_mac = {}
        for mac_key, if_name in template['name-interfaces'].iteritems():
            if_mac = node[mac_key]
            if_name_to_mac[if_name] = if_mac

        inventory['_meta']['hostvars'][ip]['name_interfaces'] = if_name_to_mac


def generate_dynamic_inventory():

    inventory_source = load_input_file()
    ip_to_node = get_host_ip_to_node(inventory_source)
    # initialize the empty inventory
    inventory = {'all': {'hosts': [],
                         'vars': {}
                         },
                 '_meta': {'hostvars': {}}}
    populate_hosts(inventory, ip_to_node.keys())
    populate_network_variables(inventory, inventory_source)
    populate_host_networks(inventory, inventory_source['networks'].keys(),
                           ip_to_node)
    populate_name_interfaces(inventory, inventory_source, ip_to_node)
    return inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host', action='store')
    args = parser.parse_args()
    if args.list:
        inventory = generate_dynamic_inventory()
    else:
        # We don't use the host argument because our inventory
        # returns all host variables in _meta when called with --list.
        # For any other arguments passed, just return this empty inventory.
        inventory = {'_meta': {'hostvars': {}}}

    return json.dumps(inventory)


if __name__ == '__main__':
    print main()
