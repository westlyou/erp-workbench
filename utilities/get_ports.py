#!bin/python
# -*- encoding: utf-8 -*-

import sys
import os
from pprint import pprint
# from name_completer import SimpleCompleter
sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
from scripts.bcolors import bcolors
from sites_list.sites_global import SITES_G
server_map = {
    None : 'undefined',
    'xx.xx.xx.xx'   : 'undefined',
    'localhost'     : 'localhost',
    '127.0.0.1'     : 'localhost',
    '144.76.184.20' : 'frieda',
    '176.9.142.21'  : 'alice2',
    '195.48.80.84'  : 'kinesys',
    '88.198.51.174' : 'lisa',
}
result = {}
for k, v in list(SITES_G.items()):
    remote_url = server_map[v.get('remote_server', {}).get('remote_url')]
    if not 'remote_url':
        continue
    docker = v.get('docker')
    if not docker:
        continue
    result_list = result.get(remote_url, [])
    result_list.append([docker.get('odoo_port'), docker.get('container_name')])
    result_list.sort()
    result[remote_url] = result_list
pprint(result)
    
    