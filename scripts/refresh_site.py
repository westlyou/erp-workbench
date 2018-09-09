#/bin/python
# -*- encoding: utf-8 -*-
import importlib
import sys
import os
import logging
import subprocess
from subprocess import PIPE
from argparse import ArgumentParser

SITES_HOME = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
sys.path.insert(0, SITES_HOME)
from config import SITES, BASE_INFO

DATA_HOME = BASE_INFO['erp_server_data_path']
#docker run -it -v /home/robert/odoo_projects_data:/mnt/sites -v /home/robert/erp_workbench/dumper/:/mnt/sites/dumper  --rm=true --link db:db  dbdumper -s
#dd = {
    #'data_home' : DATA_HOME,
    #'sites_home': SITES_HOME,
    #'cmd'       : dumper_cmd,
    #'dbname'    : dbname,
    #'runsudo'   : ''
#}


# bin/c docker -duo all  afbstest -skip afbs_survey,partner_firstname,mapper,afbs_workgroups
 
def main(opts, site_name):
    site = SITES.get(site_name)
    dev = site.get('develop', {}).get('addons', ['all'])
    load_first= site.get('develop', {}).get('load_first', [])
    dev = ','.join(dev)
    first = []
    # chdir into root of ..
    os.chdir(SITES_HOME)
    docker = []
    if opts.no_docker:
        if load_first:
            first = ['bin/c -uo %s %s' % (','.join(load_first),site_name) ]
    
        cmdlines = [
            #['bin/c -m %s' % site_name],
            first,
            ['bin/c -uo %s %s' % (dev ,site_name) ]
        ]
    else:
        if load_first:
            first = ['bin/c docker -duo %s %s' % (','.join(load_first),site_name) ]
        cmdlines = [
            ['bin/c -m %s' % site_name],
            ['bin/c docker -drs %s' % site_name],
            first,
            ['bin/c docker -duo %s %s' % (dev ,site_name) ]
        ]
        
    for cmd_line in cmdlines:
        p = subprocess.Popen(
            cmd_line,
            stdout=PIPE,
            env=dict(os.environ, PGPASSWORD=pw,  PATH='/usr/bin'),
            shell=shell)
        print(p.communicate())
    
if __name__ == '__main__':
    usage = "drefresh.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument("-n", "--no-docker",
                        action="store_true", dest="no_docker", default=False,
                        help="do not use docker")

    parser.add_argument("-s", "--skip",
                        action="store", dest="skip", default='',
                        help="skip list of addons")

    opts = parser.parse_args()
    args, unknownargs = parser.parse_known_args()
    if not unknownargs:
        print('need name of site')
        sys.exit()
    site_name = unknownargs[0]
    if not SITES.get(site_name):
        '%s is not a know site' % site_name
        sys.exit()
    pp = os.path.normpath('%s/%s' % (BASE_INFO.get('erp_server_data_path'), site_name))
    if not os.path.exists(pp) and os.path.isdir(pp):
        print('%s does not point to a valid site sctructure' % pp)
        sys.exit()
    main(args, site_name)
#
