#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import logging
import re
from pprint import pformat
import subprocess
from subprocess import PIPE
from copy import deepcopy
#from config.config_data.base_info import base_info as BASE_INFO
from config import BASE_INFO
from config import ACT_USER
from scripts.messages import *
from scripts import bcolors

class UpdateError(subprocess.CalledProcessError):
    """Specific class for errors occurring during updates of existing repos.
    """

# --------------------------------------
# sites_handler.py maintains two set of data
# 1. local_data.py
#   this file contains info about the local user,
#   like with what credentials she/he will be accessing local and remote data
#   if it does not exist, it will be copied from templates
#   and must be editted afterwards
#
# 2. sites_global/*.py and sites_local/*.py.py
#   ssites_global contains descriptions of of sites. they are ment to be
#   maintained in a remote repo
#   sites_local1 contain the same list of site descriptions.
#   However they will be only handeled on the local computer.

# -------------------------------------------------------------
# the marker is used to place a new site when the file is updated
# -------------------------------------------------------------
# defined in messages.py
#MARKER = '# ---------------- marker ----------------'
SITES_LIST_INI ="""from .sites_local import SITES_L
from .sites_global import SITES_G
"""
class SitesHandler(object):
    def __init__(self, base_path, template_name='', preset_values=''):
        self.base_path = base_path
        #self.check_and_copy_local_data()
        self.template_name = template_name
        self.preset_values = preset_values

    # robert refacture
    # def check_and_copy_local_data(self):
    #     # make sure config localdata exists and is correctly edited
    #     p1 =  '%s/config/localdata.py' % self.base_path
    #     p2 =  '%s/templates/localdata.py' % self.base_path
    #     if not os.path.exists(p1):
    #         # BB, move localdata to config
    #         if os.path.exists('%s/localdata.py' % self.base_path):
    #             open(p1, 'w').write(open('%s/localdata.py' % self.base_path, 'r').read())
    #             print(LOCALDATA_MOVED % ('%s/localdata.py' % self.base_path, p1))
    #             os.unlink('%s/localdata.py' % self.base_path)
    #             try:
    #                 os.unlink('%s/localdata.pyc' % self.base_path)
    #             except:
    #                 pass
    #             sys.exit()
    #         # silently copy the defaults file
    #         open(p1, 'w').write(open(p2, 'r').read())
    #         print(LOCALDATA_CREATED % p1)
    #         sys.exit()
    #     else:
    #         data = open(p1, 'r').read().split('\n')
    #         m = re.compile(r'[^#]+UNEDITED')
    #         for line in data:
    #             if m.match(line):
    #                 print(LOCALDATA_NOT_EDITED % p1)

    def check_and_create_sites_repo(self, force = False):
        # check whether sites repo defined in BASEINFO exists
        # if not download and install it
        sites_list_path = BASE_INFO.get('sitesinfo_path')
        if not sites_list_path:
            return '' # not yet configured
        sites_list_url = BASE_INFO.get('sitesinfo_url')
        if sites_list_url == 'localhost':
            bp = '/' + '/'.join([p for p in sites_list_path.split('/') if p][:-1])
            if not os.path.exists(bp):
                print(LOCALSITESLIST_BASEPATH_MISSING % bp)
            p1 = sites_list_path
            if not os.path.exists(p1):
                os.makedirs(p1, exist_ok=True)
                # add __init__.py
                open('%s/__init__.py' % p1, 'w').write(SITES_LIST_INI)
                template = open('%s/templates/newsite.py' % self.base_path, 'r').read()
                template = template.replace('xx.xx.xx.xx', 'localhost')
                # default values for the demo sites
                defaults = {
                    'site_name' : 'demo_global', 
                    'marker' : self.marker,
                    'base_sites_home' : '/home/%s/erp_workbench' % ACT_USER,
                    'odoo_version' : '12',
                    'base_url' : 'demo_global',
                    'local_user_mail' : 'mail@localhost.com',
                    'remote_server' : 'localhost',
                    'docker_port' : 8800,
                    'docker_long_poll_port' : 18800,
                }                
                # create global sites
                os.mkdir('%s/sites_global' % p1)
                __ini__data = open('%s/templates/sites_list__init__.py' % self.base_path).read()
                open('%s/sites_global/__init__.py' % p1, 'w').write(__ini__data)
                open('%s/sites_global/demo_global.py' % p1, 'w').write(SITES_GLOBAL_TEMPLATE % (
                    'demo_global', template % defaults))
                # create local sites
                os.mkdir('%s/sites_local' % p1)
                __ini__data = __ini__data.replace('SITES_G', 'SITES_L')
                open('%s/sites_local/__init__.py' % p1, 'w').write(__ini__data)
                defaults['site_name'] = 'demo_local'
                open('%s/sites_local/demo_local.py' % p1, 'w').write(SITES_GLOBAL_TEMPLATE % (
                    'demo_local', template % defaults))
                print(LOCALSITESLIST_CREATED % (
                    os.path.normpath('%s/sites_global/demo_global.py' % p1), 
                    os.path.normpath('%s/sites_local/demo_local.py' % p1)))
                sys.exit()
        elif not os.path.exists(sites_list_path):
            # try to git clone sites_list_url
            act = os.getcwd()
            dp = '/' + '/'.join([p for p in sites_list_path.split('/') if p][:-1])
            os.chdir(dp)
            cmd_lines = ['git clone %s ' % sites_list_url]
            for cmd_line in cmd_lines:
                p = subprocess.Popen(
                    cmd_line,
                    stdout=PIPE,
                    env=dict(os.environ,  PATH='/usr/bin'),
                    shell=True)
                p.communicate()
            print(LOCALSITESLIST_CLONED % (sites_list_url, os.getcwd()))
            os.chdir(act)
        return sites_list_path

    @property
    def marker(self):
        #if self.parsername == 'docker':
            #return self.docker_rpc_host
        return MARKER

    def get_sites(self):
        sites_list_path = self.check_and_create_sites_repo()
        if not sites_list_path:
            return (None, None)
        self.sites_list_path = sites_list_path
        SITES_L = {}
        # if sites_list_path is != self.self.base_path + '/sites_list' we have to add it to the path
        sites_list_path = os.path.normpath(sites_list_path)
        if sites_list_path != os.path.normpath(self.base_path + '/sites_list'):
            parts = sites_list_path.split('/')
            if parts[-1] == 'sites_list':
                parts = [p for p in parts if p]
                sites_list_path = '/' + '/'.join(parts[:-1])
            sys.path.insert(0, os.path.normpath(sites_list_path))
        try:
            from sites_list import SITES_G, SITES_L
            #from sites_list.sites_local import SITES_L
        except ImportError:
            from bcolors import bcolors
            print(bcolors.FAIL)
            print('*' * 80)
            print('could not import sites list')
            print(bcolors.ENDC)
            return [], []
            
        # -------------------------------------------------------------
        # test code from prakash to set the local sites value to true
        #------------------------------------------------------------
        for key in list(SITES_L.keys()):
            SITES_L[key]['is_local'] = True

        SITES = {}
        SITES.update(SITES_G)
        SITES.update(SITES_L)

        # -------------------------------------------------------------
        # merge passwords
        # -------------------------------------------------------------
        DEFAULT_PWS = {
            'odoo_admin_pw' : '',
            #'email_pw_incomming' : '',
            #'email_pw_outgoing' : '',
        }
        # read passwords
        SITES_PW = {}
        try:
            from sites_pw import SITES_PW
        except ImportError:
            pass
        # merge them
        for key in list(SITES.keys()):
            kDic = SITES_PW.get(key, DEFAULT_PWS)
            for k in list(DEFAULT_PWS.keys()):
                SITES[key][k] = kDic.get(k, '')
            # get dockerhub password if available
            docker_info = SITES[key].get('docker', {})
            docker_hub_info = SITES[key].get('docker_hub', {})
            hub_name  = docker_info.get('hub_name', '')
            if hub_name:
                # docker hub passwords are a separte block
                kDic_hub = SITES_PW.get('docker_hub', {})
                if kDic_hub:
                    # get docker_hub block from pw struct
                    kdic_hub_info = kDic_hub.get(
                        hub_name, {} # get image repository for this site
                    )
                    hub_user = docker_hub_info.get(hub_name, {}).get('user')
                    if hub_user:
                        docker_hub_pw = kdic_hub_info.get(hub_user, {}).get('docker_hub_pw', '')
                        if docker_hub_pw:
                            SITES[key]['docker_hub'][hub_name]['docker_hub_pw'] = docker_hub_pw

        return SITES, SITES_L
    
    def drop_site(self, template_name):
        SITES, SITES_L = self.get_sites()
        sites_list_path = self.sites_list_path
        if template_name in list(SITES_L.keys()):
            try:
                os.unlink('%s/sites_local/%s.py' % (sites_list_path, template_name))
                os.unlink('%s/sites_local/%s.pyc' % (sites_list_path, template_name))
            except:
                pass
            return True
        elif template_name in list(SITES.keys()):
            try:
                os.unlink('%s/sites_global/%s.py' % (sites_list_path, template_name))
                os.unlink('%s/sites_global/%s.pyc' % (sites_list_path, template_name))
            except:
                pass
            return True
        print((bcolors.FAIL))
        print(('*' * 80))
        print(('%s is not an existing site description' % template_name))
        print((bcolors.ENDC))
        
    
    def find_template(self, template_name):
        sites_list_path = self.check_and_create_sites_repo()
        SITES, SITES_L = self.get_sites()
        if template_name in list(SITES.keys()):
            return open('%ssites_global/%s.py' % (sites_list_path, template_name)).read()
        elif template_name in list(SITES_L.keys()):
            return open('%ssites_local/%s.py' % (sites_list_path, template_name)).read()
        print((bcolors.FAIL))
        print(('*' * 80))
        print(('%s is not an existing site description' % template_name))
        print((bcolors.ENDC))
               
    def add_site_global(self, handler, template_name = '', preset_values = {}):
        """add a global site to the list of site
        
        Arguments:
            handler {instance} -- the handler is the calling instance. trough it, all the callers 

        
        Keyword Arguments:
            template_name {str} -- the name of the template to use to construct the site description (default: {''})
            preset_values {dict} -- aset of values to use as default when constructing the site (default: {{}})
        
        Returns:
            [type] -- [description]
        """

        self.handler = handler
        handler.default_values['base_sites_home'] = '/root/erp_workbench' 
        handler.default_values['base_url'] = ('%s.ch' % handler.site_name)
        template = ''
        remote_url = handler.opts.use_ip or 'xx.xx.xx.xx'
        no_outer = False
        if template_name:
            template = self.find_template(template_name)
            # now we replace all instances of the old name with the new one
            template = template.replace(template_name, handler.opts.name)
            no_outer = True # do not wrap the template in an outer dict
            # 'remote_url' : '176.9.142.21',  # alice2
            #template['remote_server']['remote_url'] = remote_url
            #template = '"%s" : %s' % (handler.opts.name, pformat(template))
        if not template:
            template = open('%s/templates/newsite.py' % handler.sites_home, 'r').read() % handler.default_values
            template = template.replace('xx.xx.xx.xx', remote_url)
        return self._add_site('G', template, no_outer)

    def add_site_local(self, handler, template_name = ''):
        self.handler = handler
        handler.default_values['base_sites_home'] = '/home/%s/erp_workbench' % ACT_USER
        handler.default_values['base_url'] = ('%s.ch' % handler.site_name)
        template = ''
        if template_name:
            template = self.find_template(template_name)
            # 'remote_url' : '176.9.142.21',  # alice2
            template['remote_server']['remote_url'] = 'localhost'
            template = '"%s" : %s' % (handler.opts.name, pformat(template))
        if not template:
            template = open('%s/templates/newsite.py' % handler.sites_home, 'r').read() % handler.default_values
            template = template.replace('xx.xx.xx.xx', 'localhost')
        return self._add_site('L', template, False)

    def _add_site(self, where, template, no_outer):
        site_name = self.handler.site_name
        if self.handler.sites.get(site_name):
            print("site %s allready defined" % site_name)
            return
        if site_name.find('.') > -1 :
            print(SITE_ADDED_NO_DOT % site_name)
            return
        if where not in ['L', 'G']:
            return
        if not no_outer:
            outer_template = SITES_GLOBAL_TEMPLATE % (site_name, template)
        else:
            outer_template = template
        if where == 'G':
            #m = re.compile(r'\n%s' % MARKER)
            #sites = open('%s/sites_global.py' % sites_list_path).read()
            #if not m.search(sites):
                #print "ERROR: the marker could not be found in sites.py"
                #print "make sure it exists and starts at the beginning of the line"
                #return
            #open('%s/sites_global.py' % sites_list_path, 'w').write(m.sub(template, sites))
            
            # add a new file with the sites info
            f = open('%s/sites_global/%s.py' % (BASE_INFO['sitesinfo_path'], site_name), 'w').write(outer_template)
        elif where == 'L':
            site_name = self.handler.site_name
            f = open('%s/sites_local/%s.py' % (BASE_INFO['sitesinfo_path'], site_name), 'w').write(outer_template)
        return True
        

    def pull(self, auto='check'):
        actual = os.getcwd()
        if not hasattr(self, 'sites_list_path'):
            return
        if auto =='check':
            if not BASE_INFO.get('sites_autopull', ''):
                return
        os.chdir(self.sites_list_path)
        p = subprocess.Popen(
            'git pull',
            stdout=PIPE,
            env=dict(os.environ,  PATH='/usr/bin'),
            shell=True)
        p.communicate()
        os.chdir(actual)
