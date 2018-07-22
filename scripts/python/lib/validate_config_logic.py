#!/usr/bin/env python
"""Config logic validation"""

# Copyright 2018 IBM Corp.
#
# All Rights Reserved.
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

from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals

from netaddr import IPNetwork
import re

from lib.exception import UserException, UserCriticalException


class ValidateConfigLogic(object):
    """Config logic validation

    Args:
        config (object): Config
    """

    CONFIG_VERSION = 'v2.0'

    def __init__(self, config):
        self.config = config
        from lib.config import Config
        # Instantiate Config with supplied config object
        self.cfg = Config(cfg=self.config)
        self.exc = ''

    def _validate_version(self):
        """Validate version

        Exception:
            If config version is not supported
        """

        if self.config.version != self.CONFIG_VERSION:
            self.exc += "Config version '{}' is not supported".format(
                self.config.version)

    def _validate_netmask_prefix(self):
        """Validate netmask and prefix

        The netmask or prefix needs to be specified, but not both.

        Exception:
            If both or neither the netmask and prefix are specified.
        """
        msg_either = "Config 'deployer:' Either 'netmask' or 'prefix' \
            needs to be specified\n"
        msg_both = "Config 'deployer:' Both 'netmask' and 'prefix' can not \
            be specified\n"

        for element in (
                self.config.deployer.networks.mgmt,
                self.config.deployer.networks.client):
            for member in element:
                try:
                    netmask = member.netmask
                except AttributeError:
                    netmask = None
                try:
                    prefix = member.prefix
                except AttributeError:
                    prefix = None

                if netmask is None and prefix is None:
                    self.exc += "%s - %s %s" % (netmask, prefix, msg_either)
                if netmask is not None and prefix is not None:
                    self.exc += "%s - %s %s" % (netmask, prefix, msg_both)

    def _validate_physical_interfaces(self):
        """ Validate that;
            - no data switch ports are specified more than once
            - All physical interfaces reference valid interface definitions
            - All rename values are either 'true' or 'false'
        Exception:
            UserException if any of the above criteria fail
            in config.yml
        """

        def get_dupes(_list):
            found = []
            dupes = []
            for item in _list:
                if item in found:
                    dupes.append(item)
                else:
                    found.append(item)
            return dupes

        def validate_switch_defined(switch):
            global exc
            if switch not in sw_lbls:
                msg = ('\nSwitch "{}" in node template "{}" is not defined.'
                       '\nValid defined switches are: {}\n').format(
                    switch, ntmpl_lbl, sw_lbls)
                self.exc += msg

        def validate_interface_defined(phy_ifc_lbl):
            if phy_ifc_lbl not in ifc_lbls:
                msg = ('\nPhysical interface "{}" in node template "{}" '
                       '\nreferences an undefined interface.')
                self.exc += msg.format(phy_ifc_lbl, ntmpl_lbl)
                self.exc += '\nValid labels are: {}\n'.format(ifc_lbls)

        def _add_ports_to_ports_list(switch, ports):
            if switch in ports_list:
                ports_list[switch] += ports
            else:
                ports_list[switch] = ports

        ifcs = self.cfg.get_interfaces()
        ifc_lbls = []
        for ifc in ifcs:
            ifc_lbls.append(ifc['label'])

        sw_lbls = self.cfg.get_sw_mgmt_label()
        sw_lbls += self.cfg.get_sw_data_label()

        ports_list = {}
        for ntmpl_ind in self.cfg.yield_ntmpl_ind():
            ntmpl_lbl = self.cfg.get_ntmpl_label(ntmpl_ind)
            for phyintf_idx in self.cfg.yield_ntmpl_phyintf_data_ind(ntmpl_ind):
                phy_ifc_lbl = self.cfg.get_ntmpl_phyintf_data_ifc(
                    ntmpl_ind, phyintf_idx)
                validate_interface_defined(phy_ifc_lbl)
                rename = self.cfg.get_ntmpl_phyintf_data_rename(ntmpl_ind, phyintf_idx)
                if rename is not True and rename is not False:
                    msg = ('\nInvalid value for "rename:" ({}) in node template '
                           '"{}", \nphysical interface "{}"').format(
                        rename, ntmpl_lbl, phy_ifc_lbl)
                    msg += '\nValid values are "true" or "false"\n'
                    self.exc += msg
                switch = self.cfg.get_ntmpl_phyintf_data_switch(
                    ntmpl_ind, phyintf_idx)
                validate_switch_defined(switch)
                ports = self.cfg.get_ntmpl_phyintf_data_ports(
                    ntmpl_ind, phyintf_idx)
                _add_ports_to_ports_list(switch, ports)

            for phyintf_idx in self.cfg.yield_ntmpl_phyintf_pxe_ind(ntmpl_ind):
                phy_ifc_lbl = self.cfg.get_ntmpl_phyintf_pxe_interface(
                    ntmpl_ind, phyintf_idx)
                validate_interface_defined(phy_ifc_lbl)
                rename = self.cfg.get_ntmpl_phyintf_pxe_rename(ntmpl_ind, phyintf_idx)
                if rename is not True and rename is not False:
                    msg = ('\nInvalid value for "rename:" ({}) in node template '
                           '"{}", \nphysical interface "{}"').format(
                        rename, ntmpl_lbl, phy_ifc_lbl)
                    msg += '\nValid values are "true" or "false"\n'
                    self.exc += msg
                switch = self.cfg.get_ntmpl_phyintf_pxe_switch(
                    ntmpl_ind, phyintf_idx)
                validate_switch_defined(switch)
                ports = self.cfg.get_ntmpl_phyintf_pxe_ports(
                    ntmpl_ind, phyintf_idx)
                _add_ports_to_ports_list(switch, ports)

            for phyintf_idx in self.cfg.yield_ntmpl_phyintf_ipmi_ind(ntmpl_ind):
                switch = self.cfg.get_ntmpl_phyintf_ipmi_switch(
                    ntmpl_ind, phyintf_idx)
                validate_switch_defined(switch)
                ports = self.cfg.get_ntmpl_phyintf_ipmi_ports(
                    ntmpl_ind, phyintf_idx)
                _add_ports_to_ports_list(switch, ports)

        for switch in ports_list:
            dupes = get_dupes(ports_list[switch])
            if dupes:
                msg = ('\nDuplicate port(s) defined on switch "{}"'
                       '\nDuplicate ports: {}\n'.format(switch, dupes))
                self.exc += msg

    def _validate_deployer_networks(self):
        """ Validate that for each deployer pxe interface and ipmi interface;
            - The container_ipaddr and bridge_ipaddr are in the same subnet.
        """

        self._validate_netmask_prefix()

        netprefix = self.cfg.get_depl_netw_client_prefix()
        cont_ip = self.cfg.get_depl_netw_client_cont_ip()
        br_ip = self.cfg.get_depl_netw_client_brg_ip()
        for i, cip in enumerate(cont_ip):
            netp = netprefix[i]
            bip = br_ip[i]
            cidr_cip = IPNetwork(cip + '/' + str(netp))
            net_c = str(IPNetwork(cidr_cip).network)
            cidr_bip = IPNetwork(bip + '/' + str(netp))
            net_b = str(IPNetwork(cidr_bip).network)
            if net_c != net_b:
                self.exc += ("Config 'deployer: container_ipaddr:' and 'bridge_ipaddr:' "
                             "need to be in the same subnet.\nContainer network {} \n"
                             "Bridge network:   {}".format(net_c, net_b))

        netprefix = self.cfg.get_depl_netw_mgmt_prefix()
        cont_ip = self.cfg.get_depl_netw_mgmt_cont_ip()
        br_ip = self.cfg.get_depl_netw_mgmt_brg_ip()
        for i, cip in enumerate(cont_ip):
            if cip:
                netp = netprefix[i]
                bip = br_ip[i]
                cidr_cip = IPNetwork(cip + '/' + str(netp))
                net_c = str(IPNetwork(cidr_cip).network)
                cidr_bip = IPNetwork(bip + '/' + str(netp))
                net_b = str(IPNetwork(cidr_bip).network)
                if net_c != net_b:
                    self.exc += ("Config 'deployer: container_ipaddr:' and 'bridge_ipaddr:' "
                                 "need to be in the same subnet.\nContainer network {} \n"
                                 "Bridge network:   {}".format(net_c, net_b))

    def _validate_dhcp_lease_time(self):
        """Validate DHCP lease time value

        Lease time can be given as an int (seconds), int + m (minutes),
        int + h (hours) or "infinite".

        Exception:
            Invalid lease time value
        """

        dhcp_lease_time = self.cfg.get_globals_dhcp_lease_time()

        if not (re.match('^\d+[mh]{0,1}$', dhcp_lease_time) or
                dhcp_lease_time == "infinite"):
            exc = ("Config 'Globals: dhcp_lease_time: {}' has invalid value!"
                   "\n".format(dhcp_lease_time))
            exc += ('Value can be in seconds, minutes (e.g. "15m"),\n'
                    'hours (e.g. "1h") or "infinite" (lease does not expire).')
            raise UserException(exc)

    def validate_config_logic(self):
        """Config logic validation"""

        self._validate_version()
        self._validate_physical_interfaces()
        self._validate_deployer_networks()
        self._validate_dhcp_lease_time()

        if self.exc:
            raise UserCriticalException(self.exc)
