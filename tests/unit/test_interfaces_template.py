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

import jinja2
import os.path
import unittest


TEMPLATE_FILE = 'playbooks'+os.path.sep+'templates'+os.path.sep+'interfaces.j2'


class TestInterfacesTemplate(unittest.TestCase):

    def test_template(self):
        inv_hn = 'localhost'
        hostvars = {
            "localhost": {
                "host_networks": {
                    "mgmt-net": {
                        "addr": "172.244.5.10"
                    },
                    "stg-net": {
                        "addr": "172.270.200.10"
                    },
                    "br-vlan": {
                        "addr": "0.0.0.0"
                    },
                    "external1": {
                        "addr": "10.5.1.7"
                    },
                    "external2": {}
                }
            }
        }
        networks = {
            "stg-net": {
                "description": "OS storage network description",
                "bridge": "br-storage",
                "method": "static",
                "vlan": 30,
                "eth-port": "eth10",
                "netmask": "255.255.255.252",
                "tcp_segmentation_offload": "off"
            },
            "mgmt-net": {
                "description": "OS mgmt network description",
                "bridge": "br-mgmt",
                "method": "static",
                "vlan": 10,
                "eth-port": "eth10",
                "netmask": "255.255.255.252",
                "tcp_segmentation_offload": "off"
            },
            "br-vlan": {
                "description": "OS vxlan network description",
                "bridge": "br-vlan",
                "method": "static",
                "eth-port": "eth11"
            },
            "external1": {
                "description": "Site network description",
                "network": "10.5.1.0",
                "method": "static",
                "eth-port": "eth10",
                "netmask": "255.255.255.0",
                "dns-search": "myco.domain.com",
                "dns-nameservers": "10.5.1.200",
                "gateway": "10.5.1.1",
                "broadcast": "10.5.1.255"
            },
            "external2": {
                "description": "eth11 10gbit network",
                "method": "manual",
                "eth-port": "eth11"
            }
        }

        template_path, template_file = os.path.split(TEMPLATE_FILE)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                                 trim_blocks=True)
        template = env.get_template(template_file)
        rendered_file = template.render({'networks': networks,
                                         'inventory_hostname': inv_hn,
                                         'hostvars': hostvars})

        # For debugging convenience, we do a line by line compare if the
        # output does not match the expected
        if expected_output_1 != rendered_file:
            expected_lines = expected_output_1.splitlines()
            rendered_lines = rendered_file.splitlines()
            for x in range(len(expected_lines)):
                if expected_lines[x] != rendered_lines[x]:
                    print 'Rendered_file'
                    print rendered_file
                    self.assertEqual(expected_lines[x], rendered_lines[x])
            # Line differences should fail above but if the difference is
            # a different number of lines then fail here:
            if len(expected_lines) != len(rendered_lines):
                print 'Rendered_file'
                print rendered_file
                self.fail('Expected vs rendered line count is different. '
                          'Expected: %s Rendered: %s' % (len(expected_lines),
                                                         len(rendered_lines)))


expected_output_1 = """\
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

# The loopback network interface
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp

# Site network description
auto eth10
iface eth10 inet static
    address 10.5.1.7
    netmask 255.255.255.0
    gateway 10.5.1.1
    network 10.5.1.0
    broadcast 10.5.1.255
    dns-search myco.domain.com
    dns-nameservers 10.5.1.200

# eth11 10gbit network
auto eth11
iface eth11 inet manual




# OS storage network description
iface eth10.30 inet manual
    vlan-raw-device eth10

auto br-storage
iface br-storage inet static
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
    bridge_ports eth10.30
    address 172.270.200.10
    netmask 255.255.255.252
    offload-sg off

# OS mgmt network description
iface eth10.10 inet manual
    vlan-raw-device eth10

auto br-mgmt
iface br-mgmt inet static
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
    bridge_ports eth10.10
    address 172.244.5.10
    netmask 255.255.255.252
    offload-sg off

# OS vxlan network description
auto br-vlan
iface br-vlan inet static
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
    bridge_ports eth11
    address 0.0.0.0

"""

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
