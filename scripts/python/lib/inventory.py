import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader


class Inventory():
    INV_CHASSIS_PART_NUMBER = 'chassis-part-number'
    INV_CHASSIS_SERIAL_NUMBER = 'chassis-serial-number'
    INV_MODEL = 'model'
    INV_SERIAL_NUMBER = 'serial-number'
    INV_IPV4_IPMI = 'ipv4-ipmi'
    INV_USERID_IPMI = 'userid-ipmi'
    INV_PASSWORD_IPMI = 'password-ipmi'
    INV_ARCHITECTURE = 'architecture'

    def __init__(self):
        pass

    def load(self, inv_file, log):
        self.inv_path = os.path.abspath(
            os.path.dirname(os.path.abspath(inv_file)) +
            os.path.sep +
            os.path.basename(inv_file))
        try:
            return yaml.load(open(self.inv_path), Loader=AttrDictYAMLLoader)
        except:
            log.error('Could not load inventory file: ' + self.inv_path)
            sys.exit(1)

    def dump(self, inventory, log):
        try:
            yaml.dump(
                inventory,
                open(self.inv_path, 'w'),
                indent=4,
                default_flow_style=False)
        except:
            log.error('Could not dump inventory file: ' + self.inv_path)
            sys.exit(1)
