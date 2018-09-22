#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import print_function
import os
import sys
from subprocess import PIPE, Popen
from optparse import OptionParser
from dosetup_odoo import collect_tags, PROJECT_HOME
from collections import OrderedDict
import zipfile
import shutil
from dosetup_odoo import make_base_config_file

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

TAGS = [
    'erp_version',
    'erp_minor',
    'erp_nightly',
]

# to find executable python


def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))


def main(opts):  # nosetup=False, onlysetup=False):
    """
    we want to create an odoo instance
    the variables and their values we find in login_info.cfg.in
    """
    print(PROJECT_HOME)
    PROJECT_NAME = os.path.split(PROJECT_HOME)[-1]
    # create folder for odoo_addons
    try:
        os.mkdir('downloads')
    except:
        pass  # allready exists
    tags = OrderedDict()
    collect_tags(tags, TAGS)
    VERSION = tags.get('erp_version')
    ODOO_MINOR = tags.get('erp_minor', '')
    NIGHTLY = tags.get('erp_nightly', '')
    # the following line would read something like
    # erp_version : '11.0' -> will become '11'
    # erp_minor: '.0' <-- will be wrapped into version
    # erp_nightly : '', defaults to version, can be either 'version + minor' or 'master'
    # https://nightly.odoo.com/ODOO_VERSION+ODO_MINOR/nightly/src/odoo_ODOO_VERSIONODOO_MINOR.latest.zip
    # https://nightly.odoo.com/11.0/nightly/src/odoo_11.0.latest.zip
    # erp_version : '12' 
    # erp_minor: .0alpha1' 
    # erp_nightly : 'master', 
    # https://nightly.odoo.com/master/nightly/src/odoo_12.0alpha1.latest.zip
    
    # first calculate the elements
    if VERSION.find('.') > 0:
        # we assume it to be something like '11.0
        NIGHTLY = VERSION
        ODOO_MINOR = ''
    else:
        # we could build a combination of version and minor
        try:
            float(minor)
            NIGHTLY = VERSION + ODOO_MINOR
        except:
            #we probably have an alpha version
            pass

    erp_src = 'https://nightly.odoo.com/%%s/nightly/src/odoo_%%s%%s.latest.zip' %% (
        NIGHTLY, VERSION, ODOO_MINOR)
    fname = os.path.split(erp_src)[-1]
    python_cmd = ''

    # delete an existing download if force is activated
    if opts.force:
        try:
            os.unlink('downloads/%%s' %% fname)
        except:
            pass
    # do the download
    adir = os.getcwd()
    os.chdir('downloads')
    if not os.path.exists(fname):
        cmd = ['wget', erp_src]
        print('*' * 80)
        print('downloading:')
        print(erp_src)
        print('to', '%%s/%%s' %% (os.getcwd(), fname))
        print()
        p = Popen(cmd, stdout=PIPE)
        p.communicate()
    # now do the install
    if is_venv():
        # where is python
        cmd = ['/bin/bash', '-c', 'echo $(which python)']
        p = Popen(cmd, stdout=PIPE)
        python_cmd = p.communicate()[0].strip()
        # where is pip
        cmd = ['/bin/bash', '-c', 'echo $(which pip)']
        p = Popen(cmd, stdout=PIPE)
        pip_cmd = p.communicate()[0].strip()

        if not opts.noinstall:
            print ('about to install odoo')
            zip_archive = zipfile.ZipFile(fname)
            zipfile_name = zip_archive.infolist()[0].filename.split('/')[0]
            print ('unpacking %%s into folder odoo' %% zipfile_name)
            zip_archive.extractall()
            # do the actuall installing
            cmd = [pip_cmd, 'install', '-e', '.']
            # cd into odos directry, otherwise the path will be kept
            os.chdir(zipfile_name)
            print('installing odoo, this migth take some time')
            print(os.getcwd())
            p = Popen(cmd)
            p.communicate()
            os.chdir(adir)
            # make some links in bin
            os.chdir('bin')
        if not os.path.exists('odoo_bin'):
            cmd = ['/bin/bash', '-c', 'echo $(which odoo)']
            p = Popen(cmd, stdout=PIPE)
            odoo_cmd = p.communicate()[0].strip()
            if not odoo_cmd or not os.path.exists(odoo_cmd):
                # with odoo 9, "which odoo" does produce no result
                # so we search for python and fix the result
                odoo_cmd = '%%s/odoo.py' %% os.path.split(python_cmd)[0]
                if not os.path.exists(odoo_cmd):
                    print(bcolors.FAIL, '*' * 80)
                    print('did not find odo executable')
                    print(odoo_cmd)
                    return
            try:          
                os.symlink(odoo_cmd, 'odoo_bin')
            except: # FileExistsError exist only in python 3
                pass
            # create also erp_bin, so with time we will have
            # only erp and erp_bin
            try:          
                os.symlink(odoo_cmd, 'erp_bin')
            except: # FileExistsError exist only in python 3
                pass
        # the following two links are pure convinience, and because we allways had it ..
        if not os.path.exists('python'):
            os.symlink(python_cmd, 'python')
        if not os.path.exists('pip'):
            os.symlink(pip_cmd, 'pip')
    else:
        print()
        print('not running in a virtual env, not installing')

    os.chdir(adir)
    # if we sugsessfully installed odoo, we also install
    # the requirements of the actual site
    if python_cmd:
        print('installing extrarequirements for site', PROJECT_NAME)
        cmd = [pip_cmd, 'install', '-r', 'install/requirements.txt']
        p = Popen(cmd, stdout=PIPE)    
        p.communicate()

        #and finally we need to create a config file
        print('creating config file etc/odoo.cfg for site')
        make_base_config_file()
    if opts.demo_data:
        from create_db import main as create_db_main
        create_db_main(opts)

if __name__ == '__main__':
    usage = "build_odoo.py -h for help on usage"
    parser = OptionParser(usage=usage)
    # parser.add_option(
    #     "-i", "--ignores",
    #     action="store_true", dest="ignores", default=False,
    #     help = 'set svn:ignores'
    # )
    parser.add_option(
        "-d", "--demo_data",
        action="store_true", dest="demo_data", default=False,
        help='create a database with demo-data'
    )
    parser.add_option(
        "-f", "--force",
        action="store_true", dest="force", default=False,
        help='force to reload newest odoo'
    )
    parser.add_option(
        "-p", "--pwd",
        action="store", dest="password", default='admin',
        help = 'database password'
    )
    parser.add_option(
        "-n", "--noinstall",
        action="store_true", dest="noinstall", default=False,
        help='do not install erp, only create config'
    )

    (opts, args) = parser.parse_args()
    main(opts)  # opts.noinit, opts.initonly)
