#!/usr/bin/env python
import yaml
import json
f = open('inventory.yml')
inventory = yaml.safe_load(f)
f.close()
print(json.dumps(../playbooks/inventory/inventory.yml, indent=4))
