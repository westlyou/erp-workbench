#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import print_function

import subprocess
import warnings
import sys
import os
#from __builtin__ import file
from pprint import pprint
from optparse import OptionParser
from dosetup_odoo import make_base_config_file, PROJECT_HOME
from collections import OrderedDict
import psycopg2
from odoorpc import ODOO
from subprocess import PIPE, Popen, STDOUT
import psutil
import time
import time
import atexit
from signal import SIGTERM
import logging
import getpass
import uuid

# ACT_USER is logged in user
ACT_USER = getpass.getuser()
PROJECT_NAME = os.path.split(PROJECT_HOME)[-1]

def check_and_kill(port):
    try:
        #errMsg = 'Enter integer value for port number'
        port = int(port)
        cmd = 'lsof -t -i:{0}'.format(port)
        pid = subprocess.check_output(cmd, shell=True)
        pid = int(pid)
    except ValueError:
        pid = None
        return
    except Exception as e:
        # print("No process running on port {0}".format(port))
        return
    processTypeCmd = 'ps -p {0} -o comm='.format(pid)
    processType = subprocess.check_output(processTypeCmd, shell=True).rstrip('\n')
    confirm = ''
    if processType:

        killcmd = 'kill -9 {0}'.format(pid) if pid else None
        isKilled = os.system('kill -9 {0}'.format(pid)) if pid else None
        if isKilled == 0:
            # print("Port {0} is free. Processs {1} killed successfully".format(port, pid))
            return
        else:
            print("Cannot free port {0}.Failed to kill process {1}, err code:{2}".format(port, pid, isKilled))
            sys.exit()

SQL = """SELECT pg_terminate_backend(pg_stat_activity.pid) 
  FROM pg_stat_activity 
  WHERE pg_stat_activity.datname = '%%s' 
    AND pid <> pg_backend_pid();"""
SQL2 = "DROP DATABASE %%s"

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

def get_process_id(name):
    """
    Return process ids found by (partial) name .

    """
    # child = subprocess.Popen(['pgrep', '-f', name], stdout=subprocess.PIPE, shell=False)
    # response = child.communicate()[0]
    # pids = [int(pid) for pid in response.split()]
    pids = [p.info['pid'] for p in psutil.process_iter(attrs=['pid', 'name']) if name in p.info['name']]
    result = []
    for pid in pids:
        result.append((pid, psutil.Process(pid).cmdline()))
    return result

def create_new_db(opts):
    # what python do we need to use
    # if we run our old configuration we get it from the project dir
    # if we are running under virtualenv, we have to use this one
    #p.communicate()
    # now wait for 10 secs to allow odoo to spinn up
    # now we can create a new database
    # for this we attach to odoo first
    temp_name = uuid.uuid4().hex 
    site_name = PROJECT_NAME
    p_name = 'erp_bin'
    start_cmd = [
        '%%s/bin/erp_runner.py' %% PROJECT_HOME,
        'start',
        p_name,
        temp_name
    ]
    stop_cmd = [
        '%%s/bin/erp_runner.py' %% PROJECT_HOME,
        'stop',
        p_name,
        temp_name
    ]

    p = Popen(start_cmd, stdout=PIPE, stderr=STDOUT)
    p.communicate()
    print(bcolors.OKBLUE, '\n------------------------------')
    print('started erp system in the background')
    print('now waiting for 5 secs to allow it to spin up')
    print(bcolors.ENDC)
    time.sleep(5)

    odoo = ODOO()
    try:
        odoo.login(PROJECT_NAME, 'admin', opts.password)
    except:
        pass
    if not odoo:
        print(bcolors.FAIL, '\n------------------------------')
        print('could not start odoo')
        print('please try again. If this does not help, look for a prosses using')
        print('ps aux | grep ', p_name)
        print('and kill it')
        print(bcolors.ENDC )
    old_timeout = odoo.config['timeout']
    odoo.config['timeout']=600
    print(bcolors.WARNING, '\n------------------------------')
    print('dropping db:', site_name)
    print(bcolors.ENDC )
    # drop the old db
    try:
        odoo.db.drop('admin', db=site_name) 
    except:
        pass
    print(bcolors.WARNING, '\n------------------------------')
    print('creating new db:', site_name)
    print(bcolors.ENDC )
    odoo.db.create('admin', db=site_name, demo=True, admin_password=opts.password)
    # now kill the process again
    print(bcolors.WARNING, '\n------------------------------')
    print('killing background odoo process again',)
    print(bcolors.ENDC )

    #process_info = get_process_id(p_name)
    p = Popen(stop_cmd, stdout=PIPE, stderr=STDOUT)
    p.communicate()
    print(bcolors.OKGREEN, '------------------------------')
    print('all done',)
    print(bcolors.ENDC )


def main(opts):
    check_and_kill('8069')
    conn_string = "dbname='%%s' user=%%s host='%%s' password='%%s'" %% ('postgres', ACT_USER, 'localhost', opts.password)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print(bcolors.WARNING, 'close connections', bcolors.ENDC)
    cursor.execute(SQL %% PROJECT_NAME)
    cursor.fetchall()
    conn.commit()
    conn.close()
    make_base_config_file()
    # now the database should be non existant or be free of connections
    create_new_db(opts)

    

if __name__ == '__main__':
    usage = bcolors.WARNING + """
    create_db creates a new database for site %%s
    - h for help on usage
    """ %% PROJECT_NAME 
    usage += bcolors.ENDC
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-p", "--pwd",
        action="store", dest="password", default='admin',
        help = 'database password'
    )
    
    parser.add_option(
        "-a", "--addon",
        action="store", dest="addon",
        help = 'addon to deal with'
        )
    (opts, args) = parser.parse_args()
    main(opts)  # opts.noinit, opts.initonly)
    
