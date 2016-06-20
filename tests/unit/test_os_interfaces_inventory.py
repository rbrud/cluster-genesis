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

import copy
from yggdrasil import os_interfaces_inventory as test_mod
import mock
import unittest

TEST_PKG_MOD = 'yggdrasil.os_interfaces_inventory'


class TestOSInterfacesInventory(unittest.TestCase):

    def test_get_host_ip_to_node(self):
        source = {'nodes': {'type1': [{test_mod.HOST_IP_KEY: 'myIP',
                                       'otherkey': 'otherval1'},
                                      {test_mod.HOST_IP_KEY: 'myIP2',
                                       'otherkey': 'otherval2'},
                                      {test_mod.HOST_IP_KEY: 'myIP3',
                                       'otherkey': 'otherval3'},
                                      {'no_ip_key': 'something',
                                       'otherkey': 'otherval4'}],
                            'type2': [{test_mod.HOST_IP_KEY: 'myIP4',
                                       'otherkey': 'otherval5'},
                                      {test_mod.HOST_IP_KEY: 'myIP5',
                                       'otherkey': 'otherval6'},
                                      {test_mod.HOST_IP_KEY: 'myIP6',
                                       'otherkey': 'otherval7'},
                                      {'no_ip_key': 'something',
                                       'otherkey': 'otherval8'}]
                            }
                  }

        ret = test_mod.get_host_ip_to_node(source)
        expected = {'myIP': {test_mod.HOST_IP_KEY: 'myIP',
                             'otherkey': 'otherval1'},
                    'myIP2': {test_mod.HOST_IP_KEY: 'myIP2',
                              'otherkey': 'otherval2'},
                    'myIP3': {test_mod.HOST_IP_KEY: 'myIP3',
                              'otherkey': 'otherval3'},
                    'myIP4': {test_mod.HOST_IP_KEY: 'myIP4',
                              'otherkey': 'otherval5'},
                    'myIP5': {test_mod.HOST_IP_KEY: 'myIP5',
                              'otherkey': 'otherval6'},
                    'myIP6': {test_mod.HOST_IP_KEY: 'myIP6',
                              'otherkey': 'otherval7'}}
        #self.maxDiff = None
        self.assertDictEqual(ret, expected)

    def test_populate_hosts(self):
        inventory = {'all': {'hosts': [],
                             'vars': {}
                             },
                     '_meta': {'hostvars': {}}
                     }
        hosts = ['a', 'b', 'c']
        test_mod.populate_hosts(inventory, hosts)
        expected = {'all': {'hosts': ['a', 'b', 'c'],
                            'vars': {}
                            },
                    '_meta': {'hostvars': {'a': {'host_networks': {}},
                                           'b': {'host_networks': {}},
                                           'c': {'host_networks': {}}}}}
        self.assertDictEqual(inventory, expected)

    def test_populate_network_variables(self):
        inventory = {'all': {'hosts': [],
                             'vars': {}
                             },
                     '_meta': {'hostvars': {}}
                     }
        expected_output = copy.deepcopy(inventory)
        inv_src = {'networks': {'net1': {'addr': '10.5.1.5/22',
                                         'otherkey': 'otherval'},
                                'net2': {'addr': '0.0.0.0/1',
                                         'otherkey': 'otherval'},
                                'net3':  {'otherkey': 'otherval'}}}
        test_mod.populate_network_variables(inventory, inv_src)
        nets = {'net1': {'network': '10.5.0.0',
                         'netmask': '255.255.252.0',
                         'otherkey': 'otherval'},
                'net2': {'otherkey': 'otherval'},
                'net3': {'otherkey': 'otherval'}}
        expected_output['all']['vars']['networks'] = nets
        #self.maxDiff = None
        self.assertDictEqual(inventory, expected_output)

    def test_populate_host_networks(self):
        # Set up test input
        inventory = {'_meta': {'hostvars': {}}}
        net_list = ['net1', 'net2', 'net3', 'net4']
        ihv = inventory['_meta']['hostvars']
        for x in range(5):
            ihv['nodeIP%s' % x] = {'host_networks': {}}
        ip_to_node = {'nodeIP0': {'net1-addr': '1.1.1.1',
                                  'net2-addr': '2.2.2.1',
                                  'net4-addr': '4.4.4.1'},
                      'nodeIP1': {'net3-addr': '3.3.3.2'},
                      'nodeIP2': {'net1-addr': '1.1.1.3',
                                  'net2-addr': '',
                                  'net3-addr': '3.3.3.3'},
                      'nodeIP3': {'net1-addr': '1.1.1.4',
                                  'net3-addr': '3.3.3.4',
                                  'net4-addr': '4.4.4.4'},
                      'nodeIP4': {'net2-addr': '2.2.2.5',
                                  'net3-addr': '3.3.3.5'}
                      }

        expected_output = copy.deepcopy(inventory)
        hv = expected_output['_meta']['hostvars']
        hv['nodeIP0']['host_networks'] = {'net1': {'addr': '1.1.1.1'},
                                          'net2': {'addr': '2.2.2.1'},
                                          'net4': {'addr': '4.4.4.1'}}
        hv['nodeIP1']['host_networks'] = {'net3': {'addr': '3.3.3.2'}}
        hv['nodeIP2']['host_networks'] = {'net1': {'addr': '1.1.1.3'},
                                          'net2': {},
                                          'net3': {'addr': '3.3.3.3'}}
        hv['nodeIP3']['host_networks'] = {'net1': {'addr': '1.1.1.4'},
                                          'net3': {'addr': '3.3.3.4'},
                                          'net4': {'addr': '4.4.4.4'}}
        hv['nodeIP4']['host_networks'] = {'net2': {'addr': '2.2.2.5'},
                                          'net3': {'addr': '3.3.3.5'}}
        test_mod.populate_host_networks(inventory, net_list, ip_to_node)
        #import json
        #print 'Output %s' % json.dumps(inventory, indent=4)
        #print 'Expected_output %s' % json.dumps(expected_output, indent=4)
        self.assertDictEqual(inventory, expected_output)

    @mock.patch(TEST_PKG_MOD+'.populate_name_interfaces')
    @mock.patch(TEST_PKG_MOD+'.populate_host_networks')
    @mock.patch(TEST_PKG_MOD+'.populate_network_variables')
    @mock.patch(TEST_PKG_MOD+'.populate_hosts')
    @mock.patch(TEST_PKG_MOD+'.get_host_ip_to_node')
    @mock.patch(TEST_PKG_MOD+'.load_input_file')
    def test_generate_dynamic_inventory(self, load, get_host_ip_to_node,
                                        populate_hosts,
                                        populate_network_variables,
                                        populate_host_networks,
                                        populate_name_interfaces):
        ret = test_mod.generate_dynamic_inventory()
        load.assert_any_call()
        get_host_ip_to_node.assert_called_once_with(load.return_value)
        populate_hosts.assert_called_once_with(mock.ANY,
                                               mock.ANY)
        populate_network_variables.assert_called_once_with(mock.ANY,
                                                           load.return_value)
        populate_name_interfaces.assert_called_once_with(
            mock.ANY, load.return_value, get_host_ip_to_node.return_value)
        self.assertTrue(populate_host_networks.called)
        expected_output = {'all': {'hosts': [],
                                   'vars': {}
                                   },
                           '_meta': {'hostvars': {}}}
        self.assertDictEqual(ret, expected_output)

    def test_populate_name_interfaces(self):
        inventory = {'all': {'hosts': ['nodeIP0', 'nodeIP1', 'nodeIP2'],
                             'vars': {}
                             },
                     '_meta': {'hostvars': {'nodeIP0': {},
                                            'nodeIP1': {},
                                            'nodeIP2': {}}}
                     }
        source = {'node-templates': {
            'compute': {
                'name-interfaces': {'mac-key1': 'eth10',
                                    'mac-key2': 'eth20'}},
            'controller': {
                'name-interfaces': {'mac-key1': 'eth30',
                                    'mac-key2': 'eth40'}},
            'osd': {
                'name-interfaces': {'mac-key1': 'eth50',
                                    'mac-key2': 'eth60'}}}}

        ip_to_node = {'nodeIP0': {'mac-key1': 'key1val0',
                                  'mac-key2': 'key2val0',
                                  'template': 'compute'},
                      'nodeIP1': {'mac-key1': 'key1val1',
                                  'mac-key2': 'key2val1',
                                  'template': 'controller'},
                      'nodeIP2': {'mac-key1': 'key1val2',
                                  'mac-key2': 'key2val2',
                                  'template': 'osd'}}

        test_mod.populate_name_interfaces(inventory,
                                          source, ip_to_node)
        hv = inventory['_meta']['hostvars']
        # Verify nodeIP0 vars
        ifs = {'eth10': 'key1val0',
               'eth20': 'key2val0'}
        self.assertEqual(hv['nodeIP0']['name_interfaces'], ifs)
        # Verify nodeIP1 vars
        ifs = {'eth30': 'key1val1',
               'eth40': 'key2val1'}
        self.assertEqual(hv['nodeIP1']['name_interfaces'], ifs)
        # Verify nodeIP2 vars
        ifs = {'eth50': 'key1val2',
               'eth60': 'key2val2'}
        self.assertEqual(hv['nodeIP2']['name_interfaces'], ifs)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
