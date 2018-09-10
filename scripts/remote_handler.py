#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import logging
from optparse import OptionParser
import subprocess
from subprocess import PIPE
from config import FOLDERNAMES, SITES, SITES_LOCAL, BASE_PATH, BASE_INFO, ACT_USER, APACHE_PATH, NGINX_PATH, MARKER, bcolors
from copy import deepcopy

from scripts.create_handler import InitHandler
from scripts.utilities import collect_options
HA = """
    %s
    """
HL = "    ServerAlias %s\n"

class RemoteHandler(InitHandler):
    def __init__ (self, opts, sites=SITES):
        super(RemoteHandler, self).__init__(opts, sites)

        # ----------------------------------
        # add_site_to_apache
        # create virtual host entry for apache
        # if user is allowed to write to the apache directory, add it to
        #   sites_available and sites_enabled
        # if not, just print it out
        # @opts             : option instance
        # @default_values   : dictionary with default values
        # ----------------------------------
    def add_site_to_apache(self):
        """
        create virtual host entry for apache
        if user is allowed to wite to the apache directory, add it to
          sites_available and sites_enabled
        if not, just print it out
        @opts             : option instance
        @default_values   : dictionary with default values
        """
        opts = self.opts
        default_values = self.default_values
        default_values['marker'] = MARKER
        site_name = self.site_name
        if site_name not in SITES:
            print('%s is not known in sites.py' % site_name)
            return
        df = deepcopy(default_values)
        site_info = self.flatten_site_dic(site_name)
        df['vservername'] = site_info.get('vservername', '    www.%s.ch' % site_name)
        aliases_string = ''
        for alias in site_info.get('vserveraliases', []):
            aliases_string += HL % alias
        df['serveralias'] = aliases_string.rstrip()
        df.update(site_info)
        template = open('%s/templates/apache.conf' % default_values['sites_home'], 'r').read() % df
        #template = template % d
    
        print(template)
        apa = '%s/sites-available/%s.conf' % (APACHE_PATH, site_name )
        ape = '%s/sites-enabled/%s.conf' % (APACHE_PATH, site_name )
        try:
            open(apa, 'w').write(template)
            if os.path.exists(ape):
                try:
                    os.unlink(ape)
                except:
                    pass # exists ??
            try:
                os.symlink(apa, ape)
            except:
                pass
            print("%s added to apache" % site_name)
            print('restart apache to activate')
        except:
            print("could not write %s" % apa)

    # ----------------------------------
    # add_site_to_nginx
    # create virtual host entry for nginx
    # if user is allowed to write to the nginx directory, add it to
    #   sites_available and sites_enabled
    # if not, just print it out
    # @opts             : option instance
    # @default_values   : dictionary with default values
    # ----------------------------------
    def add_site_to_nginx(self):
        """
        create virtual host entry for nginx
        if user is allowed to wite to the nginx directory, add it to
          sites_available and sites_enabled
        if not, just print it out
        @opts             : option instance
        @default_values   : dictionary with default values
        """
        opts = self.opts
        default_values = self.default_values
        default_values['marker'] = MARKER
        site_name = self.site_name
        
        if site_name not in SITES:
            print('%s is not known in sites.py' % site_name)
            return

        df = deepcopy(default_values)
        docker_info = self.site['docker']
        df['odoo_port'] = docker_info['odoo_port']
        long_polling_port = docker_info.get('odoo_longpoll')
        if not long_polling_port:
            long_polling_port = int(docker_info['odoo_port']) + 10000
        df['odoo_longpoll'] = long_polling_port
        site_info = self.flatten_site_dic(site_name)
        df['vservername'] = site_info.get('vservername', '    www.%s.ch' % site_name)
        lets_encrypt = site_info.get('letsencrypt')
        if not lets_encrypt:
            print(bcolors.WARNING + '*' * 80)
            print('could not read lets_encrypt_path the site description')
            print('this is needed to add the site to nginx')
            print('you can fix this by executing: bin/e %s ' % site_name)
            print("and addinga stanza like")
            print("""
            'letsencrypt' : {
                'path' :'/etc/letsencrypt/live/'
            },
            """)
            print('*' * 80 + bcolors.ENDC)
            return
        
        lets_encrypt_path = lets_encrypt['path']
        df['lets_encrypt_path'] = lets_encrypt_path
        df.update(site_info)
        template_80 = open('%s/templates/nginx.conf.80' % default_values['sites_home'], 'r').read() % df
        #template_443 = open('%s/templates/nginx.conf.443' % default_values['sites_home'], 'r').read() % df
        #template = template % d
    
        print(template_80)
        #print template_443
        apa_80 = '%s/sites-available/%s-80' % (NGINX_PATH, site_name )
        ape_80 = '%s/sites-enabled/%s-80' % (NGINX_PATH, site_name )
        #apa_443 = '%s/sites-available/%s-443' % (NGINX_PATH, site_name )
        #ape_443 = '%s/sites-enabled/%s-443' % (NGINX_PATH, site_name )
        try:
            open(apa_80, 'w').write(template_80)
            #open(apa_443, 'w').write(template_443)
            if os.path.exists(ape_80):
                try:
                    os.unlink(ape_80)
                except:
                    pass # exists ??
            try:
                os.symlink(apa_80, ape_80)
            except:
                pass
            #if os.path.exists(ape_443):
                #try:
                    #os.unlink(ape_443)
                #except:
                    #pass # exists ??
            #try:
                #os.symlink(apa_443, ape_443)
            #except:
                #pass
            print("%s added to nginx" % site_name)
            print('restart nginx to activate')
        except:
            print("could not write %s" % ape_80)
            
    # ----------------------------------
    # flatten_site_dic
    # check whether a site dic has all substructures
    # flatten them into a dictonary without substructures
    # @ site_name       : dictonary to flatten
    # ----------------------------------
    def flatten_site_dic(self, site_name, sites=SITES):
        """
        check whether a site dic has all substructures
        flatten them into a dictonary without substructures
        @ site_name       : dictonary to flatten
        """
        res = {}
        site_dic = sites.get(site_name)
        if not site_dic:
            print('error: %s not found in provided list of sites' % site_name)
            return
        sd = site_dic.copy()
        parts = [
            'docker',
            'remote_server',
            'apache',
        ]
        vparts = [
            'slave_info',
        ]
        both = parts + vparts
        for k, v in list(sd.items()):
            if not k in both:
                res[k] = v
        for p in parts:
            pDic = sd.get(p)
            if not pDic:
                print('error: %s not found site description for %s' % (p, site_name))
                return
            for k, v in list(pDic.items()):
                res[k] = v
        for p in vparts:
            pDic = sd.get(p, {})
            for k, v in list(pDic.items()):
                res[k] = v
        return res
