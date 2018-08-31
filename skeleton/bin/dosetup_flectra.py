#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import print_function
import glob
import os
import sys
from subprocess import PIPE, Popen
from optparse import OptionParser
import shutil
import inspect
from collections import OrderedDict

"""
this script creates a new config file for odoo . Use --force to do so.
"""
TAG = '%%s(PROJECT_NAME)%%s' %% (
    '$', '$')  # make sure the tag definition does not replace it self
UTAG = '$(USERNAME)$'

filename = inspect.getframeinfo(inspect.currentframe()).filename
# PROJECT_HOME is the folder in which the project is created
PROJECT_HOME = os.path.split(os.path.dirname(os.path.abspath(filename)))[0]
# PROJECT_LIST_DIR the folder that houses all projects
PROJECT_LIST_DIR = os.path.split(os.path.split(PROJECT_HOME)[0])[0]

# the LOGIN_FILE is a config file skeleton that was used for creating
# a buildout.cfg file
# It is created by ooin's bin/c -c PROJECT_NAME
# and contains lines like
# odoo_version = 1.1.0
# db_name = psytex
LOGIN_FILE = '%%s/login_info.cfg.in' %% PROJECT_HOME
OUT_FILE = '%%s/etc/flectra.conf' %% PROJECT_HOME
BASE_TAG_FILE = 'etc/tmp.cfg'
# we have to find out what library path to use
cmd = ['/bin/bash', '-c', 'echo $(which python)']
p = Popen(cmd, stdout=PIPE, stderr=PIPE)
LIB_DIR = str(os.path.normpath(p.communicate()[0]).strip()).decode('utf-8')
# now hunt for the actual libraries
# when we find python at /home/robert/.virtualenvs/fruba/bin/python
# the library is probably at /home/robert/.virtualenvs/fruba/lib/python2.7/site-packages/odoo/addons
#                            /home/robert/.virtualenvs/fruba/lib/python2.7/site-packages/odoo/addons'
LIB_DIR = os.path.sep.join(LIB_DIR.split(os.path.sep)[:-2])
LIB_DIR = '%%s/lib/python2.7/site-packages' %% LIB_DIR
# what tags will we be lookin for in LOGIN_FILE
TAGS = [
    'addons_path',
    'admin_passwd',
    'create_database',
    'current_user',
    'data_dir',
    'db_host',
    'db_name',
    'dbfilter',
    'db_password',
    'log_db_level',
    'odoo_version',
    'without_demo',
    
]
SKIP_TAGS = [
    'http_port',
    'xmlrpc_port'
]

class bcolors:
    """
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def collect_tags(tags_dic, _tags=TAGS):
    """
    [summary]
    collects values from LOGIN_FILE

    Arguments:
        tags OrderedDict -- return collected values 
    """
    result = {}
    with open(LOGIN_FILE, 'r') as fh:
        last_tag = ''
        tag_parts = []
        for line in fh.readlines():
            # skip comments and section headers
            line = line.strip()
            if not line:
                continue
            if line[0] in ['#', '[']:
                # if last_tag is set, we must handle it
                if last_tag:
                    """addons_path =
                        local psytex_addons/
                        local /home/robert/odoo_instances/psytex/addons
                    """
                    tag_line = ''
                    for tag_part in tag_parts:
                        if not tag_part.strip():
                            continue
                        lparts = tag_part.split(' ')
                        if not lparts[0] == 'local':
                            continue  # we know only how to handle local
                        if tag_line:
                            tag_line += ','
                        if lparts[1].startswith('/'):
                            tag_line += lparts[1]
                        else:
                            tag_line += ('%%s/%%s' %% (PROJECT_HOME, lparts[1]))
                    if tag_line:
                        result[last_tag] = tag_line
                    tag_line = ''
                    last_tag = ''
                    tag_parts = []
                continue
            # addons_path does span multiple lines
            if '=' in line:
                parts = [p.strip() for p in line.split('=') if p.strip()]
                if len(parts) == 2:
                    # db_name = psytex
                    last_tag = ''
                    result[parts[0]] = parts[1]
                    continue
                # this is something like:
                # addons_path =
                last_tag = parts[0]
                continue
            if line:
                tag_parts.append(line)
    # now all lines in the LOGIN_FILE are handled
    # we can fill the tags dict
    for tag in _tags:
        v = result.get(tag)
        if v:
            tags_dic[tag] = v

def make_base_config_file(tags):
    # create a new cofig file to learn the base addon path
    base_tags = OrderedDict()
    btfn = BASE_TAG_FILE
    cmd = ['bin/flectra-bin', '-s', '-c', btfn, '--stop-after-ini']
    print('create base config')
    p = Popen(cmd, stdout=PIPE)
    p.communicate()
    with open(btfn, 'r') as in_file:
        for line in in_file.readlines():
            if ' = ' in line:
                k,v = line.split(' = ')[:2]
                base_tags[k] = v
            
    with open(OUT_FILE, 'w') as fh:
        fh.write('[options]\n')
        xmlrpc_port_seen = False
        for k, v in tags.items():
            if k == 'addons_path':
                #v = '%%(ph)s/odoo/addons,' %% {'ph': LIB_DIR} + v
                v = base_tags[k].strip() + ',' + v.strip()
            fh.write('%%s = %%s\n' %% (k, v))
            if k == 'xmlrpc_port':
                xmlrpc_port_seen = True
        if not xmlrpc_port_seen:
            fh.write('xmlrpc_port = 8069\n')
        # now write out the rest
        keys = list(tags.keys()) + SKIP_TAGS
        for k,v in base_tags.items():
            if k in keys:
                continue
            fh.write('%%s = %%s' %% (k, v))
    
def main(opts):  # nosetup=False, onlysetup=False):
    """
    we want to create a odoo config file
    the variables and their values we find in login_info.cfg.in
    """
    print(PROJECT_HOME)
    PROJECT_NAME = os.path.split(PROJECT_HOME)[-1]
    # create folder for odoo_addons
    try:
        os.mkdir('%%s_addons' %% PROJECT_NAME)
    except:
        pass  # allready exists
    tags = OrderedDict()
    collect_tags(tags)
    if not os.path.exists('%%s/etc/' %% PROJECT_HOME):
        os.mkdir('%%s/etc/' %% PROJECT_HOME)
    make_base_config_file(tags)            


if __name__ == '__main__':
    usage = "dosetup_flectra.py -h for help on usage"
    parser = OptionParser(usage=usage)
    # parser.add_option(
    #     "-i", "--ignores",
    #     action="store_true", dest="ignores", default=False,
    #     help = 'set svn:ignores'
    # )
    parser.add_option(
        "-f", "--force",
        action="store_true", dest="force", default=False,
        help='f is not used for flectra'
    )

    (opts, args) = parser.parse_args()
    main(opts)  # opts.noinit, opts.initonly)
