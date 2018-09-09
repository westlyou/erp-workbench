
#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import logging
import re
from glob import glob
from config import BASE_PATH

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
    print('*' * 80)
    print(bcolors.WARNING +bcolors.FAIL + 'please run bin/pip install -r install/requirements.txt' + bcolors.ENDC)
    print('not all libraries are installed')
    print('*' * 80)
    sys.exit()

ALIAS_HEADER = ""
ALIAS = """
# %(lname)s
alias  cu_%(sname)s="cd %(ppath)s/%(lname)s/"
"""
ALIAS_LINE = 'alias  cu_%(sname)s="cd %(path)s"\n'

AMARKER = '##-----customer-alias-marker %s-----##'
ABLOCK = """%(aliasmarker_start)s
# please do not change the lines between the two markers
# they are managed by the odooMaker scripts
%(alias_header)s
%(alias_list)s
%(aliasmarker_end)s"""

class AliasHandler(object):
    def __init__(self, opts):
        self.opts = opts
        
    def add_aliases(self):
        """
        """
        # # check if project exists
        # inner = default_values['inner']
        # if not os.path.exists(inner):
        #     # project does not yet exist, just return
        #     return
        # # remember where we came from
        # adir = os.getcwd()
        # os.chdir('%s' % inner)
        # p = subprocess.Popen(['bin/python', 'alias.py'],
        #                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # out, err = p.communicate()
        # return True
        opts = self.opts
        pp = os.path.expanduser(opts.path)
        marker_start = AMARKER  % 'start'
        marker_end = AMARKER  % 'end'
        # where do we want to add our aliases?
        alias_script = "bash_aliases"
        try:
            dist = open("/etc/lsb-release").readline()
            dist = dist.split("=")
            print(dist[1])
            if dist[1].strip("\n") == "LinuxMint":
                alias_script = "bashrc"
            elif dist[1].strip("\n") == "Ubuntu":
                alias_script = "bash_aliases"
        except:
            print('could not determine linux distribution')
            pass
        home = os.path.expanduser("~")
        alias_path = '%s/.%s' % (home, alias_script)
        try:
            data = open(alias_path, 'r').read()
        except:
            data = ''
        data = data.split('\n')
        alias_str = ''
        # loop over data and add lines to the result untill we see the marker
        # then we loop untill we get the endmarker or the end of the file
        start_found = False
        end_found = False
        for line in data:
            if not start_found:
                if line.strip() == marker_start:
                    start_found = True
                    continue
                alias_str += '%s\n' % line
            else:
                if line.strip() == marker_end:
                    end_found = True
                    start_found = False
        # we no have all lines without the constucted alias in alias_str
        # we add a new block of aliases to it
        alias_str += ABLOCK % {
            'aliasmarker_start' : marker_start,
            'aliasmarker_end' : marker_end,
            'alias_list' : self.create_aliases(),
            'alias_header' : ALIAS_HEADER % {'pp': pp},
            'ppath' : pp,
            }
    
        open(alias_path, 'w').write(alias_str)
    
    
    def create_aliases(self):
        """
        """
        opts = self.opts
        pp = os.path.expanduser(opts.path)
        # shortnamesconstruct
        files = glob('%s/*' % pp)
        alias_paths = [f for f in files if os.path.isdir(f)]
        names = [os.path.split(p)[-1] for p in alias_paths]
        names.sort()
        long_names = alias_paths
        for n in names:
            if n in alias_paths:
                continue # the  short ones
            alias_paths.append(n)
            long_names.append(n)
        result = ALIAS_LINE % {'sname' : 'pro', 'path' : pp }
        processed = []
        for i in range(len(alias_paths)):
            if os.path.exists('%s/%s' % (pp, long_names[i])):
                if long_names[i] in processed:
                    continue
                result += ALIAS % {
                    'sname' : alias_paths[i],
                    'lname' : long_names[i],
                    'ppath' : pp,
                }
                processed.append(long_names[i])
    
        return result

def main(opts):
    handler = AliasHandler(opts)
    handler.add_aliases()

if __name__ == '__main__':
    
    usage = "create_customer_aliases.py" \
    " adds aliases for each customer found in the customer folder" \
    " the alias is cu_CUSTOMERNAME"
    "\n-h for help on usage"
    parser = argparse.ArgumentParser(usage=usage, add_help=False)
    parser.add_argument(
        "-p", "--path",
        action="store", dest="path", default="~/%s/customers" % BASE_PATH,
        help = 'name of the site to create'
    )
    args, unknownargs = parser.parse_known_args()
    main(args) 
    