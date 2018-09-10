#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import logging
from optparse import OptionParser
import subprocess
from subprocess import PIPE
from config import FOLDERNAMES, BASE_INFO, BASE_PATH, SITES_HOME
from scripts.utilities import get_process_id
import psutil
import time

# fix ca zeile 600 wenn localdata geladen wird, suchen mit PROCESS_NAMES
# dann ev mit pip merken, und pid stoppen
"""
robert@mozart:~/projects/redproducts/redproducts$ psql -U robert -d postgres
psql (9.4.4)
Type "help" for help.

postgres=# drop database redproducts;
DROP DATABASE
postgres=# create database redproducts;
CREATE DATABASE
"""
PROCESS_NAMES_DIC = {'odoo': 'odoo_bin',
                     'flectra': 'flectra_bin', 'start_openerp': ''}
PROCESS_NAMES = list(PROCESS_NAMES_DIC.keys())
#sys.path.insert(0, SITES_HOME)
from scripts.utilities import get_remote_server_info, bcolors, SITES

# to find executable python


def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))


def hunt_python(program):
    # try if the ogram is an executable
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    # bad luck, maybe we are virtual?
    # if we are in a virtual env
    # we run a shell scrip executing "which"
    if is_venv():
        cmd = ['/bin/bash', '-c', 'echo $(which python)']
        p = subprocess.Popen(cmd, stdout=PIPE)
        return p.communicate()[0].strip()

    return None

# to avoid waiting for an EOF on a pipe ...


def getlines(fd):
    line = bytearray()
    c = None
    while True:
        c = fd.read(1)
        if c is None:
            return
        line += c
        if c == '\n':
            yield str(line)
            del line[:]


def which(file):
    """
    """
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path, file)):
            return os.path.join(path, file)

    return None

# #1676  rsync -z --delete -av root@144.76.184.20:/opt/odoo/.local/share/Odoo/filestore/redproducts/ /home/robert/projects/redproducts/redproducts/parts/filestore/redproducts/
#     "breitschtraeff" : {
#         'servename' : '144.76.184.20',
#         'remote_data_path' : '/root/erp_workbench',
#         'remote_user' : 'root'
#     },


class DBUpdater(object):
    """
    class to do update the loacal database
    """
    dpath = ''

    # ------------------------------------
    # get_instance_list
    # checks all subdirectories whether
    # they provide an etc/open_erp.conf
    # if yes, it is considered to be an
    # openerp site
    # a dict of {'sitename' : dbname, ..}
    #   is returned
    # ------------------------------------
    # def get_instance_list(self):
    # """
    # checks all subdirectories whether
    # they provide an etc/open_erp.conf
    # if yes, it is considered to be an
    # openerp site
    # a dict of {'sitename' : dbname, ..}
    # is returned
    # """
    #opts = self.opts
    #home = self.BASE_INFO['erp_server_data_path']
    #dirs = [d for d in os.listdir(home) if os.path.isdir('%s/%s' % (home, d))]
    #result = {}
    # for d in dirs:
    #p = '%s/%s/etc/openerp-server.conf' % (home, d)
    # if os.path.exists(p):
    #db = self.get_value_from_config(p, 'db_name')
    #result[d] = db
    # if opts.verbose:
    #print d, 'db:', get_value_from_config(p, 'db_name')
    # return result

    def dump_instance(self):
        # -dump -ip  10.42.0.140 redo2oo -v
        opts = self.opts
        dbname = self.site_name
        dpath = ''
        dpath = '%s/%s/dump' % (BASE_INFO['erp_server_data_path'], dbname)
        print(bcolors.WARNING)
        print('*' * 80)
        # step one, create local dump
        if os.path.exists(dpath):
            odoo = self.get_odoo(verbose=True)
            import odoorpc
            try:
                runnig_db = odoo.env.db
            except (odoorpc.error.InternalError, AttributeError):
                runnig_db = 'unknown'
            if odoo and  runnig_db == dbname:

                #["PGPASSWORD=%s " % POSTGRES_PASSWORD, "/usr/bin/pg_dump", "-h", POSTGRES_HOST, "-U", POSTGRES_USER, '-Fc', dbname, "> %s/%s.dmp" % (dpath, dbname)]
                cmdline = "PGPASSWORD=%s /usr/bin/pg_dump -h %s -U %s -Fc %s > %s/%s.dmp" % \
                    (self.db_password, self.db_host,
                     self.db_user, dbname, dpath, dbname)

                print(cmdline)
                #print cmds
                p = subprocess.Popen(
                    cmdline, stdout=subprocess.PIPE, shell=True)
                p.communicate()
                print('dumped:', dpath)
            elif odoo:
                if not opts.force:
                    print((bcolors.FAIL))
                    print(('*' * 80))
                    print(('site %s is running, not %s, I can not determin what to so. leaving!' % (runnig_db, dbname)))
                    if opts.new_target_site:
                        print(('stop the the running odoo or use the option -F (force) if you just want to copy %s to %s' % 
                              (dbname, opts.new_target_site)))
                    print((bcolors.ENDC))
                    sys.exit()
                print('odoo is not running, so NO! dump was created')                
            else:
                print('odoo is not running, so NO! dump was created')
        else:
            print('not existing:', dpath)
            print(bcolors.ENDC)
            sys.exit()
        # if we want to copy the dumped stuff to a remote site
        # do it now
        if opts.use_ip_target:
            # we want to move the data to some remote server
            # so we have to look up what path we need remotely
            # this probably only works if we have root permission on the target
            target_site_name = dbname
            if opts.new_target_site:
                # is this a valid site?
                if not opts.new_target_site in list(self.sites.keys()):
                    print('not a valid site:', opts.new_target_site)
                    print(bcolors.ENDC)
                    sys.exit()
                target_site_name = opts.new_target_site
            server_dic = get_remote_server_info(opts)
            remote_data_path = server_dic['remote_data_path']
            remote_user = server_dic['remote_user']
            # we have to copy the local filestore to the remote filestore
            lfst_path = '%s/%s/filestore/%s' % (
                BASE_INFO['erp_server_data_path'], dbname, dbname)
            rfst_path = '%s/%s/filestore/%s' % (
                remote_data_path, target_site_name, target_site_name)
            ipt = opts.use_ip_target
            if ipt in ['localhost', '127.0.0.1']:
                rfst_path = '%s/%s/filestore/%s' % (
                    BASE_INFO['erp_server_data_path'], target_site_name, target_site_name)
                dpath = '%s/%s/dump' % (
                    BASE_INFO['erp_server_data_path'], dbname)
                target = '%s/%s/dump' % (
                    BASE_INFO['erp_server_data_path'], target_site_name)
                print('*' * 80)
                print('will copy the site data to %s' % rfst_path)
                cmdline = 'rsync -av %s/ %s/ --delete' % (lfst_path, rfst_path)
                p = subprocess.Popen(
                    cmdline, stdout=subprocess.PIPE, shell=True)
                print(cmdline)
                if opts.verbose:
                    print(p.communicate())
                else:
                    p.communicate()
                # now copy dumped db
                local_dump = '%s/%s.dmp' % (dpath, dbname)
                remote_dump = '%s/%s/dump/%s.dmp' % (
                    BASE_INFO['erp_server_data_path'], target_site_name, target_site_name)
                cmdline = 'rsync -av %s %s' % (local_dump, remote_dump)
                p = subprocess.Popen(
                    cmdline, stdout=subprocess.PIPE, shell=True)
                print(cmdline)
                if opts.verbose:
                    print(p.communicate())
                else:
                    p.communicate()
            else:
                print('*' * 80)
                print('will copy the site data to %s@%s:/%s' % (
                    remote_user, opts.use_ip_target, rfst_path))
                cmdline = 'rsync -av %s/ %s@%s:%s/ --delete' % (
                    lfst_path, remote_user, opts.use_ip_target, rfst_path)
                p = subprocess.Popen(
                    cmdline, stdout=subprocess.PIPE, shell=True)
                print(cmdline)
                if opts.verbose:
                    print(p.communicate())
                else:
                    p.communicate()
                # now copy dumped db
                local_dump = '%s/%s.dmp' % (dpath, dbname)
                remote_dump = '%s/%s/dump/%s.dmp' % (
                    remote_data_path, target_site_name, target_site_name)
                cmdline = 'rsync -av %s %s@%s:%s' % (
                    local_dump, remote_user, opts.use_ip_target, remote_dump)
                p = subprocess.Popen(
                    cmdline, stdout=subprocess.PIPE, shell=True)
                print(cmdline)
                if opts.verbose:
                    print(p.communicate())
                else:
                    p.communicate()

        print(bcolors.ENDC)

    def close_db_connections_and_delete_db(self, site_name):
        """
        Force close of all connection to db and delete it
        :site_name  : site name for which we will delete the db
        """
        from config import ACT_USER
        import psycopg2

        SQL = """SELECT pg_terminate_backend(pg_stat_activity.pid) \
          FROM pg_stat_activity \
          WHERE pg_stat_activity.datname = '%s' \
            AND pid <> pg_backend_pid();"""
        SQL2 = "DROP DATABASE %s"
        dbpw = 'admin'

        conn_string = "dbname='%s' user=%s host='%s' password='%s'" % (
            'postgres', ACT_USER, 'localhost', dbpw)
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        print('close connections')
        cursor.execute(SQL % site_name)
        cursor.fetchall()
        conn.commit()
        conn.close()
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        conn.autocommit = True
        print('drop db %s' % site_name)
        try:
            cursor.execute(SQL2 % site_name)
        except psycopg2.ProgrammingError as e:
            pass
        except Exception as e:
            print(str(e))
        conn.commit()
        conn.close()

    def _doUpdate(self, db_update=True, norefresh=None, site_name='', verbose='', extra_data={}):
        """
        """
        opts  = self.opts
        try:
            # we want to make sure the local directories exist
            self.create_folders(site_name, quiet=True)
        except AttributeError:
            pass
        if 'remote_user' in extra_data:
            remote_user = extra_data['remote_user']
        else:
            remote_user = self.remote_user
        #remote_data_path = self.remote_data_path
        if 'remote_url' in extra_data:  # self.opts.use_ip:
            remote_url = extra_data['remote_url']
        else:
            remote_url = self.remote_url
        # remote_data_path = self.remote_data_path # server_info['remote_data_path']
        if 'remote_data_path' in extra_data:
            remote_data_path = extra_data['remote_data_path']
        else:
            remote_data_path = self.remote_data_path
        #
        if 'remote_pw' in extra_data:
            remote_pw = extra_data['remote_pw']
        else:
            remote_pw = self.db_password

        # make sure we are in odo_instances so we find the scripts
        actual_pwd = os.getcwd()
        os.chdir(self.sites_home)

        # self.remote_user #server_info.get('user', 'remote_user') # da is ein wischi waschi ..
        user = remote_user
        pw = remote_pw  # self.db_password
        # check if we have to copy things to a new target
        use_site_name = site_name
        if opts.new_target_site:
            use_site_name =  opts.new_target_site
        dpath = '%s/%s/dump/%s.dmp' % (self.data_path, use_site_name, use_site_name)
        if not norefresh:
            # ---------------------------
            # updatedb.sh
            # ---------------------------
            """
            #!/bin/sh
            # updatedb.sh executes the script dodump.sh on a remote server
            # dodump.sh creates a temporary docker container that dumps a servers database
            # into this servers data folder within erp_workbench
            # parameters:
            # $1 : site name
            # $2 : server url
            # $3 : remote_data_path like /root/erp_workbench
            # $4 : login name on remote server
            # $5 : local path to odo server data
            # $6 : local path to odo_instances
            # $7 : vebose flag
            c1="ssh $4@$2 'bash -s' < $6/scripts/dodump.sh $1 $3 $7"
            echo "-1-" $c1
            $c1
            c2="rsync -avzC --delete $4@$2:$3/$1/filestore/ $5/$1/filestore/"
            echo "-2-" $c2
            $c2
            c3="rsync -avzC --delete $4@$2:$3/$1/dump/ $5/$1/dump/"
            echo "-3-" $c3
            $c3
            """
            # ---------------------------
            # dodump.sh
            # ---------------------------
            """
            #!/bin/sh
            # dodump.sh dumps a site's database into its folder
            # the folder is /root/erp_workbench/$1/dump where $1 represents the site's name
            # dodump creates a temporary docker container that dumps a servers database
            # it is called by updatedb.sh and executed on the remote computer
            # $1 : name of the server                     updatedb.$1
            # $2 : path to the location of odo_instances  updatedb.$3
            #      on the remote server
            # $3 : verbose flag                           updatedb.$7
            echo '----------- running dodump ----------------'
            FILE=$2/dumper/rundumper.py
            echo "FILE:$FILE"
            echo $HOSTNAME
            if [ -f "$FILE" ]
             then {
                echo 'calling python' $FILE $1 $3
                python $FILE $1 -d $3
            }
            else {
                echo 'kein rundumper'
                sudo docker run -v $2:/mnt/sites  --rm=true --link db:db  dbdumper -d $1
            }
            fi
            """
            os.system('%s/scripts/updatedb.sh %s %s %s %s %s %s %s' % (
                self.default_values['sites_home'],  # no param
                site_name,                         # param 1
                remote_url,                        # param 2
                remote_data_path,                   # param 3
                remote_user,                       # param 4
                self.erp_server_data_path,        # param 5
                self.sites_home,                   # param 6
                verbose,                           # param 7
            ))
            # if remote user is not root we first have to copy things where we can access it
            if remote_user != 'root':
                """
                dodump_remote.sh is run on the reote server, and copies everything to a place,
                where it can be accessed by user that is logged in to the remote server.
                Assuming that the remote server is:
                    82.220.39.73
                Assuming that the remote data is at:
                    /root/erp_workbench
                the local user loggs in to the remote server as:
                    odooprojects
                the remote user has its odoo data in:
                    /home/odooprojects/erp_workbench
                the server name for which we want to copy the data is:
                    afbstest
                then on the REMOTE server we have to execute the following commands:
                    rsync -av /root/erp_workbench/afbstest/filestore/ /home/odooprojects/erp_workbench/afbstest/filestore/
                    rsync -av /root/erp_workbench/afbstest/dump/ /home/odooprojects/erp_workbench/afbstest/dump/
                    chmod a+rw /home/odooprojects/erp_workbench/afbstest/* -R
                the above commands will be executed on the REMOTE machine by calling:
                    #sudo $5/scripts/site_syncer.py $1 $2 $3 $4 $5
                    sudo /root/odoo_sites/scripts/site_syncer.py afbstest 82.220.39.73 /home/odoprojects/erp_workbench odoprojects /root/odoo_sites

                #!/bin/sh
                # dodump_remote.sh rsyncs a remote site in /root/odoo_sites/SITENAME
                # to /home/someuser/odoo_sites/SITENAME, so we can rsync it from there
                # the folder is /root/erp_workbench/$1/dump where $1 represents the site's name
                # parameters:
                # $1 : site name
                # $2 : server url
                # $3 : remote_data_path to the server data like /root/odoo_server_data
                # $4 : login name on remote server
                # $5 : path to roots instance home on the remote server (/root/erp_workbench)
                echo sudo $5/scripts/site_syncer.py $1 $2 $3 $4 $5
                sudo $5/scripts/site_syncer.py $1 $2 $3 $4 $5
                """
                # this calls the remote site_syncer.py script
                # it copies needed files to the users home and changes ownership
                remote_user_data_path = remote_data_path  # self.remote_user_data_path
                os.system('%s/scripts/updatedb_remote.sh %s %s %s %s %s' % (
                    self.default_values['sites_home'],
                    site_name,
                    remote_url,
                    remote_user_data_path,
                    remote_user,
                    self.remote_sites_home))  # where scripts/site_syncer.py is to be found
            # -----------------------------------------------
            # rsync the remote files to the local directories
            # -----------------------------------------------
            """
            #!/bin/sh
            # updatedb.sh executes the script dodump on a remote server
            # dodump creates a temporary docker container that dumps a servers database
            # into this servers data folder within erp_workbench
            # parameters:
            # $1 : site name
            # $2 : server url
            # $3 : remote_data_path like /root/erp_workbench
            # $4 : login name on remote server
            # $5 : erp_server_data_path
            # $6 : target site name
            echo ssh $4@$2 'bash -s' < scripts/dodump.sh $1
            ssh $4@$2 'bash -s' < scripts/dodump.sh $1
            echo rsync -avzC --delete $4@$2:/$3/$1/filestore/$1 $5/$6/filestore/$6
            rsync -avzC --delete $4@$2:/$3/$1/filestore/$1 $5/$6/filestore/$6
            echo rsync -avzC --delete $4@$2:/$3/$1/dump/$1.dmp $5/$6/dump/$6.dmp
            rsync -avzC --delete $4@$2:/$3/$1/dump/$1.dmp $5/$6/dump/$6.dmp
            
            """
            if remote_user != 'root':
                remote_user_data_path = remote_data_path
                #remote_data_path = self.remote_user_data_path
            os.system('%s/scripts/rsync_remote_local.sh %s %s %s %s %s %s' % (
                self.default_values['sites_home'],
                site_name,
                remote_url,
                remote_data_path,
                remote_user,
                BASE_INFO['erp_server_data_path'],
                use_site_name,
            ))
            if not os.path.exists(dpath):
                print('-------------------------------------------------------')
                print('%s not found' % dpath)
                print('-------------------------------------------------------')
                return
            try:
                if self.opts.backup:
                    # no need to update database
                    return
            except AttributeError:
                pass
        if db_update:
            # make sure the needed directories exist
            fp = '%s/%s/filestore' % (self.data_path, use_site_name)
            if not os.path.exists(fp) and os.path.isdir(fp):
                print(bcolors.FAIL + '%s is not yet created, can not be updated' % use_site_name + bcolors.ENDC)
                return
            pw = self.login_info['db_password']
            user = self.login_info['db_user']
            shell = False
            # mac needs absolute path to psql
            where = os.path.split(which('psql'))[0]
            wd = which('docker')
            dumper_image_name = BASE_INFO.get('docker_dumper_image')
            if wd:
                whered = os.path.split(wd)[0]
            else:
                whered = ''
            if whered:
                cmd_lines_docker = [
                    ['%s/docker run -v %s:/mnt/sites  -v %s/dumper/:/mnt/sites/dumper --rm=true --link db:db  -it %s -r %s' %
                     (whered, BASE_INFO['erp_server_data_path'], BASE_PATH, dumper_image_name, use_site_name)]
                ]
            else:
                cmd_lines_docker = [
                    ['docker run -v %s:/mnt/sites  -v %s/dumper/:/mnt/sites/dumper --rm=true --link db:db  -it %s -r %s' %
                     (BASE_INFO['erp_server_data_path'], BASE_PATH, dumper_image_name, use_site_name)]
                ]
            # if we know admins password, we set it
            # for non docker pw is usualy admin, so we do not use it
            #adminpw = self.sites[self.site_name].get('odoo_admin_pw')
            # if adminpw:
                #cmd_lines_docker += [['%s/psql' % where, '-U', user, '-d', site_name,  '-c', "update res_users set password='%s' where login='admin';" % adminpw]]
            cmd_lines_no_docker = [
                # delete the local database(s)
                ['%s/psql' % where, '-U', user, '-d', 'postgres',
                    '-c', "drop database IF EXISTS %s;" % use_site_name],
                # create database again
                ['%s/psql' % where, '-U', user, '-d', 'postgres',
                    '-c', "create database %s;" % use_site_name],
                # do the actual reading of the database
                # the database will have thae same name as on the remote server
                ['%s/pg_restore' % where, '-O', '-U',
                    user, '-d', use_site_name, dpath],
                # set standard password
                ['%s/psql' % where, '-U', user, '-d', use_site_name,  '-c',
                    "update res_users set password='admin' where login='admin';"],
            ]
            cmd_lines = [
                {'cmd_line': ['chmod', 'a+rw', '%s/%s/filestore' % (
                    BASE_INFO['erp_server_data_path'], use_site_name)], 'is_builtin': True},
                {'cmd_line': ['chmod', 'a+rw', '%s/%s/filestore/' % (
                    BASE_INFO['erp_server_data_path'], use_site_name), '-R'], 'is_builtin': True},
                {'cmd_line': ['chmod',  'a+rw', '%s/%s/log' % (
                    BASE_INFO['erp_server_data_path'], use_site_name)], 'is_builtin': True},
            ]

            if self.opts.dataupdate_docker or self.opts.transferdocker:
                cmd_lines = cmd_lines_docker + cmd_lines
                shell = True
            else:
                cmd_lines = cmd_lines_no_docker + cmd_lines
            self.run_commands(cmd_lines, shell=shell, user=user, pw=pw)
            # go back where we have been
            os.chdir(actual_pwd)

    def create_db_demo(self):
        os.chdir(self.default_values['inner'])
        # create a new config file with nothing changed but db stuff
        found = False
        for f_name in ['openerp.cfg', 'odoo.cfg', 'flectra.cfg', 'odoo.conf']:
            if os.path.isfile('etc/%s' % f_name):
                found = True
                break
        if not found:
            print('no config file found')
            return
        d = open('etc/%s' % f_name).read()
        # just add new values for the db stuff
        # this will be the ued ones
        d += '\ndb_name = False'
        d += '\ndbfilter = False'
        d = open('etc/no_db_%s' % f_name, 'w').write(d)
        # what process should we start
        found = False
        for p_name in ['start_openerp', 'start_odoo', 'start_flectra', 'odoo']:
            if os.path.isfile('bin/%s' % p_name):
                found = True
                break
        if not found:
            print('no executable script found')
            return
        process_info = get_process_id(p_name, self.default_values['inner'])
        if process_info:
            p = psutil.Process(process_info[0][0])
            p.terminate()
            # now we change restart without a database
        # what python do we need to use
        # if we run our old configuration we get it from the project dir
        # if we are running under virtualenv, we have to use this one
        p = subprocess.Popen(
            [
                hunt_python('%s/bin/python' % self.default_values['inner']),
                'bin/%s' % p_name,
                '-c',
                '%s/etc/no_db_%s' % (self.default_values['inner'], f_name)
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # no wait for 10 secs to allow odoo to spinn up
        process_info = get_process_id(p_name, self.default_values['inner'])
        if not process_info:
            print(bcolors.FAIL, '\n------------------------------')
            print('could not start', 'bin/%s' % p_name)
            print(bcolors.ENDC)
        # wait for 5 secs to allow odoo to spin up
        print(bcolors.OKBLUE, '\n------------------------------')
        print('started odoo in the background')
        print('now waiting for 5 secs to allow odoo to spin up')
        print(bcolors.ENDC)
        time.sleep(5)
        # now we can create a new database
        # for this we attach to odoo first
        try:
            odoo = self.get_odoo(no_db=True)
        except:
            pass
        if not odoo:
            print(bcolors.FAIL, '\n------------------------------')
            print('could not start odoo')
            print('please try again. If this does not help, look for a prosses using')
            print('ps aux | grep ', p_name)
            print('and kill it')
            print(bcolors.ENDC)
        old_timeout = odoo.config['timeout']
        odoo.config['timeout'] = 600
        print(bcolors.WARNING, '\n------------------------------')
        print('dropping db:', self.site_name)
        print(bcolors.ENDC)
        # drop the old db
        try:
            odoo.db.drop('admin', db=self.site_name)
        except:
            pass
        print(bcolors.WARNING, '\n------------------------------')
        print('creating new db:', self.site_name)
        print(bcolors.ENDC)
        odoo.db.create('admin', db=self.site_name,
                       demo=True, admin_password='admin')
        # now kill the process again
        print(bcolors.WARNING, '\n------------------------------')
        print('killing the procces', end=' ')
        print(bcolors.ENDC)

        process_info = get_process_id(p_name, self.default_values['inner'])
        if process_info and process_info[0]:
            psutil.Process(process_info[0][0]).terminate()
        print(bcolors.OKGREEN, '------------------------------')
        print('all done', end=' ')
        print(bcolors.ENDC)

    def doUpdate(self, db_update=True, norefresh=None, names=[], is_local=False, set_local=True):
        """
        """
        opts = self.opts
        if not names:
            names = self.site_names
        if norefresh is None:
            norefresh = opts.norefresh
        if len(names) > 1:
            # if len name > 1 we are a restoring ...
            # would this work at all?
            set_local = False
        for site_name in names:
            # we have to get info about the remote server indirectly
            # as it could be overridden by overrideremote
            server_dic = get_remote_server_info(opts)
            # do we need to close all connections first?
            if opts.dataupdate_close_connections:
                if opts.new_target_site:
                    use_site_name =  opts.new_target_site
                self.close_db_connections_and_delete_db(use_site_name)

            # determine what erp command to execute
            for process_name in PROCESS_NAMES:
                process_info = get_process_id(
                    process_name, self.default_values['inner'])
                if process_info:
                    break
            if set_local:
                # kill the process
                if not process_info:
                    print('odoo/flectra not running')
                else:
                    if not norefresh:
                        p = psutil.Process(process_info[0][0])
                        if p.is_running():
                            p.terminate()
            self._doUpdate(db_update, norefresh, site_name,
                           opts.verbose and ' -v' or '', extra_data=server_dic)
            if set_local:
                # restart process
                os.chdir(self.default_values['inner'])
                prossess_pid = None
                for process_name in PROCESS_NAMES:
                    run_cmd = 'bin/%s' % process_name
                    if os.path.exists(run_cmd):
                        break
                try:
                    if not opts.noupdatedb: #norefresh:
                        if process_info:
                            p = subprocess.Popen(
                                process_info[0][1], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        else:
                            if process_name != 'start_openerp':
                                p = subprocess.Popen(
                                    [run_cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            else:
                                # good old start_openerp
                                p = subprocess.Popen(
                                    ['%s/bin/python' % self.default_values['inner'], run_cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        lcounter = 0
                        for line in getlines(p.stdout):
                            lcounter +=1
                            if lcounter > 100:
                                break
                            if "running on" in line:
                                print(bcolors.OKGREEN)
                                print("STARTUP OK")
                                print(bcolors.ENDC)
                                break
                            else:
                                print(line)
                                if 'Address already in use' in line:
                                    p=subprocess.Popen(['lsof', '-i', ':8069'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
                                    result = p.communicate()
                                    print(result)
                                break
                        prossess_pid = p.pid
                except:
                    print('could not chdir to:%s' % self.default_values['inner'])
                    pass
                if not opts.noupdatedb:
                    try:
                        # make sure we do not start sending out emails and such
                        self.set_local_data()
                    except:
                        # we probably could not log in
                        pass
                    if prossess_pid:
                        p = psutil.Process(prossess_pid,)
                        print('about to terminate %s' % p.cmdline()[-1])
                        if p.is_running():
                            p.terminate()
                            p.kill()
                    # just to be sure ..
                    process_info = get_process_id(
                        PROCESS_NAMES_DIC[process_name], self.default_values['inner'])
                    if process_info:
                        p = psutil.Process(process_info[0][0])
                        print('about to terminate %s' % ','.join(p.cmdline()[-1]))
                        if p.is_running():
                            try:
                                p.terminate()
                            except:
                                print('failed to terminate: %' % ','.join(
                                    p.cmdline()[-1]))

    def doTransfer(self):
        """
        transfer data from on docker acount to an other
        the following steps have to be executed
        - dump the source
        - copy the source to the target. changing the folder in target
        - stoping the target container
        - restoring the source dump into target
        - restarting target container

        the transfer always is done on localhost
        but this will change
        """
        opts = self.opts
        for site_name in self.site_names:
            slave_db_data = SITES[site_name]
            # we have to get info about the remote server indirectly
            # as it could be overridden by overrideremote
            server_dic = get_remote_server_info(opts)
            if not server_dic:
                return
            if not site_name in self.get_instance_list():
                print('*' * 80)
                print('site %s does not exist or is not initialized' % site_name)
                print('run bin/c.sh -D %s' % site_name)
                if len(self.site_names) > 1:
                    continue
                return
            remote_url = server_dic.get('remote_url')
            remote_user = server_dic.get('remote_user')
            remote_data_path = server_dic.get('remote_data_path')
            dpath = '%s/%s/dump/%s.dmp' % (
                BASE_INFO['erp_server_data_path'], site_name, site_name)

            # get info about main site
            if opts.transferdocker:
                docker_info = slave_db_data.get('docker')
                if not docker_info or not docker_info.get('container_name'):
                    print('*' * 80)
                    print('no docker info found for %s, or container_name not set' % site_name)
                    if len(self.site_names) > 1:
                        continue
                    return
            slave_info = slave_db_data.get('slave_info')
            if not slave_info:
                print('*' * 80)
                print('no slave info found for %s' % site_name)
                if len(self.site_names) > 1:
                    continue
                return
            master_name = slave_info.get('master_site')
            if not master_name in self.get_instance_list():
                print('*' * 80)
                print('master_site %s does not exist or is not initialized' % master_name)
                print('run bin/c.sh -D %s' % master_name)
                if len(self.site_names) > 1:
                    continue
                return
            if not master_name:
                print('*' * 80)
                print('master_site not provided for %s' % site_name)
                if len(self.site_names) > 1:
                    continue
                return
            master_db_data = SITES[master_name]
            master_server_dic = get_remote_server_info(opts, master_name)
            master_remote_url = 'localhost'  # server_dic.get('remote_url')
            master_remote_user = server_dic.get('remote_user')
            master_remote_data_path = server_dic.get('remote_data_path')
            # update local master file, but not local database
            self.doUpdate(db_update=False, names=[master_name])
            # rsync -avzC --delete /home/robert/erp_workbench/afbs/filestore/afbs/ /home/robert/erp_workbench/afbstest/filestore/afbstest/
            ddiC = {
                'base_path': self.default_values['sites_home'],
                'master_name': master_name,
                'master_db_name': master_db_data['db_name'],
                'slave_name': site_name,
                'slave_db_name': slave_db_data['db_name']
            }
            # make sure directory for the rsync target exist
            rsync_target = '%(base_path)s/%(slave_name)s/filestore/%(slave_name)s/' % ddiC
            if not os.path.exists(rsync_target):
                os.makedirs(rsync_target)
            cmd_lines = [
                'rsync -avzC --delete %(base_path)s/%(master_name)s/dump/%(master_name)s.dmp  %(base_path)s/%(slave_name)s/dump/%(slave_name)s.dmp' % ddiC,
                'rsync -avzC --delete %(base_path)s/%(master_name)s/filestore/%(master_db_name)s/  %(base_path)s/%(slave_name)s/filestore/%(slave_db_name)s/' % ddiC,
            ]
            # now we have to decide whether docker needs to be used
            if opts.transferdocker:
                # stop local docker
                stopdocker = 'docker stop %s' % docker_info.get(
                    'container_name')
                cmd_lines += [stopdocker]
            # execute transfer
            # user and pw needs to be defined ??
            self.run_commands(cmd_lines, user, pw)
            # update database
            self.doUpdate(names=[site_name], norefresh=True)
            if opts.transferdocker:
                # restart local docker
                startdocker = 'docker restart %s' % docker_info.get(
                    'container_name')
                cmd_lines += [startdocker]
                self.run_commands(cmd_lines, user, pw)
