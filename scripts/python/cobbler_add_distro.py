#!/usr/bin/env python
from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
import xmlrpclib

from lib.logger import Logger

class Ipmi(object):
    def __init__(self, argv):
        self.log = Logger(__file__)

        ARGV_MAX = 6
        argv_count = len(sys.argv)
        if argv_count > ARGV_MAX:
            try:
                raise Exception()
            except:
                self.log.error('Invalid argument count')
                exit(1)
        
        INV_FILE = sys.argv[1]
        PATH     = sys.argv[2]
        NAME     = sys.argv[3]
        ARCH     = sys.argv[4]
        
        if ARCH == "amd64":
            ARCH = "x86_64"
        
        if len(sys.argv) == ARGV_MAX:
            LOG_LEVEL = sys.argv[5]
            self.log.set_level(LOG_LEVEL)
        
        COBBLER_USER = 'cobbler'
        COBBLER_PASS = 'cobbler'
        
        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER,COBBLER_PASS)
        
        options = {
            "name"  : NAME,
            "path"  : PATH,
            "arch"  : ARCH
        }
        
        import_output = cobbler_server.background_import(options,token)
        self.log.info(
            "Running Cobbler import on mounted dir: " + 
            options["path"]
            )
        
        cobbler_server.sync(token)
        self.log.info("Running Cobbler sync")

def main(argv):
    ipmi_data = Ipmi(argv)

if __name__ == '__main__':
    main(sys.argv)
