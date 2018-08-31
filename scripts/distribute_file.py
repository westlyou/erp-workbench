#!/usr/bin/python
# -*- encoding: utf-8 -*-

import glob
import os
import sys
import subprocess
from subprocess import PIPE
from optparse import OptionParser
import shutil
import inspect
sys.path.insert(0, os.getcwd())
from utilities import list_sites, SITES, BASE_PATH

def main(opts, args):
    """
    """
    if opts.list_sites:
        list_sites(SITES)
        return
    for a in args:
        if not os.path.isfile(a):
            print a, 'is not a file'


if __name__ == '__main__':
    usage = "distribute_file.py -h for help on usage"
    parser = OptionParser(usage=usage)

    parser.add_option(
        "-l", "--list",
        action="store_true", dest="list_sites", default=False,
        help = 'list available sites'
    )
    parser.add_option(
        "-n", "--name",
        action="store", dest="name", default='all',
        help = 'name of the site to which to copy the file. default all'
    )
    (opts, args) = parser.parse_args()
    main(opts,  args)
