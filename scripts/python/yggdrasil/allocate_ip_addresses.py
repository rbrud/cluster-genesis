#!/usr/bin/env python
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

import argparse
import netaddr
from orderedattrdict import yamlutils
import sys
import yaml


def load_input(inventory_file):
    with open(inventory_file, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yamlutils.AttrDictYAMLLoader)

        except yaml.YAMLError as ex:
            print(ex)
            sys.exit(1)


def save_inventory(inventory, inventory_file):
    stream = file(inventory_file, 'w')
    yaml.dump(inventory, stream, default_flow_style=False, explicit_start=True)


def get_networks(inventory):
    networks = inventory['networks']
    nets = {}
    for net_name, net in networks.iteritems():
        method = net.get('method')
        address = net.get('addr')
        if address and method == 'static':
            # We will process this network since it has static IPs
            # and a network address provided.
            # We get a list of IPs to exclude from the generation
            exclude_addrs = [net.get('gateway')]
            dns = net.get('dns-nameservers')
            if dns:
                if type(dns) is list:
                    exclude_addrs = exclude_addrs + dns
                else:
                    exclude_addrs.append(dns)

            ip_net = netaddr.IPNetwork(address)
            nets[net_name] = {'net': ip_net,
                              'ip_iterator': ip_net.iter_hosts(),
                              'exclude': exclude_addrs}
        elif method == 'manual':
            nets[net_name] = {'manual_addr': ''}
    return nets


def allocate_ips_to_nodes(inventory, networks):
    # Flatten the nodes from the inventory into a single list
    nodes = [node for sublist in inventory['nodes'].values() for node
             in sublist]

    templates = inventory['node-templates']

    for node in nodes:
        template = templates[node['template']]
        for node_net in template['networks']:
            if node_net not in networks.keys():
                continue
            node_ip_key = '%s-addr' % node_net
            if node.get(node_ip_key) is not None:
                print ('Node %(node_name)s already has IP address %(addr)s'
                       ' assigned on network %(net)s.  This IP assignment'
                       ' will not be changed.'
                       ) % {'node_name': node.get('hostname'),
                            'addr': node.get(node_ip_key),
                            'net': node_net}
                continue
            if 'manual_addr' in networks[node_net]:
                ip = networks[node_net]['manual_addr']
            elif str(networks[node_net]['net'].network) == '0.0.0.0':
                # Some vlan bridges just use 0.0.0.0 in the interfaces file
                ip = '0.0.0.0'
            else:
                ip = get_next_ip(networks[node_net])
            node[node_ip_key] = ip


def get_next_ip(network):
    ip = str(network['ip_iterator'].next())
    while ip in network['exclude']:
        ip = str(network['ip_iterator'].next())

    return ip


def allocate_ips(inventory):
    inv = load_input(inventory)
    nets = get_networks(inv)
    allocate_ips_to_nodes(inv, nets)
    save_inventory(inv, inventory)


def main():

    parser = argparse.ArgumentParser(
        description=('Allocates IP addresses on nodes in an inventory file.'),
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--inventory',
                        dest='inventory_file',
                        required=True,
                        help='The path to the inventory file.')

    # Handle error cases before attempting to parse
    # a command off the command line
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    allocate_ips(args.inventory_file)

if __name__ == "__main__":
    main()
