#!%(python_path)s
# -*- encoding: utf-8 -*-
from __future__ import print_function 
import glob
import os
import sys
import subprocess
from subprocess import PIPE
from optparse import OptionParser
import shutil
import inspect

"""
this script sets up a new odoo project within the redcor project structure
it makes sure that all varaible-placeholder that are left from creating the structure and copying templtes
are replaced with the actual values.
Furthermore it creates login_info.cfg from login_info.cfg.in.
login_info.cfg is not overwritten automatically. Use --force to do so.
"""
SKIP_DIRS = [
    'anybox.recipe.openerp',
    'a.r.odoo',
    'bin',
    'bootstrap.py',
    'develop-eggs',
    'downloads',   
    'eggs',
    'etc',
    'parts',
    'python',
    'sql_dumps',
]

TAG = '%%s(PROJECT_NAME)%%s' %% ('$', '$') #make sure the tag definition does not replace it self
UTAG = '$(USERNAME)$'
#SKELETON_PATH = 'odoo/skeleton'
SKELETON_NAME = 'skeleton'
DEBUG = True

filename = inspect.getframeinfo(inspect.currentframe()).filename
# PROJECT_HOME is the folder in which the project is created
PROJECT_HOME  = os.path.split(os.path.dirname(os.path.abspath(filename)))[0]
# PROJECT_LIST_DIR the folder that houses all projects
PROJECT_LIST_DIR = os.path.split(os.path.split(PROJECT_HOME)[0])[0]

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


def replaceTags(dlist, projectname, replace_user):
    data = dlist[0]
    replaced = False
    if data.find(TAG) > -1:
        data = data.replace(TAG, projectname)
        replaced = True
    if data.find(UTAG) > -1:
        if not replace_user and (DEBUG):
            replace_user = projectname
        if replace_user:
            data = data.replace(UTAG, replace_user)
        replaced = True
    if replaced:
        dlist[0] = data
    return replaced

def doUpdate(root, name, PROJECT_NAME, force=False):
    fpath = os.path.join(root, name)
    for d in SKIP_DIRS:
        if fpath.find('/%%s/' %% d) > -1:
            return
    data = open(fpath, 'r').read()
    replace_user = ''
    try:
        replace_user = os.getlogin()
    except:
        import getpass
        replace_user = getpass.getuser()
    fpath_ori = ''
    if name == 'login_info.cfg.in':
        fpath_ori = fpath
        fpath = os.path.join(root, 'login_info.cfg')

    dlist = [data]
    if replaceTags(dlist, PROJECT_NAME, replace_user):
        # here we land, if a tag was to replace
        plist = [fpath_ori, fpath]
        if PROJECT_NAME == SKELETON_NAME:
            # do not overwrite 'login_info.cfg.in'
            plist = [fpath]
        for fp in plist:
            if fp:
                f = open(fp, 'w')
                f.write(dlist[0])
                f.close()
        print('File:', fpath, ' updated')
    elif fpath_ori:
        # here we land, if project was allredy constructed
        #just make sure that there is a 'login_info.cfg'
        if not os.path.exists(fpath) or force:
            shutil.copyfile(fpath_ori, fpath)
            print('File:', fpath_ori, ' copied to ', fpath)
        else:
            print('*' * 80)
            print('login_info.cfg not overwritten. Use --f --force to replace it ')
            print('*' * 80)

def  skip_root(root, home):
    # we want to check whether root is in SKIP_DIRS
    # but we must be carefull not to skipp all files when any of the names in SKIP_DIRS
    # are part of the path to the project
    if root.startswith(home):
        root = root[len(home):]
    parts = root.split(os.path.sep)
    for part in parts:
        if part in SKIP_DIRS:
            return True
    return False

def main(opts): #nosetup=False, onlysetup=False):
    nosetup = opts.noinit
    onlysetup = opts.initonly
    force = opts.force
    # replace all placeholder to the name of the actual directory
    print(PROJECT_HOME)
    PROJECT_NAME = os.path.split(PROJECT_HOME)[-1]
    if not onlysetup:
        for root, dirs, files in os.walk(PROJECT_HOME, topdown=False):
            for name in files:
                if skip_root(root, PROJECT_HOME):
                    continue
                fpath = os.path.join(root, name)
                if os.path.islink(fpath):
                    continue
                doUpdate(root, name, PROJECT_NAME, force)

    # create folder for odoo_addons
    try:
        os.mkdir('%%s_addons' %% PROJECT_NAME)
    except:
        pass # allready exists

    # create virtual env
    if nosetup:
        setupline = []
    else:
        setupline = ['virtualenv', '-p', %(python_ver)s, 'python']

    if onlysetup:
        cmd_lines = [['virtualenv', 'python'],['python/bin/python', 'bootstrap.py'],]
    else:
        cmd_lines = [
            # delete the local database(s)
            setupline,
            ['python/bin/pip', 'install', '-U', 'setuptools'],
            ['python/bin/pip', 'install', '-r', 'install/requirements.txt'],
            ['python/bin/pip', 'install', '-r', 'parts/odoo/requirements.txt'],
            ['python/bin/python', 'bootstrap.py'],
        ]

    for cmd_line in cmd_lines:
        if not cmd_line:
            continue
        print(' '.join(cmd_line))
        try:
            p = subprocess.Popen(cmd_line, stdout=PIPE)
            p.communicate()
            #os.system(' '.join(cmd_line))
        except Exception as e:
            print(bcolors.FAIL, '-' * 80)
            print(str(e))
            print(bcolors.ENDC, '-' * 80)
    # now set the path in the odoorunner
    data = open('%%s/bin/odoorunner.py' %% PROJECT_HOME).read()
    data = data.replace('#--!/usr/bin/python--', '#!%%s/bin/python' %% PROJECT_HOME)
    f = open('%%s/bin/odoorunner.py'  %% PROJECT_HOME, 'w')
    f.write(data)
    f.close()
    # allways set svn:ignores
#    handle_svn_ignores()

if __name__ == '__main__':
    usage = "dosetup.py -h for help on usage"
    parser = OptionParser(usage=usage)
    # parser.add_option(
    #     "-i", "--ignores",
    #     action="store_true", dest="ignores", default=False,
    #     help = 'set svn:ignores'
    # )
    parser.add_option(
        "-f", "--force",
        action="store_true", dest="force", default=False,
        help = 'overwrite existing login_info.cfg'
    )
    parser.add_option(
        "-n", "--noinit",
        action="store_true", dest="noinit", default=True,
        help = 'do not initialize virtual env'
    )
    parser.add_option(
        "-N", "--initonly",
        action="store_true", dest="initonly", default=False,
        help = 'do only initialize virtual env'
    )


    (opts, args) = parser.parse_args()
    main(opts) #opts.noinit, opts.initonly)
