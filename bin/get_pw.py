#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import os
import sys
import argparse
from pprint import pprint

sys.path.insert(0, os.getcwd())

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
    
def main(opts):
    from sites_pw import SITES_PW
    if opts.name in SITES_PW:
        pprint(SITES_PW[opts.name])
    else:
        print(bcolors.FAIL, 'stanza %s not found' % opts.name, bcolors.ENDC)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        action="store", 
        dest="name",
        help="name of the stanza")

    opts = parser.parse_args()
    main(opts)    