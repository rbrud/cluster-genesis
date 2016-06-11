#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader

ARGV_MAX = 3
argv_count = len(sys.argv)
if argv_count > ARGV_MAX:
    try:
        raise Exception()
    except:
        print('Invalid argument count')
        exit(1)


def abs_path(file):
    return os.path.abspath(
        os.path.dirname(os.path.abspath(file)) +
        os.path.sep +
        os.path.basename(file))

yaml_file = abs_path(sys.argv[1])

try:
    content = yaml.load(open(yaml_file), Loader=AttrDictYAMLLoader)
except:
    print('Could not load file: ' + yaml_file)
    sys.exit(1)

if len(sys.argv) == ARGV_MAX:
    yaml_file = abs_path(sys.argv[2])

try:
    yaml.dump(
        content,
        open(yaml_file, 'w'),
        indent=4,
        default_flow_style=False)
except:
    print('Could not dump file: ' + yaml_file)
    sys.exit(1)
