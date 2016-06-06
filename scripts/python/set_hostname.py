#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
from pyghmi.ipmi import command as ipmi_command

from lib.inventory import Inventory
from lib.logger import Logger

NODES = 'nodes'
HOSTNAME = b'hostname'

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

log = Logger(__file__)
INV_FILE = sys.argv[1]
inv = Inventory()
inventory = inv.load(INV_FILE, log)

node_inv = inventory[NODES]
for inv_key in node_inv:
    node_index = 0
    for i in range(0, len(node_inv[inv_key])):
        if HOSTNAME in node_inv[inv_key][i]:
            if node_inv[inv_key][i][HOSTNAME] is None:
                node_index += 1
                node_inv[inv_key][i][HOSTNAME] = inv_key + str(node_index)
        else:
            node_index += 1
            node_inv[inv_key][i][HOSTNAME] = inv_key + str(node_index)

inv.dump(inventory, log)
