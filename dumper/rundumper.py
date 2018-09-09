#/bin/python
# -*- encoding: utf-8 -*-
import importlib
import sys
import os
import logging
import subprocess
from subprocess import PIPE
if len(sys.argv) > 1:
    dbname = sys.argv[1]
else:
    print('no database name provided')
    sys.exit()
verbose = len(sys.argv) > 3
dumper_cmd = len(sys.argv) > 2 and sys.argv[2] or '-d'
SITES_HOME = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
try:
    os.chdir(SITES_HOME + '/config')
    sys.path.insert(0, '.')
    BASE_INFO = {}
    n = 'base_info'
    fun = importlib.import_module(n)
    BASE_INFO.update(getattr(fun, n))
    os.chdir(SITES_HOME)
except:
    print('trying to import base_info from %s/config failed' % SITES_HOME)
    sys.exit()

DATA_HOME = BASE_INFO['erp_server_data_path']
#docker run -it -v /home/robert/odoo_projects_data:/mnt/sites -v /home/robert/erp_workbench/dumper/:/mnt/sites/dumper  --rm=true --link db:db  dbdumper -s
dd = {
    'data_home' : DATA_HOME,
    'sites_home': SITES_HOME,
    'cmd'       : dumper_cmd,
    'dbname'    : dbname,
    'runsudo'   : ''
}
if not os.geteuid() == 0:
    dd['runsudo'] = 'sudo'
if dumper_cmd in ['-h', '-s']:
    cmd_line = '%(runsudo)s docker run -v %(data_home)s:/mnt/sites  -v %(sites_home)s/dumper/:/mnt/sites/dumper --rm=true --link db:db  dbdumper %(cmd)s' % dd
else:
    cmd_line = '%(runsudo)s docker run -v %(data_home)s:/mnt/sites  -v %(sites_home)s/dumper/:/mnt/sites/dumper --rm=true --link db:db  dbdumper %(cmd)s %(dbname)s' % dd
    
(DATA_HOME, SITES_HOME, dumper_cmd, dbname)
if verbose:
    print('--------- rundocker start ----------')
    print(cmd_line)
    cmd_line = cmd_line + ' -v'
p = subprocess.Popen(cmd_line, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
if verbose:
    result =  p.communicate()
    if result:
        errs = result[1].split('\n')
        result = result[0].split('\n')
        for l in result:
            print(l)
        for l in errs:
            print(l)
    print('--------- rundocker end ----------')
else:
    p.communicate()
