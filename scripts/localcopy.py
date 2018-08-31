#!bin/python
# -*- encoding: utf-8 -*-
import os
#from optparse import OptionParser
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

try:
    from ruamel.std.argparse import ArgumentParser, set_default_subparser
    import argparse
except ImportError:
    print '*' * 80
    print bcolors.WARNING +bcolors.FAIL + 'please run bin/pip install -r install/requirements.txt' + bcolors.ENDC
    print 'not all libraries are installed'
    print '*' * 80
    sys.exit()

#from argparse import ArgumentParser #, _SubParsersAction
import subprocess
from subprocess import PIPE

usage = """
localcopy copies all serverdata from source to target.
This includes:
- the server dump
- the filestore

After having performded the copy , the target sql-server %sMUST!%s be restored
from the sql dump. This operation is %sNOT%s performed by localcopy.
To perform the restore:
- run: bin/c docker -dud -N target (if site runs in a docker container)
- run: bin/c -u -N target (if site runs without docker)
""" % (bcolors.FAIL, bcolors.ENDC, bcolors.FAIL, bcolors.ENDC)

final_message = """
Now the target sql-server %sMUST!%s be restored
To perform the restore:
- run: bin/c docker -dud -N %%s (if site runs in a docker container)
- run: bin/c -u -N -v %%s (if site runs without docker)
""" % (bcolors.FAIL, bcolors.ENDC)

main_message = """
-----------------------------------------------------------------
%sBe carefull !! %s
Only data %sactually existing%s on the filesystem is copied.
To refresh the data do a bin/c -u -nupdb -v %%s
on your %slocal%s machine to force a fresh server dump
-----------------------------------------------------------------
""" % (bcolors.FAIL, bcolors.ENDC, bcolors.FAIL, bcolors.ENDC, bcolors.WARNING, bcolors.ENDC)

def main():
    parser = ArgumentParser(usage = usage)
    parser.add_argument(
        "-v", "--verbose",
        action="store_true", dest="verbose", default=True,
        help="be verbose, default True")
    parser.add_argument(
        "-r", "--remote-host",
        action="store", dest="remote_host",
        help="remote host")
    parser.add_argument(
        "-ru", "--remote-user",
        action="store", dest="remote_user", default='root',
        help="user on remote host. Default root")
    args, unknownargs = parser.parse_known_args()
    print main_message %  ((unknownargs and unknownargs[0]) or 'SOURCE')
    if len(unknownargs) != 2:
        print bcolors.WARNING + 'need exactly two arguments: soucedirectory, targetdirectory' + bcolors.ENDC
        return
    source, target = unknownargs
    source = source.strip()
    target = target.strip()
    source = source.endswith('/') and source[:-1] or source
    target = target.endswith('/') and target[:-1] or target
    source_name = source.split('/')[-1]
    target_name = target.split('/')[-1]
    if not os.path.exists(source) and not os.path.isdir(source):
        print bcolors.WARNING + '%s seems not to exist' % source + bcolors.ENDC
        return
    source_f = os.path.normpath('%s/filestore/%s' % (source, source_name))
    if not os.path.exists(source_f) and not os.path.isdir(source_f):
        print bcolors.WARNING + '%s seems not to exist' % source_f + bcolors.ENDC
        return
    source_d = os.path.normpath('%s/dump/%s.dmp' % (source, source_name))
    if not os.path.exists(source_d):
        print bcolors.WARNING + '%s seems not to exist' % source_d + bcolors.ENDC
        return
    if not os.path.exists(source) and not os.path.isdir(source):
        print bcolors.WARNING + '%s seems not to exist' % source + bcolors.ENDC
        return
    if not os.path.exists(target) and not os.path.isdir(target):
        print bcolors.WARNING + '%s seems not to exist' % target + bcolors.ENDC
        return
    target_d = os.path.normpath('%s/dump/%s.dmp' % (target, target_name))
    target_f = os.path.normpath('%s/filestore/%s' % (target, target_name))

    cmd_lines = [
        'rsync -av %s  %s' % (source_d,target_d),
        'rsync -av --delete %s/  %s/' % (source_f,target_f),
    ]
    counter = 0
    if args.remote_host:
        rh = args.remote_host
        ru = args.remote_user
        # we could reed the following from the config files
        if ru == 'root':
            home = '/root/odoo_instances/'
        else:
            home = os.path.expanduser('~/odoo_instances/')
        target_d = os.path.normpath('%s@%s:%s%s/dump/%s.dmp' % (ru, rh, home, target, target_name))
        target_f = os.path.normpath('%s@%s:%s%s/filestore/%s' % (ru, rh, home, target, target_name))
        cmd_lines = [
            'rsync -av %s  %s' % (source_d,target_d),
            'rsync -av --delete %s/  %s/' % (source_f,target_f),
        ]
        for cmd_line in cmd_lines:
            counter +=1
            if args.verbose:
                print 'counter:', counter
            if not cmd_line:
                continue
            print '-' * 80
            print cmd_line
            p = subprocess.Popen(
                cmd_line,
                stdout=PIPE,
                env=dict(os.environ,  PATH='/usr/bin'),
                shell=True)
            if args.verbose:
                result = p.communicate()
                print result[0]
                if result[1]:
                    print bcolors.FAIL + 'an error occured:\n'
                    print                '-----------------\n'+ bcolors.ENDC
                    print result[1]
                    print                
            else:
                p.communicate()
        print final_message % (target, target)            
    else:
        for cmd_line in cmd_lines:
            counter +=1
            if args.verbose:
                print 'counter:', counter
            if not cmd_line:
                continue
            print '-' * 80
            print cmd_line
            p = subprocess.Popen(
                cmd_line,
                stdout=PIPE,
                env=dict(os.environ,  PATH='/usr/bin'),
                shell=True)
            if args.verbose:
                result = p.communicate()
                print result[0]
                if result[1]:
                    print bcolors.FAIL + 'an error occured:\n'
                    print                '-----------------\n'+ bcolors.ENDC
                    print result[1]
                    print
                else:
                    print final_message % (target, target)

            else:
                p.communicate()        

if   __name__ == '__main__'  :
    main()
