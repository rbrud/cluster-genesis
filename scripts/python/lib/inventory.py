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

INV_SWITCHES = 'switches'
INV_MGMT = 'mgmt'
INV_LEAF = 'leaf'
INV_MGMTSWITCH = 'mgmtswitch'
INV_LEAFSWITCH = 'leafswitch'
INV_USERID = 'userid'
INV_PASSWORD = 'password'

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

    def load(self):
        try:
            return yaml.load(open(self.cfg_file), Loader=AttrDictYAMLLoader)
        except:
            self.log.error('Could not load inventory file: ' + self.cfg_file)
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
        cfg = self.load()
        if (CFG_USERID_MGMT_SWITCH in cfg and
            cfg[CFG_USERID_MGMT_SWITCH] is not None):
                userid = cfg[CFG_USERID_MGMT_SWITCH]
        else:
            userid = cfg[CFG_USERID_DEFAULT]
        if (CFG_PASSWORD_MGMT_SWITCH in cfg and
            cfg[CFG_PASSWORD_MGMT_SWITCH] is not None):
               password = cfg[CFG_PASSWORD_MGMT_SWITCH]
        else:
            password = cfg[CFG_PASSWORD_DEFAULT]
        for key in cfg[CFG_IPADDR_MGMT_SWITCH]:
            _dict = AttrDict()
            _list = []
            index = 0
            for _key, _value in key.items():
                index += 1
                _dict[CFG_HOSTNAME] = INV_MGMTSWITCH  + str(index)
                _dict[CFG_IPV4_ADDR] = _value
                _dict[CFG_RACK_ID] = _key
                _dict[INV_USERID] = userid
                _dict[INV_PASSWORD] = password
                _list.append(_dict)
        inv = AttrDict({})
        inv[INV_SWITCHES] = AttrDict({})
        inv[INV_SWITCHES][INV_MGMT] = _list

        cfg = self.load()
        if (CFG_USERID_LEAF_SWITCH in cfg and
            cfg[CFG_USERID_LEAF_SWITCH] is not None):
                userid = cfg[CFG_USERID_LEAF_SWITCH]
        else:
            userid = cfg[CFG_USERID_DEFAULT]
        if (CFG_PASSWORD_LEAF_SWITCH in cfg and
            cfg[CFG_PASSWORD_LEAF_SWITCH] is not None):
               password = cfg[CFG_PASSWORD_LEAF_SWITCH]
        else:
            password = cfg[CFG_PASSWORD_DEFAULT]
        for key in cfg[CFG_IPADDR_LEAF_SWITCH]:
            _dict = AttrDict()
            _list = []
            index = 0
            for _key, _value in key.items():
                index += 1
                _dict[CFG_HOSTNAME] = INV_LEAFSWITCH  + str(index)
                _dict[CFG_IPV4_ADDR] = _value
                _dict[CFG_RACK_ID] = _key
                _dict[INV_USERID] = userid
                _dict[INV_PASSWORD] = password
                _list.append(_dict)
        inv[INV_SWITCHES][INV_LEAF] = _list

        self.dump(inv)
