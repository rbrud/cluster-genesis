#!/usr/bin/env python
# Copyright 2016, IBM US, Inc.

from yggdrasil import allocate_ip_addresses
import types
import unittest


class TestAllocateIPAddresses(unittest.TestCase):

    def test_get_networks(self):
        inv = {'networks': {'net1': {'method': 'static',
                                     'addr': '0.0.0.0/1'},
                            'net2': {'method': 'dhcp',
                                     'addr': '1.2.3.0/22'},
                            'net3': {'method': 'manual'},
                            'net4': {'method': 'static',
                                     'addr': '10.1.1.0/24',
                                     'gateway': '10.1.1.1',
                                     'dns-nameservers': '10.1.1.3'},
                            'net5': {'method': 'static',
                                     'addr': '10.1.1.0/24',
                                     'gateway': '10.1.1.1',
                                     'dns-nameservers': ['10.1.1.3',
                                                         '10.1.1.4']}}}
        nets = allocate_ip_addresses.get_networks(inv)
        self.assertTrue('net1' in nets.keys())
        self.assertEqual(nets['net1']['exclude'], [None])
        self.assertEqual(str(nets['net1']['net'].network), '0.0.0.0')
        self.assertTrue(isinstance(nets['net1']['ip_iterator'],
                                   types.GeneratorType))

        self.assertFalse('net2' in nets.keys())

        self.assertTrue('net3' in nets.keys())
        self.assertFalse('exclude' in nets['net3'])
        self.assertFalse('net' in nets['net3'])

        self.assertTrue('net4' in nets.keys())
        self.assertEqual(nets['net4']['exclude'], ['10.1.1.1', '10.1.1.3'])
        self.assertEqual(str(nets['net4']['net'].network), '10.1.1.0')
        self.assertTrue(isinstance(nets['net4']['ip_iterator'],
                                   types.GeneratorType))

        self.assertTrue('net5' in nets.keys())
        self.assertEqual(nets['net5']['exclude'], ['10.1.1.1', '10.1.1.3',
                                                   '10.1.1.4'])
        self.assertEqual(str(nets['net5']['net'].network), '10.1.1.0')
        self.assertTrue(isinstance(nets['net5']['ip_iterator'],
                                   types.GeneratorType))

    def test_allocate_ips_to_nodes(self):
        inv = {'networks': {'net1': {'method': 'static',
                                     'addr': '0.0.0.0/1'},
                            'net2': {'method': 'dhcp',
                                     'addr': '1.2.3.0/22'},
                            'net3': {'method': 'manual'},
                            'net4': {'method': 'static',
                                     'addr': '10.1.1.0/24',
                                     'gateway': '10.1.1.1',
                                     'dns-nameservers': '10.1.1.3'},
                            'net5': {'method': 'static',
                                     'addr': '10.2.1.0/24',
                                     'gateway': '10.2.1.1',
                                     'dns-nameservers': ['10.2.1.3',
                                                         '10.2.1.4']}}}
        templates = {'controller': {'networks': ['net1', 'net2',
                                                 'net3', 'net4', 'net5']},
                     'compute': {'networks': ['net4', 'net5', 'net1']},
                     'ceph-osd': {'networks': ['net4', 'net5']}}

        nodes = {'controllers': [{'template': 'controller'},
                                 {'template': 'controller'},
                                 {'template': 'controller'}],
                 'compute': [{'template': 'compute'},
                             {'template': 'compute'},
                             {'template': 'compute'}],
                 'ceph-osd': [{'template': 'ceph-osd'},
                              {'template': 'ceph-osd'},
                              {'template': 'ceph-osd'}]}
        inv['nodes'] = nodes
        inv['node-templates'] = templates

        networks = allocate_ip_addresses.get_networks(inv)
        allocate_ip_addresses.allocate_ips_to_nodes(inv, networks)
        expected_nodes = {'controllers': [{'template': 'controller',
                                           'net1-addr': '0.0.0.0',
                                           'net4-addr': '10.1.1.2',
                                           'net5-addr': '10.2.1.2',
                                           'net3-addr': ''},
                                          {'template': 'controller',
                                           'net1-addr': '0.0.0.0',
                                           'net4-addr': '10.1.1.4',
                                           'net5-addr': '10.2.1.5',
                                           'net3-addr': ''},
                                          {'template': 'controller',
                                           'net1-addr': '0.0.0.0',
                                           'net4-addr': '10.1.1.5',
                                           'net5-addr': '10.2.1.6',
                                           'net3-addr': ''}],
                          'ceph-osd': [{'template': 'ceph-osd',
                                        'net4-addr': '10.1.1.6',
                                        'net5-addr': '10.2.1.7'},
                                       {'template': 'ceph-osd',
                                        'net4-addr': '10.1.1.7',
                                        'net5-addr': '10.2.1.8'},
                                       {'template': 'ceph-osd',
                                        'net4-addr': '10.1.1.8',
                                        'net5-addr': '10.2.1.9'}],
                          'compute': [{'template': 'compute',
                                       'net1-addr': '0.0.0.0',
                                       'net4-addr': '10.1.1.9',
                                       'net5-addr': '10.2.1.10'},
                                      {'template': 'compute',
                                       'net1-addr': '0.0.0.0',
                                       'net4-addr': '10.1.1.10',
                                       'net5-addr': '10.2.1.11'},
                                      {'template': 'compute',
                                       'net1-addr': '0.0.0.0',
                                       'net4-addr': '10.1.1.11',
                                       'net5-addr': '10.2.1.12'}],
                          }
#         import json
#         print 'Output %s' % json.dumps(inv, indent=4)
#         print 'Expected_output %s' % json.dumps(expected_nodes, indent=4)
        # self.maxDiff = None
        self.assertEqual(inv['nodes'], expected_nodes)

    def test_allocate_ips_to_nodes_existing_ip(self):
        # Test the allocate code when a node already has an IP
        # on a network.
        inv = {'networks': {'net4': {'method': 'static',
                                     'addr': '10.1.1.0/24',
                                     'gateway': '10.1.1.1',
                                     'dns-nameservers': '10.1.1.3'},
                            'net5': {'method': 'static',
                                     'addr': '10.2.1.0/24',
                                     'gateway': '10.2.1.1',
                                     'dns-nameservers': ['10.2.1.3',
                                                         '10.2.1.4']}}}
        templates = {'controller': {'networks': ['net4', 'net5']}}

        nodes = {'controllers': [{'template': 'controller',
                                  'net4-addr': '10.1.1.15'},
                                 {'template': 'controller',
                                  'net5-addr': '10.2.1.16'},
                                 {'template': 'controller'}]}
        inv['nodes'] = nodes
        inv['node-templates'] = templates

        networks = allocate_ip_addresses.get_networks(inv)
        allocate_ip_addresses.allocate_ips_to_nodes(inv, networks)
        expected_nodes = {'controllers': [{'template': 'controller',
                                           'net4-addr': '10.1.1.15',
                                           'net5-addr': '10.2.1.2'},
                                          {'template': 'controller',
                                           'net4-addr': '10.1.1.2',
                                           'net5-addr': '10.2.1.16'},
                                          {'template': 'controller',
                                           'net4-addr': '10.1.1.4',
                                           'net5-addr': '10.2.1.5'}]}
        # import json
        # print 'Output %s' % json.dumps(inv, indent=4)
        # print 'Expected_output %s' % json.dumps(expected_nodes, indent=4)
        # self.maxDiff = None
        self.assertEqual(inv['nodes'], expected_nodes)


if __name__ == "__main__":
    unittest.main()
