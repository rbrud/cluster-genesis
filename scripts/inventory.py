#!/usr/bin/env python
import yaml
import json
import sys

f = open(sys.argv[1])
inventory = yaml.safe_load(f)
f.close()
print(inventory)
