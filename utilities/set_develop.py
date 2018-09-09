#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import shutil
from pprint import pprint

sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
from config import BASE_INFO, SITES

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

import argparse
    
def main(opts):
    # make sure project folder exists in Dropbox
    projpath = BASE_INFO['project_path']
    datapath = BASE_INFO['erp_server_data_path']
    site_name = opts.name
    if not site_name:
        print(bcolors.WARNING + 'sitename needed' + bcolors.ENDC)
        return
    if not SITES.get(site_name):
        print('%s is not a known site' % site_name)
        return
    
    sitepath = '%s/%s/%s' % (projpath, site_name, site_name)
    siteaddonpath = '%s/%s/%s/%s_addons' % (projpath, site_name, site_name, site_name)
    if not os.path.exists(sitepath):
        print('site %s is not yet created. Please create it with\nbin/c -c %s' % (site_name, site_name))
        return
    addon = opts.addon
    addonspath = '%s/%s/addons' % (datapath, site_name)
    if opts.list:
        print(addonspath)
        print(bcolors.OKBLUE)
        for f in os.listdir(addonspath):
            print(f)
        print(bcolors.ENDC)
        return
    if not addon:
        print(bcolors.WARNING + 'addon needed' + bcolors.ENDC)
        return
    if not os.path.exists(addonspath):
        print('%s does not exist' % addonspath)
        return
    stop = opts.stop
    target_path = '%s/%s' % (siteaddonpath, addon)
    if stop:
        # we remove from project folder
        # all changes should allready be processed
        target_path
        try:
            shutil.rmtree(target_path)
            print(bcolors.OKGREEN, '%s removed' % target_path, bcolors.ENDC)
        except:
            print(bcolors.FAIL, 'Could not remove:%s' % target_path, bcolors.ENDC)
    else:
        apath = '%s/%s' % (addonspath, addon)
        if os.path.exists(target_path):
            print('%s allready exists' % target_path)
        if os.path.exists(apath):
            shutil.move(apath, siteaddonpath)
            print(bcolors.OKGREEN, 'moved %s to %s' % (addon, siteaddonpath), bcolors.ENDC)
        else:
            print(bcolors.FAIL, '%s not found' % apath, bcolors.ENDC)
            

if __name__ == '__main__':
    usage = bcolors.WARNING + "\nset_develop.py moves an addon to the developement folder in the sites bildout folder\n" \
    "the parameter -s removes it from there." \
    "\n-h for help on usage" + bcolors.ENDC
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument(
        "-n", "--name",
        action="store", dest="name", default=False,
        help = 'name of the site'
        )
    
    parser.add_argument(
        "-a", "--addon",
        action="store", dest="addon",
        help = 'addon to deal with'
        )

    parser.add_argument(
        "-l", "--list",
        action="store_true", dest="list", default=False,
        help = 'list addons'
        )
    parser.add_argument(
        "-s", "--stop",
        action="store_true", dest="stop", default=False,
        help = 'stop treating addon as in develop mode'
        )
    opts, unknownargs = parser.parse_known_args()
    if not opts.name:
        if unknownargs:
            opts.__dict__['name'] = unknownargs.pop(0)
            if unknownargs:
                opts.__dict__['addon'] = unknownargs.pop(0)
            
    main(opts)
    