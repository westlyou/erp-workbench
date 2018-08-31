#!/usr/bin/env python
import sys
import time
import os
import atexit
from signal import SIGTERM
import logging
from subprocess import PIPE, Popen, STDOUT
import getpass
import psutil
from dosetup_odoo import PROJECT_HOME, make_base_config_file, BASE_CFG_FILE

# PROJECT_NAME is the folder-name in which the project is created
PROJECT_NAME = os.path.split(os.path.dirname(os.path.abspath(PROJECT_HOME)))[-1]
# ACT_USER is logged in user
ACT_USER = getpass.getuser()
## NO_DB_CFG name of config to construct/use for no db
#NO_DB_CFG = etc/tmp_no_db.cfg

NEW_TAGS = {
    'db_name' : 'False',
    'dbfilter' : 'False',
    'without_demo' : 'False',
    'demo' : 'all',
}

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
# http://giridhar-mb.blogspot.com/2013/05/python-daemon-example-with-logging.html
class MyDaemon(object):
    """
        A generic daemon class.
        Usage: subclass the Daemon class and override the run() method
    """
    startmsg = "started with pid %%s"

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %%d (%%s)\n" %% (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir(".")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %%d (%%s)\n" %% (e.errno, e.strerror))
            sys.exit(1)

            # redirect standard file descriptors
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')

        pid = str(os.getpid())

        sys.stderr.write("\n%%s\n" %% self.startmsg %% pid)
        sys.stderr.flush()

        if self.pidfile:
            open(self.pidfile, 'w+').write("%%s\n" %% pid)

        atexit.register(self.delpid)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %%s already exist. Daemon already running?\n"
            sys.stderr.write(message %% self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %%s does not exist. Daemon not running?\n"
            sys.stderr.write(message %% self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    print()
                    str(err)
                    sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        time.sleep(5)
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """

class TaskDaemon(MyDaemon):
    odoo_process = None
    p_name = ''
    def __init__(self, pid_name, cmd_name):
        """run odoo or any erp in the backgroung
        
        Arguments:
            pid_name {string} -- name of the file where the pid is stored
            cmd_name {string} -- command to execute to run the erp
        """


        super(TaskDaemon, self).__init__(pid_name)
        self.cmd_name = cmd_name

    def run(self):
        running = False
        while not self.odoo_process or running:
            ''' this function below is called every 1 second '''
            try:
                p = run_odoo(cmd_name)
                process_id = p.pid
                # process_info = get_process_id(p_name)
                self.odoo_process = psutil.Process(process_id)
                if not self.odoo_process:
                    print(bcolors.FAIL, '\n------------------------------')
                    print('could not start', 'bin/%%s' %% self.cmd_name)
                    print(bcolors.ENDC)
                else:
                    running = True
            except Exception as ex:
                print("Error in doing run_odoo(): %%s" %% (ex))

            ''' sleep for 1 second before doing stuff again '''
            time.sleep(1)

    def stop(self):
        super(TaskDaemon, self).stop()
        if self.odoo_process:
            self.odoo_process.terminate()
            self.odoo_process.kill()


def run_odoo(cmd_name):
    #cmd_name = 'odoo_bin'
    site_name = PROJECT_NAME
    f_name = BASE_CFG_FILE
    p = Popen(
        [
            'nohup',
            'bin/python' ,
            'bin/%%s' %% cmd_name,
            '-c',
            BASE_CFG_FILE,
        ], stdout=PIPE, stderr=STDOUT)
    return p

def main():
    CMD_NAME = 'odoo_bin'
    PIDFILE = '/tmp/odoorunner_daemon.pid'
    # if a command file name was passed as second parameter
    if len(sys.argv) > 2:
        CMD_NAME = sys.argv[2]
    # if a pid file name was passed as third parameter
    if len(sys.argv) > 3:
        CMD_NAME = sys.argv[3]
    daemon = TaskDaemon(PIDFILE, CMD_NAME)
    daemon_name = "TaskDemon"

    #==============================================================
    if 'start' == sys.argv[1]:
        try:
            daemon.start()
        except Exception,ex:
            print "%%s start() error: %%s" %% (daemon_name,ex)
    #==============================================================
    elif 'stop' == sys.argv[1]:
        try:
            daemon.stop()
        except Exception,ex:
            print "%%s stop() error: %%s" %% (daemon_name,ex)
    #==============================================================
    elif 'restart' == sys.argv[1]:
        try:
            daemon.restart()
        except Exception,ex:
            print "%%s retart() error: %%s" %% (daemon_name,ex)
    #==============================================================
    else:
        print "Unknown command"
        sys.exit(2)
    #==============================================================
    sys.exit(0)
 
if __name__ == "__main__":
    main()
