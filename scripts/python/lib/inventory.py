import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
from orderedattrdict import AttrDict


CFG_IPADDR_MGMT_SWITCH = 'ipaddr-mgmt-switch'
CFG_IPADDR_LEAF_SWITCH = 'ipaddr-leaf-switch'
CFG_HOSTNAME = 'hostname'
CFG_IPV4_ADDR = 'ipv4-addr'
CFG_USERID_DEFAULT = 'userid-default'
CFG_PASSWORD_DEFAULT = 'password-default'
CFG_USERID_MGMT_SWITCH = 'userid-mgmt-switch'
CFG_PASSWORD_LEAF_SWITCH = 'password-leaf-switch'
CFG_USERID_LEAF_SWITCH = 'userid-leaf-switch'
CFG_PASSWORD_MGMT_SWITCH = 'password-mgmt-switch'
CFG_RACK_ID = 'rack-id'
CFG_NODES_TEMPLATES = 'nodes_templates'
CFG_IPMI_PORTS = 'ipmi-ports'

INV_SWITCHES = 'switches'
INV_MGMT = 'mgmt'
INV_LEAF = 'leaf'
INV_MGMTSWITCH = 'mgmtswitch'
INV_LEAFSWITCH = 'leafswitch'
INV_USERID = 'userid'
INV_PASSWORD = 'password'
INV_NODES = 'nodes'
INV_HOSTNAME = 'hostname'
INV_PORT_IPMI = 'port-ipmi'
INV_IPV4_IPMI = 'ipv4-ipmi'
INV_MAC_IPMI = 'mac-ipmi'
INV_RACK_ID = 'rack-id'


class Inventory():
    INV_CHASSIS_PART_NUMBER = 'chassis-part-number'
    INV_CHASSIS_SERIAL_NUMBER = 'chassis-serial-number'
    INV_MODEL = 'model'
    INV_SERIAL_NUMBER = 'serial-number'
    INV_IPV4_IPMI = 'ipv4-ipmi'
    INV_USERID_IPMI = 'userid-ipmi'
    INV_PASSWORD_IPMI = 'password-ipmi'
    INV_ARCHITECTURE = 'architecture'

    def __init__(self, cfg_file, inv_file, log):
        self.log = log
        self.cfg_file = self._get_abs_path(cfg_file)
        self.inv_file = self._get_abs_path(inv_file)

    @staticmethod
    def _get_abs_path(file):
        return os.path.abspath(
            os.path.dirname(os.path.abspath(file)) +
            os.path.sep +
            os.path.basename(file))

    def load(self, file):
        try:
            return yaml.load(open(file), Loader=AttrDictYAMLLoader)
        except:
            self.log.error('Could not load file: ' + file)
            sys.exit(1)

    def dump(self, inventory):
        try:
            yaml.dump(
                inventory,
                open(self.inv_file, 'w'),
                indent=4,
                default_flow_style=False)
        except:
            self.log.error('Could not dump inventory file: ' + self.inv_file)
            sys.exit(1)

    def add_switches(self):
        self.cfg = self.load(self.cfg_file)
        if (CFG_USERID_MGMT_SWITCH in self.cfg and
                self.cfg[CFG_USERID_MGMT_SWITCH] is not None):
                userid = self.cfg[CFG_USERID_MGMT_SWITCH]
        else:
            userid = self.cfg[CFG_USERID_DEFAULT]
        if (CFG_PASSWORD_MGMT_SWITCH in self.cfg and
                self.cfg[CFG_PASSWORD_MGMT_SWITCH] is not None):
                password = self.cfg[CFG_PASSWORD_MGMT_SWITCH]
        else:
            password = self.cfg[CFG_PASSWORD_DEFAULT]
        for key in self.cfg[CFG_IPADDR_MGMT_SWITCH]:
            _dict = AttrDict()
            _list = []
            index = 0
            for _key, _value in key.items():
                index += 1
                _dict[CFG_HOSTNAME] = INV_MGMTSWITCH + str(index)
                _dict[CFG_IPV4_ADDR] = _value
                _dict[CFG_RACK_ID] = _key
                _dict[INV_USERID] = userid
                _dict[INV_PASSWORD] = password
                _list.append(_dict)
        inv = AttrDict({})
        inv[INV_SWITCHES] = AttrDict({})
        inv[INV_SWITCHES][INV_MGMT] = _list

        if (CFG_USERID_LEAF_SWITCH in self.cfg and
                self.cfg[CFG_USERID_LEAF_SWITCH] is not None):
                userid = self.cfg[CFG_USERID_LEAF_SWITCH]
        else:
            userid = self.cfg[CFG_USERID_DEFAULT]
        if (CFG_PASSWORD_LEAF_SWITCH in self.cfg and
                self.cfg[CFG_PASSWORD_LEAF_SWITCH] is not None):
                password = self.cfg[CFG_PASSWORD_LEAF_SWITCH]
        else:
            password = self.cfg[CFG_PASSWORD_DEFAULT]
        for key in self.cfg[CFG_IPADDR_LEAF_SWITCH]:
            _dict = AttrDict()
            _list = []
            index = 0
            for _key, _value in key.items():
                index += 1
                _dict[CFG_HOSTNAME] = INV_LEAFSWITCH + str(index)
                _dict[CFG_IPV4_ADDR] = _value
                _dict[CFG_RACK_ID] = _key
                _dict[INV_USERID] = userid
                _dict[INV_PASSWORD] = password
                _list.append(_dict)
        inv[INV_SWITCHES][INV_LEAF] = _list

        self.dump(inv)

    def yield_mgmt_rack_ipv4(self):
        self.cfg = self.load(self.cfg_file)
        for switch in self.cfg[CFG_IPADDR_MGMT_SWITCH]:
            for key, value in switch.items():
                yield key, value

    def create_nodes(self, dhcp_mac_ip, mgmt_switch_config):
        self.cfg = self.load(self.cfg_file)
        inv = self.load(self.inv_file)
        inv[INV_NODES] = None
        _dict = AttrDict()
        for key, value in self.cfg[CFG_NODES_TEMPLATES].items():
            index = 0
            for rack, ipmi_ports in value[CFG_IPMI_PORTS].items():
                _list = []
                for ipmi_port in ipmi_ports:
                    for mgmt_port in mgmt_switch_config[rack]:
                        if ipmi_port in mgmt_port.keys():
                            if mgmt_port[ipmi_port] in dhcp_mac_ip:
                                node_dict = AttrDict()
                                if (CFG_HOSTNAME not in value or
                                        value[CFG_HOSTNAME] is None):
                                    node_dict[INV_HOSTNAME] = key
                                else:
                                    node_dict[INV_HOSTNAME] = \
                                        value[CFG_HOSTNAME]
                                index += 1
                                node_dict[INV_HOSTNAME] += '-' + str(index)
                                node_dict[INV_PORT_IPMI] = ipmi_port
                                node_dict[INV_IPV4_IPMI] = \
                                    dhcp_mac_ip[mgmt_port[ipmi_port]]
                                node_dict[INV_MAC_IPMI] = mgmt_port[ipmi_port]
                                node_dict[INV_RACK_ID] = rack
                                _list.append(node_dict)
                                _dict[key] = _list
                                inv[INV_NODES] = _dict

        self.dump(inv)
