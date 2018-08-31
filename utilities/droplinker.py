#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import shutil
from pprint import pprint
from name_completer import SimpleCompleter

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

try:
    from ruamel.std.argparse import ArgumentParser, set_default_subparser
    import argparse
except ImportError:
    print('*' * 80)
    print(bcolors.WARNING +bcolors.FAIL + 'please run bin/pip install -r install/requirements.txt' + bcolors.ENDC)
    print('not all libraries are installed')
    print('*' * 80)
    sys.exit()
    
def main(opts):
    # make sure project folder exists in Dropbox
    projpath = BASE_INFO['project_path']
    dbfullpath = '%s/%s' % (opts.dropboxpath, os.path.split(projpath)[-1])
    if not os.path.exists(dbfullpath):
        os.makedirs(dbfullpath)
    site_name = opts.name
    if not site_name:
        print(bcolors.WARNING + 'sitename needed' + bcolors.ENDC)
        return
    if not SITES.get(site_name):
        print('%s is not a known site' % site_name)
        return
    
    dbsitepath = '%s/%s' % (dbfullpath, site_name)
    dbsiteaddonpath = '%s/%s/%s_addons' % (dbfullpath, site_name, site_name)
    sitepath = '%s/%s/%s' % (projpath, site_name, site_name)
    siteaddonpath = '%s/%s/%s/%s_addons' % (projpath, site_name, site_name, site_name)
    if not os.path.exists(sitepath):
        print('site %s is not yet created. Please create it with\nbin/c -c %s' % (site_name, site_name))
    if not os.path.exists(dbsitepath):
        os.makedirs(dbsitepath)
    # if both targetpath and sourcepath exist we check whether siteaddonpath is a link to dbsiteaddonpath
    if os.path.exists(dbsiteaddonpath) and os.path.exists(siteaddonpath):
        if not os.path.islink(siteaddonpath):
            # we rename it ..
            try:
                os.rename(siteaddonpath, '%s.ori' % siteaddonpath)
                print((bcolors.WARNING + '%s renamed to %s' + bcolors.ENDC) % (siteaddonpath, dbsiteaddonpath))
            except:
                print((bcolors.FAIL + 'could not rename %s to %s.ori' + bcolors.ENDC) % (siteaddonpath, siteaddonpath))
                return 
        else:
            # all set
            print('%s %sallready a link to%s %s' % (siteaddonpath,bcolors.WARNING, bcolors.ENDC, dbsiteaddonpath))
            return
    if (not os.path.exists(dbsiteaddonpath)) and os.path.exists(siteaddonpath):
        if os.path.isdir(siteaddonpath):
            # we create the the folder on dropbox by moving the folder
            try:
                shutil.move(siteaddonpath, dbsiteaddonpath)
            except:
                print((bcolors.FAIL + 'could not move %s to %s' + bcolors.ENDC) % (siteaddonpath, dbsiteaddonpath))
                return
    # now we create a link
    os.symlink(dbsiteaddonpath, siteaddonpath)
    print('%s %snow is a link to%s %s' % (siteaddonpath, bcolors.WARNING, bcolors.ENDC, dbsiteaddonpath))
        
        

if __name__ == '__main__':
    usage = "droplinker.py helps to link the addons folder of a site maintained by odoo_sites to Dropbox" \
    "so it can be used from more than one computer without the need to create a repository." \
    "\n-h for help on usage"
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument(
        "-n", "--name",
        action="store", dest="name", default=False,
        help = 'name of the site to link'
        )
    
    parser.add_argument(
        "-D", "--dropboxpath",
        action="store", dest="dropboxpath", default=os.path.expanduser('~/Dropbox'),
        help = 'path to the dropbox folder. Default = %s' % os.path.expanduser('~/Dropbox')
        )

    opts, unknownargs = parser.parse_known_args()
    if not opts.name and unknownargs:
        unknownargs = [a for a in unknownargs if a and a[0] != '-']
        if unknownargs:
            opts.__dict__['name'] = unknownargs[0]
            
    main(opts)
    