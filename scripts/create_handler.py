# bin/python
# -*- encoding: utf-8 -*-

# import warnings
import sys
import os
# import logging
import re
# import socket
import subprocess
from subprocess import PIPE
from config import FOLDERNAMES, SITES, SITES_LOCAL, BASE_PATH, BASE_INFO, BASE_INFO_FILENAME, \
    ACT_USER, LOGIN_INFO_FILE_TEMPLATE, REQUIREMENTS_FILE_TEMPLATE, MODULES_TO_ADD_LOCALLY, VERSION, NEED_NAME, \
    NO_NEED_NAME, NO_NEED_SERVER_IP, ODOO_VERSIONS, FLECTRA_VERSIONS
from config.localdata import DB_USER, DB_PASSWORD, REMOTE_USER_DIC
try:
    from config.localdata import DB_PASSWORD_LOCAL
except ImportError:
    DB_PASSWORD_LOCAL = 'admin'  # bbb
from copy import deepcopy
from scripts.name_completer import SimpleCompleter
import stat
import shutil
import psycopg2
import psycopg2.extras
import urllib.request, urllib.error, urllib.parse
from pprint import pformat
from scripts.update_local_db import DBUpdater
from scripts.utilities import collect_options, _construct_sa, bcolors, find_addon_names
from scripts.messages import *
from sets import Set
import shutil

# tool to check and fix site structure
from scripts.fixup_site import fixup_sites, fixup_remote_site
"""
https://breakingcode.wordpress.com/2013/03/11/an-example-dependency-resolution-algorithm-in-python/
https://pypi.python.org/pypi/pipdeptree/0.8.0
http://stackoverflow.com/questions/14242295/build-a-dependency-graph-in-python
import networkx as nx
import re

regex = re.compile(r'^([A-Z]+)::Requires\s+=\s([A-Z"]+)$')

G = nx.DiGraph()
roots = set()
for l in raw.splitlines():
    if len(l):
        target, prereq = regex.match(l).groups()
        if prereq == '""':
            roots.add(target)
        else:
            G.add_edge(prereq, target)

Now print(the tree(s):)

for s in roots:
    print(s)
    spacer = {s: 0}
    for prereq, target in nx.dfs_edges(G, s):
        spacer[target] = spacer[prereq] + 2
        print('{spacer}+-{t}'.format()
                                     spacer=' ' * spacer[prereq],
                                     t=target)
    print('')

this prints:

A
+-H
+-B
  +-C

AA
+-BB
  +-CC
"""

# the templatefile contains placeholder
# that will be replaced with real values
LOGIN_INFO_TEMPLATE_FILE = '%s/login_info.cfg.in'
BASE_INFO_TEMPLATE = """base_info = %s"""
"""
create_new_project.py
---------------------
create a new odoo project so we can easily maintain a local and a remote
set of configuration files and keep them in sync.

It knows enough about odoo to be able to treat some special values correctly

"""


class RPC_Mixin(object):
    _odoo = None

    # ---------------------------------------------------------------------
    # RPC stuff
    # ---------------------------------------------------------------------

    # ----------------------------------
    # get_connection opens a connection to a database
    def get_cursor(self, db_name=None, return_connection=None):
        """
        """
        dbuser = self.db_user
        dbhost = self.db_host
        dbpw = self.db_password
        postgres_port = self.docker_postgres_port
        if not db_name:
            db_name = self.db_name

        if dbpw:
            conn_string = "dbname='%s' user=%s host='%s' password='%s'" % (
                db_name, dbuser, dbhost, dbpw)
        else:
            conn_string = "dbname='%s' user=%s host='%s'" % (
                db_name, dbuser, dbhost)
        try:
            conn = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            if postgres_port:
                conn_string += (' port=%s' % postgres_port)
                conn = psycopg2.connect(conn_string)

        cursor_d = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if return_connection:
            return cursor_d, conn
        return cursor_d

    # ----------------------------------
    # get_module_obj logs into odoo and then
    # returns an object with which we can manage the list of modules
    # bail out if we can not log into a running odoo site

    # the databse is access directly
    # the odoo server is accessed uding odoo's rpc_api.
    # read from either the config data or can be set using command line options.
    # --- database ---
    # - db_user : the user to access the servers database
    #   to check what modules are allready installed the servers database
    #   has to be accessed.
    #   option: "-dbu", "--dbuser".
    #   default: logged in user
    # - db_password
    #   option: "-p", "--dbpw".
    #   default: admin
    # - dbhost: the host on which the database is running
    #   option: "-dbh", "--dbhost"
    #   default: localhost.
    # --- user accessing the running odoo server ---
    # - rpcuser: the login user to access the odoo server
    #   option: "-rpcu", "--rpcuser"
    #   default: admin.
    # - rpcpw: the login password to access the odoo server
    #   option: "-P", "--rpcpw"
    #   default: admin.
    # - rpcport: the the odoo server is running at
    #   option: "-PO", "--port"
    #   default: 8069.

    def get_odoo(self, no_db=False, verbose=False):
        if not self._odoo:
            """
            get_module_obj logs into odoo and then
            returns an object with which we can manage the list of modules
            bail out if we can not log into a running odoo site

            the databse is access directly
            the odoo server is accessed uding odoo's rpc_api.
            read from either the config data or can be set using command line options.
            --- database ---
            - db_user : the user to access the servers database
              to check what modules are allready installed the servers database
              has to be accessed.
              option: "-dbu", "--dbuser".
              default: logged in user
            - db_password
              option: "-p", "--dbpw".
              default: admin
            - dbhost: the host on which the database is running
              option: "-dbh", "--dbhost"
              default: localhost.
            --- user accessing the running odoo server ---
            - rpcuser: the login user to access the odoo server
              option: "-rpcu", "--rpcuser"
              default: admin.
            - rpcpw: the login password to access the odoo server
              option: "-P", "--rpcpw"
              default: admin.
            - rpcport: the the odoo server is running at
              option: "-PO", "--port"
              default: 8069.
            """
            verbose = verbose or self.opts.verbose
            try:
                import odoorpc
            except ImportError:
                print(bcolors.WARNING + 'please install odoorpc')
                print(
                    'execute bin/pip install -r install/requirements.txt' + bcolors.ENDC)
                return
            try:
                # if we want to access a docker container, rpsuser and rpcpw has to be adjusted beforehand
                db_name = self.db_name
                rpchost = self.rpc_host
                rpcport = self.rpc_port
                rpcuser = self.rpc_user
                rpcpw = self.rpc_pw
                # login
                if verbose:
                    print('*' * 80)
                    print('about to open connection to:')
                    print('host:%s, port:%s, timeout: %s' %
                          (rpchost, rpcport, 1200))
                odoo = odoorpc.ODOO(rpchost, port=rpcport, timeout=1200)
                if not no_db:  # used when creating db
                    if verbose:
                        print('about to login:')
                        print('dbname:%s, rpcuser:%s, rpcpw: %s' %
                              (db_name, rpcuser, rpcpw))
                        print('*' * 80)
                    odoo.login(db_name, rpcuser, rpcpw)

            except odoorpc.error.RPCError:
                print(bcolors.FAIL + 'could not login to running odoo server host: %s:%s, db: %s, user: %s, pw: %s' %
                      (rpchost, rpcport, db_name, rpcuser, rpcpw) + bcolors.ENDC)
                if verbose:
                    return odoo
                return
            except urllib.error.URLError:
                print(bcolors.FAIL + 'could not login to odoo server host: %s:%s, db: %s, user: %s, pw: %s' %
                      (rpchost, rpcport, db_name, rpcuser, rpcpw))
                print('connection was refused')
                print('make sure odoo is running at the given address' + bcolors.ENDC)
                return
            self._odoo = odoo
        return self._odoo

    def get_module_obj(self):
        odoo = self.get_odoo()
        if not odoo:
            return
        module_obj = odoo.env['ir.module.module']
        return module_obj

    def get_odoo_modules(self):
        from odoorpc.error import RPCError
        modules = self.get_module_obj()
        mlist = modules.search([('application', '=', True)])
        result = {}
        for mid in mlist:
            m = modules.browse(mid)
            result[m.name] = m.shortdesc
        mlist = modules.search([('application', '=', False)])
        result2 = {}
        for mid in mlist:
            try:
                m = modules.browse(mid)
                result2[m.name] = m.shortdesc
            except RPCError as e:
                print(str(e))

        return result, result2

    @property
    def rpc_host(self):
        return self.rpchost

    @property
    def rpc_port(self):
        if self.parsername == 'docker':
            return self.docker_rpc_port
        return self.rpcport

    @property
    def rpc_user(self):
        if self.parsername == 'docker':
            return self.docker_rpc_user
        return self.login_info['rpc_user']

    @property
    def rpc_pw(self):
        if self.parsername == 'docker':
            return self.docker_rpc_user_pw
        return self.login_info['rpc_pw']

    def install_languages(self, languages):
        """
        install all languages in the target
        args:
            languages: list of language codes like ['de_CH, 'fr_CH']

        return:
            dictonary {code : id, ..}     
        """
        # what fields do we want to handle?
        # we get the source and target model
        languages = set(languages)
        langs = self.get_odoo().env['base.language.install']
        result = {}
        for code in languages:
            if not langs.search([('lang', '=', code)]):
                langs.browse(langs.create({'lang': code})).lang_install()
            result[code] = langs.search([('lang', '=', code)])[0]
        return result


class InitHandler(RPC_Mixin):
    # need_login_info will be set to false by local opperations
    # like --add-site that need no login
    need_login_info = True
    docker_registry = None

    def __init__(self, opts, sites=SITES):
        if opts.name:
            self.site_names = [opts.name]
        else:
            self.site_names = []
        self.opts = opts
        # make sure they are structured according to version
        self.sites = fixup_sites(SITES, VERSION)
        self.default_values = {}
        self.check_name(no_completion=True, must_match=True)
        # resolve inheritance within sites
        self.flatten_sites(self.sites)
        # collect info on what parser and what options are selected
        parsername, selected, options = collect_options(opts)
        self.selections = selected
        if not self.site_name and self.name_needed():
            result = self._complete_selection(parsername, list(self.sites.keys(
            )) + ['all'], results_only=True, prompt='sitename ?')
            if result:
                self.site_names = [result]
        if not selected:
            self._complete_selection(
                parsername, options, prompt='%s-options ?' % parsername)
            # check again if selected
            parsername, selected, options = collect_options(opts)
        self.parsername = parsername
        self.selections = selected
        self.login_info = {}
        # now we can really check whether name is given and valid
        self.check_name()
        # when we want to drop the site, nothing more needs to be done
        if opts.drop_site:
            return
        if self.site_name:
            # construct default values like list of target directories
            self.construct_defaults(self.site_name)
            self.default_values['current_user'] = ACT_USER
            self.default_values['foldernames'] = FOLDERNAMES
            # make sure also freshly introduced variables do not create an error 
            if 'odoo_nightly' not in self.default_values:
                 self.default_values['odoo_nightly'] = self.default_values['odoo_version'] 
             
            # construct path to datafolder odoo_server_data_path
            if self.need_login_info:
                self._create_login_info(self.login_info)
            #             # the following three values will be overruled by the docker registry
            # created using docker_handler.update_container_info
            # when we deal with a docker instance
            self.rpchost = opts.rpchost or 'localhost'
            self.rpcport = opts.rpcport or '8069'
            self.dbhost = self.opts.dbhost or 'localhost'
        # starting with odoo 11 we need to check what python version to use
        if self.version:
            try:
                if self.sites[opts.name].get('server_type') == 'flectra':
                    self.default_values.update(FLECTRA_VERSIONS[self.version])
                else:
                    self.default_values.update(ODOO_VERSIONS[self.version])
            except KeyError:
                print (bcolors.FAIL)
                print ('*' * 80)
                print ('%s has no %s version' % (self.sites[opts.name].get('server_type'), self.version))
                print (bcolors.ENDC)
                if not opts.edit_site:
                    raise
                    

    def _create_login_info(self, login_info):
        # ----------------------------------
        # what login do we need
        # local:
        #    local user
        #    odoo rpc
        #    odoo admin
        #    docker db user
        #    docker db password
        #    docker admin pw
        #    docker master pw
        # remote:
        #    remote usercreate_virtual_env
        #    # no password, as only key allowed
        #    odoo rpc
        #    odoo admin
        #    docker db user
        #    docker db password
        #    docker admin pw
        #    docker master pw

        # -----------------
        # local
        # -----------------
        # actual user
        if self.site:
            p = '%s/sites_global/%s.py' % (
                BASE_INFO['sitesinfo_path'], self.site_name)
            if not self.site.get('remote_server'):
                print(SITE_HAS_NO_REMOTE_INFO %
                      (self.site_name, os.path.normpath(p)))
                site_server_ip = 'localhost'
            else:
                site_server_ip = self.site['remote_server']['remote_url']
            if site_server_ip == 'xx.xx.xx.xx':

                if self.default_values['is_local']:
                    p = '%s/sites_local/%s.py' % (
                        BASE_INFO['sitesinfo_path'], self.site_name)

                print(SITE_NOT_EDITED % (self.site_name, os.path.normpath(p)))
                selections = self.selections
                must_exit = True
                if selections:
                    for s in selections:
                        if s[0] in NO_NEED_SERVER_IP:
                            must_exit = False
                if must_exit:
                    sys.exit()
            if self.site and not REMOTE_USER_DIC.get(site_server_ip):
                selections = self.selections
                must_exit = True
                if selections:
                    for s in selections:
                        if s[0] in NO_NEED_SERVER_IP:
                            must_exit = False
                if must_exit:
                    print(SITE_UNKNOW_IP % (site_server_ip,
                                            self.site_name, self.user, site_server_ip))
                    sys.exit()
            login_info['user'] = ACT_USER
            # access to the local database
            login_info['db_password'] = self.opts.dbpw or DB_PASSWORD_LOCAL
            login_info['db_user'] = self.opts.dbuser or DB_USER
            # access to the locally running odoo
            login_info['rpc_user'] = self.opts.rpcuser
            login_info['rpc_pw'] = self.opts.rpcpw
            # access to the local docker
            # -----------------
            # remote
            # -----------------
            # remote user depends which server the site is running on
            server = self.site and REMOTE_USER_DIC.get(
                site_server_ip, {}) or {}
            login_info['remote_user'] = server.get('remote_user') or ''
            login_info['remote_user_pw'] = self.site and server.get(
                'remote_pw') or ''
            login_info['remote_db_password'] = self.opts.dbpw or DB_PASSWORD
            login_info['remote_db_user'] = self.opts.dbuser or DB_USER
            # docker
            login_info['remote_docker_db_user'] = self.opts.remotedockerdbuser
            login_info['remote_docker_db_pw'] = self.opts.remotedockerdbpw

    def running_remote(self):
        # we to replace values that should be different when running remotely
        # this should be done in a mor systematic way.when I use massmailing, a click to the send button
        remote_info = self.site.get('remote_server', {})
        remote_url = remote_info.get('remote_url')

        def get_ipv4_address():
            """
            Returns IP address(es) of current machine.
            :return:
            """
            p = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)
            ifc_resp = p.communicate()
            patt = re.compile(
                r'inet\s*\w*\S*:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
            resp = patt.findall(ifc_resp[0])
            return resp

        return remote_url in get_ipv4_address()

    def execute_script(self):
        """
        execute externally defined script
        it must have a run command

        """
        import imp
        opts = self.opts
        extra_scripts_path = BASE_INFO.get(
            'extra_scripts_path', '%s/extra_scripts/' % self.default_values.get('sites_home'))
        script = opts.executescript
        run_fun = 'run'
        odoo = self.get_odoo()
        full_path = '%s/%s' % (extra_scripts_path, script)
        if os.path.exists('%s.py' % full_path):
            full_path = '%s.py' % full_path
        if os.path.exists(full_path):
            print(full_path)
            mod_name = os.path.splitext(script)[0]
            py_mod = imp.load_source(mod_name, full_path)
            if hasattr(py_mod, run_fun):
                # do we have parameters to pass?
                params = self.opts.executescriptparameter
                pdic = {}
                if params:
                    parts = params.split(',')
                    for p in parts:
                        try:
                            n, v = p.split('=')
                            pdic[n] = v
                        except:
                            pass
                # we pass ourself to the method, so we can access all attributes
                result = getattr(py_mod, run_fun)(self=self, **pdic)

        else:
            print(EXTRA_SCRIPT_NOT_EXISTING % full_path)

    def rebuild_site(self):
        # reload a site after the sitedescription has been updated
        try:
            from reimport import reimport, modified
        except ImportError:
            print(MODULE_MISSING % 'reimport')
        s = list(self.sites.keys())
        mlist = [m for m in modified() if m in s]
        if mlist:
            print(SITE_DESCRIPTION_RELOADED %
                  (' '.join(mlist), self.opts.command_line))
            sys.exit()

    def show_config(self):
        for k, v in list(BASE_INFO.items()):
            print(bcolors.WARNING + k + bcolors.ENDC, v)

    def set_config(self):
        data = self.opts.set_config
        force = self.opts.force
        changed = False
        if data:
            data = [tuple(d.split('=')) for d in data.split(',') if d]
            try:
                for k, v in data:
                    if v and v[0] == '-':
                        if k in BASE_INFO:
                            BASE_INFO.pop(k)
                            changed = True
                    else:
                        if force:
                            BASE_INFO[k] = v
                            changed = True
                        elif k in BASE_INFO and v:
                            BASE_INFO[k] = v
                            changed = True
                        else:
                            print(bcolors.WARNING + k + bcolors.ENDC,
                                  'is unknown or empty value provided\nconsider using -F to force setting')
                # now write to the BASE_INFO_FILENAME
                if changed:
                    baseinfo = pformat(BASE_INFO)
                    open(BASE_INFO_FILENAME, 'w').write(
                        BASE_INFO_TEMPLATE % baseinfo)
                    print(bcolors.WARNING + BASE_INFO_FILENAME +
                          ' has been written' + bcolors.ENDC)
            except ValueError:
                print(bcolors.FAIL + 'could not set value %s' % d)
                print('it must be of the form key=value')
                print(bcolors.ENDC)

    @property
    def docker_postgres_port(self):
        if self.parsername == 'docker':
            return self.postgres_port
        # does it make sense to return a default at all??
        return '8069'

    @property
    def db_container_ip(self):
        if self.parsername == 'docker':
            return self.db_ip
        # does it make sense to return a default at all??
        return 'localhost'

    @property
    def projectname(self):
        return self.site.get('projectname', self.site['site_name'])

    @property
    def is_local(self):
        return self.default_values.get('is_local')

    @property
    def odoo_server_data_path(self):
        return BASE_INFO['odoo_server_data_path']
    data_path = odoo_server_data_path

    @property
    def sitesinfo_path(self):
        return BASE_INFO['sitesinfo_path']

    @property
    def site(self, site_name=''):
        if site_name:
            name = site_name
        else:
            name = self.site_name
        if name:
            return self.sites.get(name, {})

    @property
    def site_name(self):
        return self.site_names and self.site_names[0] or ''
    
    @site_name.setter
    def site_name(self, v):
        self.site_names = [v]

    @property
    def sites_home(self):
        return self.default_values.get('sites_home', BASE_PATH)

    @property
    def version(self):
        if self.site:
            return self.site.get('odoo_version', self.default_values['odoo_version'])

    @property
    def minor(self):
        """minor version of the running erp
        
        Returns:
            string -- the minor version like '.0'
        """

        if self.site:
            return self.site.get('odoo_minor', self.default_values['odoo_minor'])

    @property
    def nightly(self):
        """what directory on the nightly server to use 
        
        Returns:
            string -- 'directory name'
            example -- 'master'
        """

        if self.site:
            return self.site.get('odoo_nightly', '')

    @property
    def docker_db_user(self):
        return self.login_info.get('docker_db_user') or self.opts.db_user or DB_USER

    @property
    def db_name(self):
        return self.site.get('db_name', self.site_name)

    @property
    def db_password(self):
        if self.parsername == 'docker':
            return self.docker_db_admin_pw
        return self.login_info.get('db_password', DB_PASSWORD)

    @property
    def db_user(self):
        if self.parsername == 'docker':
            return self.docker_db_admin
        return self.login_info.get('db_user') or self.opts.db_user or DB_USER

    @property
    def db_host(self):
        if self.parsername == 'docker':
            return self.docker_db_ip
        return self.dbhost

    @property
    def user(self):
        return self.login_info.get('user', ACT_USER)

    @property
    def remote_user(self):
        return REMOTE_USER_DIC[self.site['remote_server']['remote_url']]['remote_user']

    @property
    def remote_user_pw(self):
        return REMOTE_USER_DIC[self.site['remote_server']['remote_url']].get('remote_pw', '')

    @property
    def remote_data_path(self):
        # we first check whether config/localdata.py has an remote path set.
        remote_dic = self.site.get('remote_server')
        remote_data_path = remote_dic.get(
            'remote_data_path', remote_dic.get('remote_path'))
        if remote_data_path:
            return remote_data_path
        # then we check whether config/localdata.py has an remote path set.
        remote_dic = REMOTE_USER_DIC[self.site['remote_server']['remote_url']]
        remote_data_path = remote_dic.get(
            'remote_data_path', remote_dic.get('remote_path', self.remote_sites_home))
        return remote_data_path

    @property
    def remote_user_data_path(self):
        remote_dic = REMOTE_USER_DIC[self.site['remote_server']['remote_url']]
        remote_data_path = remote_dic.get(
            'remote_data_path', remote_dic.get('remote_path', self.remote_sites_home))
        return remote_data_path

    @property
    def remote_url(self):
        return self.site['remote_server']['remote_url']
    remote_server = remote_url  # an alias

    @property
    def remote_sites_home(self):
        return self.site.get('sites_home', '/root/odoo_instances')

    # the user can start using different paths
    # - without selecting anything:
    #   the create parser will be preselected
    # - without providing a full site name
    #   a site name will be asked for. if an invalid or partial name
    #   has bee provided, it will be used as default
    # - with a set of valid options
    def _complete_selection(self, parsername, options, results_only=False, prompt=''):
        opt = self.opts
        cmpl = SimpleCompleter(parsername, options, prompt=prompt)
        _o = cmpl.input_loop()
        if _o in options:
            if results_only:
                return _o
            if isinstance(self.opts._o.__dict__[_o], bool):
                self.opts._o.__dict__[_o] = True
            elif _o in ['updateown', 'removeown']:
                l = self.install_own_modules(quiet='listownmodules')
                cmpl = SimpleCompleter(l)
                _r = cmpl.input_loop()
                if _o:
                    self.opts._o.__dict__[_o] = _r
            else:
                self.opts._o.__dict__[_o] = input('value for %s:' % _o)

    # -------------------------------------------------------------------
    # check_name
    # check if name is in any of the sites listed in list_sites
    # or needed at all
    # @opts otion namespace
    # @no_completion: flag whether a vlid name should be selected for a
    #                 selection list
    # -------------------------------------------------------------------
    def check_name(self, no_completion=False, must_match=False):
        """
        check if name is in any of the sites listed in list_sites
        or needed at all
        @opts otion namespace
        @no_completion: flag whether a vlid name should be selected for a
                        selection list
        """
        opts = self.opts
        name = self.site_name
        if name:
            if name == 'all':
                site_names = list(self.sites.keys())
            else:
                if name.endswith('/'):
                    name = name[:-1]
                site_names = [name]

            opts._o.__dict__['name'] = name
            # if not isinstance(opts, basestring):
            #     if opts.add_site:
            #         return name
            if SITES.get(name):
                self.site_names = [name]
                return name
            if opts.add_site or opts.add_site_local:
                self.site_names = [name]
                return name
        # no name
        if not name:
            name = ''  # make sure it is a string
        if no_completion:
            # probably called at startup
            if must_match:
                matches = [k for k in list(SITES.keys()) if k.startswith(name)]
                if not matches:
                    print(
                        bcolors.WARNING + ('%s does not match any site name, discarded!' % name) + bcolors.ENDC)
                    opts._o.__dict__['name'] = ''
                    return ''
                if name:
                    self.site_names = [name]
                    return name
                return ''
            else:
                self.site_names = [name]
                return name
        if not self.name_needed():
            return
        done = False
        cmpl = SimpleCompleter('', options=list(SITES.keys(
        )), default=name or opts.sitename or '', prompt='please provide valid site name:')
        while not done:
            _name = cmpl.input_loop()
            if _name is None:
                done = True
                self.site_names = []
                return ''
            if _name and (opts.add_site or opts.add_site_local):
                if SITES.get(_name):
                    print("site %s allready exists in sites.py" % _name)
                else:
                    done = True
            if _name and SITES.get(_name):
                done = True
            else:
                print(
                    '%s is not defined in sites.py. you can add it with option --add-site' % _name)
            if done:
                opts._o.__dict__['name'] = _name
                self.site_names = [_name]
                return _name

    # ----------------------------------
    # flatten_sites
    # sites can inherit settings fro other sites
    # flatten_sites resolfes this inheritance tree
    # @SITES            : the global list of sites
    def flatten_sites(self, sites=SITES):
        """
        sites can inherit settings fro other sites
        flatten_sites resolfes this inheritance tree
        @SITES            : the global list of sites
        """
        # we allow only one inheritance level
        # check this
        for k, v in list(sites.items()):
            inherits = v.get('inherit')
            vkeys = list(v.keys())
            if inherits:
                # also the inherited site must be deepcopied
                # otherwise we copy the original to our copy that is in fact nothing but a reference fo the original
                inherited = deepcopy(sites.get(inherits))
                if not inherited:
                    print('*' * 80)
                    print('warning !!! site description %s tries to inherit %s which does not exist' % (
                        k, inherits))
                elif inherited.get('inherit'):
                    print('*' * 80)
                    print('warning !!! site description %s tries to inherit %s which does also inherit from a site. this is forbidden' % (
                        k, inherits))
                    sys.exit()
                # first copy the running site to a temporary var
                # result = v # deepcopy(v)
                # now overwrite what is in the temporary var
                # result.update(inherited)
                # now copy things back but do not overwrite "inherited" values
                # update does not work as this overwrites values that are directories
                for key, val in list(inherited.items()):
                    if isinstance(val, dict):
                        # make sure the dic exists otherwise we can not add the items
                        vvkeys = list(v.get(key, {}).keys())
                        if key not in v:
                            v[key] = {}
                        for val_k, val_val in list(val.items()):
                            if isinstance(val_val, list):
                                # v is the element in the inherited site
                                # if v does not have a key we add it with an empty list
                                if val_k not in v[key]:
                                    v[key][val_k] = []
                                [v[key][val_k].append(vi)
                                    for vi in val_val if vi not in v[key][val_k] and not ('-' + vi in v[key][val_k])]
                                # clean resulting list
                                v[key][val_k] = [vi for vi in v[key]
                                                 [val_k] if not vi.startswith('-')]
                            elif isinstance(val_val, dict):
                                # v is the site into which we inherit (the parent)
                                # key is the key in the child
                                # val is the value in the child
                                # val_val
                                if val_k not in v[key]:
                                    # so we have a target dict
                                    v[key][val_k] = {}
                                # now add elements to the the target dict
                                target = v[key][val_k]
                                for val_val_k, val_val_v in list(val_val.items()):
                                    # we do an other level of hierarchy
                                    if isinstance(val_val_v, list):
                                        if val_val_k not in target:
                                            target[val_val_k] = []
                                        sub_target = target[val_val_k]
                                        for tk in val_val_v:
                                            # should it be possible to decuct keys???
                                            if tk not in sub_target:
                                                sub_target.append(tk)
                                    elif isinstance(val_val_v, dict):
                                        if val_val_k not in target:
                                            target[val_val_k] = {}
                                        sub_target = target[val_val_k]
                                        for val_val_v_k, val_val_v_v in list(val_val_v.items()):
                                            sub_target[val_val_v_k] = val_val_v_v
                                    else:
                                        if val_val_k not in target:
                                            target[val_val_k] = val_val_v
                            else:
                                if val_k not in vvkeys:
                                    v[key][val_k] = val_val
                    elif isinstance(val, list):
                        existing = v.get(key, [])
                        v[key] = existing + \
                            [vn for vn in val if vn not in existing]
                    else:
                        # ['site_name', 'servername', 'db_name']:
                        if key in vkeys:
                            continue

    # ----------------------------------
    # construct_defaults
    # construct defaultvalues for a site
    # @site_name        : name of the site
    # ----------------------------------
    def construct_defaults(self, site_name):
        """
        construct defaultvalues for a site
        @site_name        : name of the site
        """
        # construct a dictonary with default values
        # some of the values in the imported default_values are to be replaced
        # make sure we can do this more than once
        opts = self.opts
        from templates.default_values import default_values as d_v
        self.default_values = deepcopy(d_v)
        default_values = self.default_values
        default_values['sites_home'] = BASE_PATH
        # first set default values that migth get overwritten
        # local sites are defined in local_sites and are not added to the repository
        is_local = not(SITES_LOCAL.get(site_name) is None)
        default_values['is_local'] = is_local
        default_values['db_user'] = self.db_user
        # sites_home is odoo_instnces is installed
        # eg ~/odoo_instances
        # the site_name is what the user with option -n and was checked by check_name
        default_values['site_name'] = site_name
        default_values.update(BASE_INFO)
        if isinstance(site_name, str) and SITES.get(site_name):
            if opts:
                if (not opts.add_site) and (not opts.add_site_local) and (not opts.listmodules):
                    if site_name:
                        default_values.update(SITES.get(site_name))
            else:
                default_values.update(SITES.get(site_name))
        # now make sure we have a minor version number
        if not default_values.get('odoo_minor'):
            default_values['odoo_minor'] = ''
        site_base_path = os.path.normpath(os.path.expanduser(
            '%(project_path)s/%(site_name)s/' % default_values))
        # /home/robert/projects/afbsecure/afbsecure/parts/odoo
        default_values['base_path'] = site_base_path
        default_values['data_dir'] = "%s/%s" % (
            self.odoo_server_data_path, self.site_name)
        default_values['db_name'] = site_name
        default_values['outer'] = '%s/%s' % (
            BASE_INFO['project_path'], site_name)
        default_values['inner'] = '%(outer)s/%(site_name)s' % default_values
        default_values['addons_path'] = '%(base_path)s/parts/odoo/openerp/addons,%(base_path)s/parts/odoo/addons,%(data_dir)s/%(site_name)s/addons' % default_values
        # if we are using docker, the addon path is very different
        default_values['addons_path_docker'] = '/mnt/extra-addons,/usr/lib/python2.7/dist-packages/openerp/addons'
        default_values['skeleton'] = '%s/skeleton' % self.sites_home
        # add modules that must be installed using pip
        _s = {}
        if is_local:
            _s = SITES_LOCAL.get(site_name)
        else:
            if SITES.get(site_name):
                _s = SITES.get(site_name)
        site_addons = _s.get('addons', [])
        pip_modules = _s.get('extra_libs', {}).get('pip', [])
        skip_list = _s.get('skip', {}).get('addons', [])
        # every add on module can have its own pip module that must be used
        for addon in _s.get('addons', []):
            pip_modules += addon.get('pip_list', [])
        pm = '\n'
        if pip_modules:
            pip_modules = list(set(pip_modules)) # make them uniqu
            for m in pip_modules:
                pm += '%s\n' % m
        default_values['pip_modules'] = pm
        # the site addons will only contain paths to download
        # if from one of the downloaded addon folders more than one addon should be installed ??????
        default_values['site_addons'] = _construct_sa(
            site_name, deepcopy(site_addons), skip_list)

        default_values['skip_list'] = skip_list

        # make sure that all placeholders are replaced
        m = re.compile(r'.*%\(.+\)s')
        for k, v in list(self.default_values.items()):
            if isinstance(v, str):
                counter = 0
                while m.match(v) and counter < 10:
                    v = v % self.default_values
                    self.default_values[k] = v
                    counter += 1  # avoid endless loop
        self.default_values['odoo_version'] = self.opts.odoo_version

    # -------------------------------------------------------------------
    # name_needed
    # check if name neede
    # or needed at all
    # @opts otion namespace
    # @optin : option to check
    #          if not provided check what option user has selected
    # -------------------------------------------------------------------
    def name_needed(self, option=None):
        """
        check if name needed
        or needed at all
        @opts otion namespace
        @optin : option to check
                 if not provided check what option user has selected
        """
        opts = self.opts
        if opts.name == 'db' and opts.docker_show:
            return False
        if not option:
            # only return False if all options need no name
            result = False
            options = self.selections
            for option in options:
                if self.name_needed(option[0]):
                    result = True
            return result

        # do we need a name
        # if an option is provide, check this one
        no_need_name = NO_NEED_NAME
        need_name = NEED_NAME
        if option:
            if option in no_need_name:
                return
            if option in need_name:
                return True
        # no decision could be made so far, check the options
        nn = [n for n in need_name if opts._o.__dict__.get(n)]
        nnn = [n for n in no_need_name if opts._o.__dict__.get(n)]
        if not nn:
            # nothing found that needs a name so far
            if nnn:
                # we faoun an option set that does not require name
                return
        # bah, what should we do ..
        # lets assume, we do need a name ..
        return True

    # ----------------------------------
    # delete_site_local 
    # remove all local project files
    # but leave the site description as it is
    # ----------------------------------
    def delete_site_local(self):
        """
        remove all local project files
        """
        site_name = self.site_name
        if not site_name:
            print(bcolors.FAIL)
            print('no name provided')
            print(bcolors.ENDC)
            return
        cur_path = os.getcwd()
        # remove project data
        project_path = self.default_values['project_path']
        os.chdir(project_path)
        # ----------------------------------------
        rpath ='%s/%s' % (project_path, site_name)
        if os.path.exists(rpath):
            print(bcolors.WARNING)
            print('removing %s' % rpath)
            shutil.rmtree(rpath, True)
        addons_path = self.data_path
        # ----------------------------------------
        os.chdir(addons_path)
        if os.path.exists(site_name):
            print('removing %s' % site_name)
            shutil.rmtree(site_name)
        # ----------------------------------------
        print('dropping database %s' % site_name)
        db_updater = DBUpdater()
        try:
            db_updater.close_db_connections_and_delete_db(site_name)
        except:
            pass # already deleted?
        print('removing virtualenv %s' % site_name)
        self.remove_virtual_env(site_name)
        print(bcolors.OKGREEN)
        print('tuti palletti')
        print(bcolors.ENDC)
        os.chdir(cur_path)

    def copy_admin_pw(self):
        """
        copy admin password from one site to the other
        """
        opts = self.opts
        site_name = self.site_name
        source = opts.copy_admin_pw

        # first check whether the source is valid
        if source not in self.sites:
            print(bcolors.FAIL + '*' * 80)
            print('%s is not a valid source' % source)
            print('*' * 80 + bcolors.ENDC)
            return
        # create two connections
        target_cursor, t_connection = self.get_cursor(return_connection=True)
        source_cursor, s_connection = self.get_cursor(
            db_name=source, return_connection=True)
        s_sql = "SELECT password_crypt from res_users where login = 'admin'"
        t_sql = "UPDATE res_users set password_crypt = '%s'  where login = 'admin'"
        source_cursor.execute(s_sql)
        pw = source_cursor.fetchone()[0]
        target_cursor.execute(t_sql % pw)
        t_connection.commit()
        t_connection.close()
        s_connection.close()
        print(bcolors.OKGREEN + '*' * 80)
        print('copied admin pw from %s to %s' % (source, site_name))
        print('*' * 80 + bcolors.ENDC)

    def set_admin_pw(self):
        """
        set admin password for a site
        """
        site_name = self.site_name
        pw = self.db_password
        # create a connection
        target_cursor, t_connection = self.get_cursor(return_connection=True)
        t_sql = "UPDATE res_users set password = '%s'  where login = 'admin'"
        target_cursor.execute(t_sql % pw)
        t_connection.commit()
        t_connection.close()
        print(bcolors.OKGREEN + '*' * 80)
        print('set admin pw for %s to %s' % (site_name, pw))
        print('*' * 80 + bcolors.ENDC)

    def create_folders(self, path_name='', quiet=None):
        """
        create all folders needed
        path_name = path to parent folder. create if it does not exist
        """
        errors = False
        if quiet is None:
            quiet = not self.opts.verbose
        if not path_name:
            path_name = self.site_name
        p = os.path.normpath('%s/%s' % (self.data_path, path_name))
        foldernames = self.default_values['foldernames']
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
        elif not os.path.isdir(self.data_path):
            print(bcolors.FAIL + '%s exists but is not a folder. Plese eiter remove it, or set'
                  'new folder using option -set odoo_server_data_path:/NEWPATH' + bcolors.ENDC)
        for pn in [''] + foldernames:
            try:
                pp = '%s/%s' % (p, pn)
                os.mkdir(pp)
            except:
                errors = True
                if not quiet:
                    print(bcolors.FAIL + 'could not create %s' %
                          pp + bcolors.ENDC)
        if not quiet:
            if errors:
                print(bcolors.WARNING +
                      'not all directories could be created' + bcolors.ENDC)
            else:
                print('directories for %s created' % check_name(self.opts))
        
        # now add folder content
        # handle_file_copy_move(self, source, target, filedata):
        skeleton_path = self.default_values['skeleton']
        from skeleton.files_to_copy import FILES_TO_COPY_FOLDER as files_to_copy
        for foldername in foldernames:
            file_path = '%s/%s' % (p, foldername)
            if files_to_copy.get(foldername):
                self.handle_file_copy_move(
                    '%s/%s' % (skeleton_path, foldername), file_path, files_to_copy[foldername])

    # ----------------------------------
    # update_install_serversetting
    # set the web.base.url and the google captcha keys
    def update_install_serversetting(self):
        site = self.site
        site_params = site.get('site_settings', {})

        odoo = self.get_odoo()
        if odoo:
            # -----------------------------------
            # config
            # -----------------------------------

            # get the config blocks
            # we start with setting the site
            # proto = site_params.get('proto', 'http://')
            configs = site_params.get('configs', {})

            # -----------------------------------
            # languages
            # -----------------------------------
            # 'languages' : ['de_CH', 'fr_CH', 'en_US'],
            lang_dic = {}
            languages = configs.pop('languages', [])
            if languages:
                lang_dic = self.install_languages(languages)

            # next we set the key web.base.url.freeze
            # this prevenst that the key is reset when login in as addmin
            if 'ir.config_parameter' in configs:
                # old structure like afbs
                for key, data in list(configs.items()):
                    try:
                        model = odoo.env[key]
                        records = data.get('records', [])
                        for s_info, values in records:
                            # [('key', 'support_branding.company_name'),  {'value'  : 'redO2oo GmbH'}],
                            s = model.search([(s_info[0], '=', s_info[1])])
                            if s:
                                model.browse(s).write(values)
                    except:
                        pass
            else:
                """
                'configs' : {
                    # the following sample values assume, that the module support branding is installed
                    'support_branding' : {
                        'model' : 'ir.config_parameter',
                        # list of (search-key, value), {'field' : vaue, 'filed' : value ..}
                        'records' : [
                            # list of (search-key, value), {'field' : vaue, 'filed' : value ..}
                            [('key', 'support_branding.company_name'),  {'value'  : 'redO2oo KLG'}],
                            ....
                         ]
                    },


                    website:
                    --------
                    {u'cdn_activated': False,
                    u'cdn_filters': u'^/[^/]+/static/\n^/web/(css|js)/\n^/web/image\n^/web/content\n^/website/image/',
                    u'cdn_url': False,
                    u'default_lang_id': 22,
                    u'favicon': '',
                    u'google_analytics_key': False,
                    'google_maps_api_key': False,
                    u'language_ids': [[6, False, [1, 22]]],
                    'module_website_form_editor': 0,
                    'module_website_version': 0,
                    u'social_facebook': False,
                    u'social_github': False,
                    u'social_googleplus': False,
                    u'social_linkedin': False,
                    u'social_twitter': False,
                    u'social_youtube': False,
                    u'website_id': 1,
                    u'website_name': u'My Website'}

                },
                """
                def repl_default_lang_code(data):
                    if isinstance(data, dict):
                        code = data.pop('default_lang_code', None)
                        if code:
                            data['default_lang_id'] = self.install_languages([code])[
                                code]
                for setting, values in list(configs.items()):
                    m = values['model']
                    model = odoo.env[m]
                    records = values['records']
                    for s_info, values in records:
                        # [('key', 'support_branding.company_name'),  {'value'  : 'redO2oo GmbH'}],
                        s = model.search([(s_info[0], '=', s_info[1])])
                        if s:
                            repl_default_lang_code(values)
                            model.browse(s).write(values)

            # -----------------------------------
            # companies
            # -----------------------------------
            """
            # data to be set on the remote server with
            # --set-site-data
            companies: {
                'main_company' : {
                    'company_data' : {
                        # use any number of fields you want to set on the main company
                        # this is normaly done after after all modules are installed
                        # so you can also use fields like firstname/lastname that are
                        # only available after the addons have been installed
                        'name' : 'Energy & Power Sarl',
                        'street' : 'Rue Marconi 19',
                        'zip'    : '1920',
                        'city'   : 'Martigny VS',
                        'phone'  : '+41 (0) 78 678 39 42',
                        'email' : 'info@eplusp.ch',
                        'url' : 'https://www.eplusp.ch',
                    },
                    'users' : {
                        # add users you want to be created
                        # for each user provide either an string with the email,
                        # or a dictionary with more data. In any case, the email must
                        # be provided
                        # the same rules as for the company apply
                        'bruno.cosandey@eplusp.ch' : {
                            'firstname' : 'Bruno',
                            'lastname' : 'Cosandey',
                            'street' : 'Rue Marconi 19',
                            'zip'    : '1920',
                            'city'   : 'Martigny VS',
                            'phone'  : '+41 (0) 78 678 39 42',
                            'email' : 'bruno.cosandey@eplusp.ch',
                        }
                    },
                },  # main_company
            },  # companies

            """
            companies = site_params.get('companies', {})
            main_company = companies.get('main_company')
            if main_company:
                # the main company always has id 1
                companies_o = odoo.env['res.company']
                mc = companies_o.browse([1])
                # do we have data for the main company
                mc_data = main_company.get('company_data')
                if mc_data:
                    mc.write(mc_data)
                # create related users
                users = main_company.get('users')
                if users:
                    users_o = odoo.env['res.users']
                    for login, user_data in list(users.items()):
                        firstname = user_data.get('firstname')
                        lastname = user_data.get('lastname')
                        language = user_data.get('name')
                        if language:
                            self.install_languages([language])
                        if firstname or lastname:
                            user_data['name'] = ('%s %s' %
                                                 (lastname, firstname)).strip()
                        else:
                            user_data['name'] = login
                        if not user_data.get('email'):
                            user_data['email'] = login
                        if not user_data.get('login'):
                            user_data['login'] = login
                        if not user_data.get('tz'):
                            user_data['tz'] = 'Europe/Zurich'
                        # check if user exists
                        user = users_o.search([('login', '=', login)])
                        if user:
                            users_o.browse(user).write(user_data)
                        else:
                            #user = odoo.env['res.users'].sudo().with_context().create(user_data)
                            users_o.create(user_data)
        else:
            print(ODOO_NOT_RUNNING % self.site_name, {})

    # ----------------------------------
    # set_local_data
    # set local settings from the site description
    # use remote_settings is active when we change a dokerized odoo
    def set_local_data(self, use_remote_setting=False):
        odoo = self.get_odoo()
        if not odoo:
            print(bcolors.FAIL, ODOO_NOT_RUNNING %
                  self.site_name, bcolors.ENDC)
            return
        # run set server data
        # this sets
        self.update_install_serversetting()
        site = self.site
        site_settings = site.get('site_settings', {})
        local_settings = site_settings.get('local_settings', {})
        if use_remote_setting:
            proto = site_settings.get('proto', 'https://')
            base_url = '%s%s' % (proto, site.get('apache', {}).get(
                'vservername', local_settings.get('base_url', '')))
        else:
            base_url = local_settings.get('base_url', '')
        admin_mail = local_settings.get('admin_mail', '')
        if admin_mail.find('%(local_user_mail)s') > -1:
            admin_mail = BASE_INFO.get('local_user_mail', 'robert@redO2oo.ch')
        # if admin_mail:
            #users = odoo.env['res.users']
            #u = users.search([('id', '=', 1)])
            #admin = users.browse(u)
            #admin.write({'email' : admin_mail})
            #print(bcolors.OKGREEN, 'setting admin email to:%s' % admin_mail, bcolors.ENDC)

        # do we have to install / uninstall anything
        addons = local_settings.get('addons', {})
        to_install = addons.get('install', [])
        # there are modules, like mailblocker, we want to have installed only locally
        if to_install:
            self.install_own_modules(info_dic={'local_install': to_install})
        # set the site configuration, that allways needs to be set
        # set the base url
        if odoo:
            config = odoo.env['ir.config_parameter']
        if base_url:
            base_url_obj = config.browse(
                config.search([('key', '=', 'web.base.url')]))
            base_url_obj.write({'value': base_url})
            print(bcolors.OKGREEN, 'setting base_url to:%s' %
                  base_url, bcolors.ENDC)
        # set other config stuff
        # if there is additional site configuration, set them now
        more_params = local_settings.get('site_settings')
        if more_params:
            config_params = more_params.get('configs', {}).get(
                'ir.config_parameter', {}).get('records', [])
            if self.running_remote():
                # we to replace values that should be different when running remotely
                # this should be done in a mor systematic way.when I use massmailing, a click to the send button
                remote_info = self.site.get('remote_server', {})
                if remote_info.get('redirect_emil_to'):
                    self.default_values['local_user_mail'] = remote_info.get(
                        'redirect_emil_to')
            for c_param in config_params:
                # list of (search-key-name, value), {'field' : value, 'field' : value ..}
                # [('key', 'red_override_email_recipients.override_to'),
                    # {'value'  : '%(local_user_mail)s'}],
                c_key = c_param[0][0]
                c_k_val = c_param[0][1]
                vals = c_param[1]
                c_obj = config.browse(config.search([(c_key, '=', c_k_val)]))
                if c_obj:
                    for k, v in list(vals.items()):
                        if isinstance(v, str):
                            vals[k] = v % self.default_values
                    c_obj.write(vals)
                print(bcolors.OKGREEN, 'setting %s to:%s' %
                      (c_k_val, vals), bcolors.ENDC)

    # ----------------------------------
    # set_odoo_settings
    # set odoo settings from the site description
    # like the email settings and such
    # we try to find out what our ip is and the get the data
    # according to that ip.
    # if our ip is not in the servers list, we take 127.0.0.1
    def set_odoo_settings(self, use_docker=False, local=True):
        import socket
        import fcntl
        import struct
        SITES_PW = {}

        def get_ip_address(ifname):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                return socket.inet_ntoa(fcntl.ioctl(
                    s.fileno(),
                    0x8915,  # SIOCGIFADDR
                    struct.pack('256s', ifname[:15])
                )[20:24])
            except:
                # we have no etho
                # https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ipl = s.getsockname()
                if ipl:
                    return ipl[0]
        odoo = self.get_odoo()
        if not odoo:
            print(ODOO_NOT_RUNNING % self.site_name)
            return
        site = self.site
        remote_servers = site.get('remote_servers', {})
        # if the site runs on a virtual server behind a NAT we do
        # not know its real address
        if self.opts.use_ip:
            my_ip = self.opts.use_ip
        elif self.opts.use_ip_docker:
            my_ip = self.opts.use_ip_docker
        elif local:
            my_ip = '127.0.0.1'
        else:
            my_ip = get_ip_address('eth0')
        # check whether the address in in
        s_data = remote_servers.get(my_ip)
        # use proxy on development server
        proxy = ''
        if not s_data:
            s_data = remote_servers.get(remote_servers.get('proxy'))
            proxy = remote_servers.get('proxy')
            print(bcolors.FAIL + 'no odoo_settings for (local) id:%s found' %
                  my_ip + bcolors.ENDC)
            print(bcolors.WARNING + 'using proxy (%s) to calculate site settings' %
                  my_ip + bcolors.ENDC)
        if not s_data:
            print(bcolors.WARNING + 'no odoo_settings for id:%s found' %
                  my_ip + bcolors.ENDC)
            return
        # get passwords
        try:
            from sites_pw import SITES_PW
            email_pws = SITES_PW.get(self.site_name, {}).get(
                'email', SITES_PW.get(self.site_name, {}).get('email_settings', {}))
        except ImportError:
            email_pws = {}
            pass

        # write the incomming email server
        i_server = odoo.env['fetchmail.server']
        # get the first server
        print(bcolors.OKGREEN, '*' * 80)
        print('incomming email')
        i_ids = i_server.search([])
        i_id = 0
        i_data = s_data.get('odoo_settings', {}).get('mail_incomming')
        # do we have a password
        if not local:
            i_data['password'] = email_pws.get('email_pw_incomming', '')
        if i_ids:
            i_id = i_ids[0]
        if i_id:
            incomming = i_server.browse([i_id])
            incomming.write(i_data)
        else:
            incomming = i_server.create(i_data)
        print(i_data)
        print('-' * 80)
        print('outgoing email')
        # now do the same for the outgoing server
        o_data = s_data.get('odoo_settings', {}).get('mail_outgoing')
        if not local:
            o_data['smtp_pass'] = email_pws.get('email_pw_outgoing', '')
        o_server = odoo.env['ir.mail_server']
        # get the first server
        o_ids = o_server.search([])
        o_id = 0
        if o_ids:
            o_id = o_ids[0]
        if o_id:
            outgoing = o_server.browse([o_id])
            outgoing.write(o_data)
        else:
            o_server.create(o_data)
        print(o_data)
        print('*' * 80, bcolors.ENDC)

    # ----------------------------------
    # run_tests
    # run tests listed on the command line
    # run all, if list of tests is "all"
    def run_tests(self):
        """
        tests are run, when we start odoo with the --test-enable parameter
        We therfore start odoo
        bin/start_openerp --test-enable -u redmail2bill --stop-after-init --test-file /home/robert/odoo_projects_data/redo2oo/addons/redmail2bill/tests/test_redmail2bill_generate.py
        """
        pass

    # ----------------------------------
    # install_own_modules
    # own modules are listed in sites.py under the key addons
    def install_own_modules(self, list_only=False, quiet=False, info_dic={}):
        """
        own modules are listed in the site description under the key addons
        """
        opts = self.opts
        default_values = self.default_values
        if list_only:
            from templates.install_blocks import INSTALL_BLOCKS
            print('\nthe following installable odoo module blocks exist:')
            print('---------------------------------------------------')
            for k in list(INSTALL_BLOCKS.keys()):
                print('    ', k)
            print('---------------------------------------------------')
            return

        site = self.site
        # addons decalared in addons are the ones not available from odoo directly
        site_addons = site.get('addons')
        # addons declared in the odoo_addons stanza are the ones we can get from odoo
        odoo_addons = site.get('odoo_addons')
        local_install = info_dic.get('local_install', [])
        req = []
        module_obj = None
        if not opts.installodoomodules and not opts.dinstallodoomodules:
            # opts.installown or opts.updateown or opts.removeown or opts.listownmodules or quiet: # what else ??
            # collect the names of the modules declared in the addons stanza
            # idealy their names are set, if not, try to find them out
            for a in (site_addons or []):
                names = find_addon_names(a)
                for name in names:
                    if local_install and name not in local_install:
                        continue
                    if name:
                        if opts.listownmodules:
                            req.append((name, a.get('url')))
                        else:
                            req.append(name)
                    else:
                        if a and not quiet:
                            print('could not detect name for %s' %
                                  a.get('url', ''))

        # if we only want the list to install, no need to be wordy
        if opts.dlistownmodules or opts.listownmodules or quiet == 'listownmodules':
            if quiet:
                return req
            sn = self.site_name
            print('\nthe following modules will be installed for %s:' % sn)
            print('---------------------------------------------------')
            for n, url in req:
                temp_target = os.path.normpath(
                    '%s/%s/%s/%s_addons/%s' % (BASE_INFO['project_path'], sn, sn, sn, n))
                if os.path.exists(temp_target):
                    print(bcolors.OKBLUE, '    %s %s (devel mode)' %
                          (n, temp_target), bcolors.ENDC)
                else:
                    print('    ', n, url)
            print('---------------------------------------------------')
            return

        # do we want to intall odoo modules
        if opts.dinstallodoomodules or opts.installodoomodules:
            from templates.install_blocks import INSTALL_BLOCKS
            odoo_apps_info, odoo_modules_info = self.get_odoo_modules()

            odoo_apps = list(odoo_apps_info.keys())
            odoo_apps_names = list(odoo_apps_info.values())
            odoo_apps_map = {}
            for k, v in list(odoo_apps_info.items()):
                odoo_apps_map[v] = k

            odoo_modules = list(odoo_modules_info.keys())
            odoo_module_names = list(odoo_modules_info.values())
            odoo_module_map = {}
            for k, v in list(odoo_modules_info.items()):
                odoo_module_map[v] = k
            for o in (odoo_addons or []):
                o = str(o)
                if (o not in odoo_apps) and (o not in odoo_apps_names) \
                   and (o not in odoo_modules) and (o not in odoo_module_names):
                    print('!' * 80)
                    print('%s is not a known install block' % o)
                    print(
                        'check in templates/install_blocks.py what blocks are available')
                    print('-' * 80)
                    # sys.exit()
                if o in odoo_apps_names:
                    name = odoo_module_map[o]
                    if name not in req:
                        req.append(name)
                elif o in odoo_apps:
                    if o not in req:
                        req.append(o)
                elif o in odoo_module_names:
                    name = odoo_module_map[o]
                    if name not in req:
                        req.append(name)
                elif o in odoo_modules:
                    if o not in req:
                        req.append(o)
                else:
                    # we will never come here ???
                    if o not in req:
                        req.append(o)

        if req:
            installed = []
            uninstalled = []
            to_upgrade = []

            module_obj = self.get_module_obj()
            if not module_obj:
                # should not happen, means we have no contact to odoo
                return
            # refresh the list of updatable modules within odoo
            module_obj.update_list()

            cursor = self.get_cursor()
            skiplist = self.site.get('skip', {}).get('addons', [])[
                :]  # we do not want to change the original
            skip_upd_list = self.site.get('skip', {}).get('updates', [])
            skip2 = opts.skipown or []
            if skip2:
                skip2 = skip2.split(',')
            # remove elements in the local_install from the skip lists
            skiplist = [e for e in skiplist if e not in local_install]
            skip2 = [e for e in skip2 if e not in local_install]

            for a in (skiplist) + skip2:
                if a in req:
                    req.pop(req.index(a))
            self.collect_info(cursor, req, installed,
                              uninstalled, to_upgrade, skiplist, req[:])
            if req:
                print('*' * 80)
                print('the following modules where not found:', req)
                print('you probably have to download them')
                print('*' * 80)
            if uninstalled:
                print('the following modules need to be installed:',
                      [u[1] for u in uninstalled])
                i_list = [il[0] for il in uninstalled]
                n_list = [il[1] for il in uninstalled]
                print('*' * 80)
                print(bcolors.OKGREEN + 'installing: ' +
                      bcolors.ENDC + ','.join(n_list))
                load_demo = False
                modules = module_obj.browse(i_list)
                if load_demo:
                    for m in modules:
                        m.demo = True
                if opts.single_step:
                    for module in modules:
                        print('installing: %s' % module.name)
                        module.button_immediate_install()
                else:
                    modules.button_immediate_install()
                print(bcolors.OKGREEN + 'finished installing: ' +
                      bcolors.ENDC + ','.join(n_list))
                print('*' * 80)
            if installed and (opts.updateown or opts.removeown, opts.dupdateown or opts.dremoveown):
                if opts.updateown or opts.dupdateown:
                    i_list = [il[0]
                              for il in installed if (il[1] not in skip_upd_list)]
                    n_list = [il[1]
                              for il in installed if (il[1] not in skip_upd_list)]
                    print('*' * 80)
                    print(bcolors.OKGREEN + 'upgrading: ' +
                          bcolors.ENDC + ','.join(n_list))
                    print('-' * 80)
                    modules = module_obj.browse(i_list)
                    load_demo = False
                    if load_demo:
                        for m in modules:
                            m.demo = True
                    if opts.single_step:
                        for module in modules:
                            # todo do not install every single feature that are in the same module
                            # but do it module wise
                            print('upgrading: %s' % module.name)
                            module.button_immediate_upgrade()
                    else:
                        modules.button_immediate_upgrade()
                    print(bcolors.OKGREEN + 'finished upgrading: ' +
                          bcolors.ENDC + ','.join(n_list))
                    print('*' * 80)
                else:  # uninstall ..
                    print('the following modules will be uninstalled:',
                          [u[1] for u in installed])
                    for i, n in installed:
                        print('*' * 80)
                        print('unistalling: ' + n)
                        module_obj.browse(i).button_immediate_uninstall()
                        print('finished unistalling: ' + n)
                        print('*' * 80)

    # ----------------------------------
    #  collects info on what modules are installed
    # or need to be installed
    # @req : list of required modules. If this is an empty list
    #         use any module
    # @uninstalled  : collect unistalled modules into this list
    # @to_upgrade   :collect modules that expect upgrade into this list
    def collect_info(self, cursor, req, installed, uninstalled, to_upgrade, skip_list, all_list=[]):
        opts = self.opts
        s = 'select * from ir_module_module'
        cursor.execute(s)
        rows = cursor.fetchall()
        all = not req
        updlist = []
        if opts.updateown:
            updlist = opts.updateown.split(',')
        elif opts.removeown:
            updlist = opts.removeown.split(',')
        if opts.dupdateown:
            updlist = opts.dupdateown.split(',')
        elif opts.dremoveown:
            updlist = opts.dremoveown.split(',')
        if 'all' in updlist:
            updlist = all_list
        if 'dev' in updlist or 'develop' in updlist:
            dev_list = self.site.get('develop')
            if dev_list:
                dev_list = dev_list.get('addons')
            if not dev_list:
                print(OWN_ADDONS_NO_DEVELOP % self.site_name)
                return
            updlist = dev_list
        for r in rows:
            n = r.get('name')
            s = r.get('state')
            i = r.get('id')
            if n in req or all:
                if n in req:
                    req.pop(req.index(n))
                if s == 'installed':
                    if all or updlist == 'all' or n in updlist:
                        installed.append((i, n))
                    continue
                elif s in ['uninstalled', 'to install']:
                    uninstalled.append((i, n))
                elif s == 'to upgrade':
                    to_upgrade.append(n)
                else:
                    print(n, s, id)
        # now clean all list from any modules we want to skip
        # x.pop(x.index(2))
        if skip_list:
            if uninstalled:
                for n in skip_list:
                    for u in uninstalled:
                        if u[1] == n:
                            uninstalled.pop(uninstalled.index(u))
            if to_upgrade:
                for n in skip_list:
                    try:
                        to_upgrade.pop(to_upgrade.index(n))
                    except:  # was not there ..
                        pass

    # =============================================================
    # handle docker stuff
    # =============================================================
    # ef run_commands(self, cmd_lines, shell=True, pw ='', user=''):
        # ""
        # andle docker stuff
        # ""
        # rom localdata import DB_USER, DB_PASSWORD
        # f not pw:
            # w   = self.db_password # B_PASSWORD
        # f not user:
            # ser = self.db_user # B_USER
        # ounter = 0
        # or cmd_line in cmd_lines:
            # ounter +=1
            # f self.opts.verbose:
                # rint 'counter:', counter
            # f not cmd_line:
                # ontinue
            # rint '-' * 80
            # rint cmd_line
            #  = subprocess.Popen(
                # md_line,
                # tdout=PIPE,
                # nv=dict(os.environ, PGPASSWORD=pw,  PATH='/usr/bin'),
                # hell=shell)
            # f self.opts.verbose:
                # rint p.communicate()
            # lse:
                # .communicate()

    def run_commands(self, cmd_lines, user='', pw='', shell=True):
        """
        """
        opts = self.opts
        if not pw:
            pw = self.db_password  # B_PASSWORD
        if not user:
            user = self.db_user  # B_USER
        counter = 0
        is_builtin = False
        for cmd_line in cmd_lines:
            counter += 1
            if isinstance(cmd_line, dict):
                is_builtin = cmd_line['is_builtin']
                cmd_line = cmd_line['cmd_line']
            if opts.verbose:
                print('counter:', counter)
            if not cmd_line:
                continue
            if opts.verbose:
                print('-' * 80)
                print(cmd_line)
            if is_builtin:
                p = subprocess.Popen(
                    cmd_line,
                    stdout=PIPE)
            else:
                p = subprocess.Popen(
                    cmd_line,
                    stdout=PIPE,
                    env=dict(os.environ, PGPASSWORD=pw, PATH='/usr/bin:/bin'),
                    shell=shell)
            if opts.verbose:
                print(p.communicate())
            else:
                p.communicate()

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
        default_values = self.default_values
        pp = BASE_INFO['odoo_server_data_path']
        oop = BASE_PATH
        marker_start = AMARKER % 'start'
        marker_end = AMARKER % 'end'
        # where do we want to add our aliases?
        alias_script = "bash_aliases"
        if sys.platform == 'darwin':
            alias_script = "bash_profile"
        else:
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
            'aliasmarker_start': marker_start,
            'aliasmarker_end': marker_end,
            'alias_list': self.create_aliases(),
            'alias_header': ALIAS_HEADER % {'pp': pp},
            'ppath': pp,
        }
        open(alias_path, 'w').write(alias_str)

    def create_aliases(self):
        """
        """
        opts = self.opts
        default_values = self.default_values
        pp = BASE_INFO['project_path']
        dp = self.data_path
        oop = BASE_PATH
        # shortnamesconstruct
        alias_names = [n for n in list(SITES.keys()) if len(n) <= ALIAS_LENGTH]
        names = list(SITES.keys())
        names.sort()
        long_names = alias_names
        for n in names:
            if n in alias_names:
                continue  # the  short ones
            try_length = ALIAS_LENGTH
            while n[:try_length] in alias_names:
                try_length += 1
                # we will for sure find a key ..
            alias_names.append(n[:try_length])
            long_names.append(n)
        result = ALIAS_LINE % {'sname': 'pro', 'path': pp}
        result += ALIAS_LINE % {'sname': 'ooin', 'path': oop}
        for i in range(len(alias_names)):
            if os.path.exists('%s/%s' % (pp, long_names[i])):
                result += ALIAS % {
                    'sname': alias_names[i],
                    'lname': long_names[i],
                    'ppath': pp,
                    'dpath': dp,
                }
        # ooin cd to odoo_instances
        result += OOIN % BASE_PATH
        result += OOLI % BASE_INFO['sitesinfo_path']
        result += OODA % BASE_INFO['odoo_server_data_path']
        result += DOCKER_CLEAN
        result += DOC_ET_ALL % {'user_home': os.path.expanduser("~/")}
        result += ALIASC
        result += ALIASOO
        result += VIRTENV_D

        return result

    def do_updates(self):
        """
        we want to git pull odoo_instances and sites_list
        """
        # first we change to odoo_instances main folder
        adir = os.getcwd()
        for t in self.sites_home, self.sitesinfo_path:
            os.chdir(t)
            # pull odoo_instances
            cmd_line = ['git', 'pull']
            p = subprocess.Popen(cmd_line, stdout=PIPE, stderr=PIPE)
            if self.opts.verbose:
                print(t, ':',)
                result = p.communicate()
                print(result[0])
                if result[1]:
                    print(result[1])
            else:
                p.communicate()
        os.chdir(adir)

    def do_rebuild(self):
        # we want to call bin/dosetup.py -f;bin/buildout in the buildout directory
        adir = os.getcwd()
        pp = BASE_INFO['project_path']
        f = '%s/%s/%s' % (pp, self.site_name, self.site_name)
        if os.path.exists(f):
            os.chdir(f)
            cmd_lines = (['bin/dosetup.py', '-f'], ['bin/buildout'])
            for cmd_line in cmd_lines:
                print(bcolors.WARNING)
                print('processing:', f, cmd_line)
                print(bcolors.ENDC)
                p = subprocess.Popen(cmd_line, stdout=PIPE, stderr=PIPE)
                result = p.communicate()
                print(result[0])
                if result[1]:
                    print(result[1])

    def handle_file_copy_move(self, source, target, filedata):
        opts = self.opts
        # if overwrite is set, existing files are overwritten
        # if make_links is set links to dosetup.py and update_localdb.py are created, otherwise the files are copied
        try:
            overwrite = opts.overwrite
            make_links = not opts.update_nolinks
        except AttributeError as e:
            overwrite = True
            make_links = False
        o_overwrite = overwrite
        for fname, tp in list(filedata.items()):
            # O = File, always overwrite
            # F = File
            # X = File set executable bit, allways overwrite
            # L = Linkpath)

            # D = Folder
            # T = Touch
            # R = copy and rename
            # U = Update, these files can have updatable content in the form of %(XXX)s
            # '$FILE$' link to the source
            overwrite = o_overwrite
            try:
                cmd = ''
                spath = fname
                if source:
                    spath = '%s/%s' % (source, fname)
                tpath = '%s/%s' % (target, fname)
                if isinstance(tp, tuple):
                    tp, cmd = tp
                    if cmd:
                        if cmd == '$FILE$':
                            if make_links:
                                if os.path.exists(tpath):
                                    os.remove(tpath)
                                os.symlink(spath, tpath)
                                continue
                            else:
                                # copy like normal file
                                # allways overwrite
                                if os.path.exists(tpath):
                                    os.remove(tpath)
                                shutil.copyfile(spath, tpath)
                    if tp == 'L':
                        # does the target exist and do we want to overwrite it?
                        if os.path.exists(tpath) and not os.path.islink(tpath) and make_links:
                            # we want to make links, but target is not a link
                            # so we remove it
                            os.remove(tpath)
                        elif os.path.exists(tpath) and overwrite:
                            # target exist, but we want to renew it
                            os.remove(tpath)
                        # cmd is the link
                        # change to the target
                        if not os.path.exists(tpath):
                            # link was not copied yet or has been remove due to the overwrite flag
                            adir = os.getcwd()
                            os.chdir(target)
                            try:
                                os.symlink(cmd, tpath)
                            except OSError as e:
                                print('*' * 80)
                                print(str(e))
                                print('cmd:', cmd)
                                print('tpath:', tpath)
                                print('*' * 80)
                            os.chdir(adir)
                    if tp == 'R':
                        # copy and rename
                        # cmd is the name of the new file
                        tpath = '%s/%s' % (target, cmd)
                        # only overwrite if overwrite is set
                        if overwrite and os.path.exists(tpath):
                            os.remove(tpath)
                        if overwrite or (not os.path.exists(tpath)):
                            shutil.copyfile(spath, tpath)
                    if tp == 'U':
                        # update the content of the file by replacing variables
                        if os.path.exists(tpath):
                            os.remove(tpath)
                        if overwrite or (not os.path.exists(tpath)):
                            open(tpath, 'w').write(
                                open(spath, 'r').read() % self.default_values)
                        if cmd == 'X':
                            # set executable
                            st = os.stat(tpath)
                            os.chmod(tpath, st.st_mode | stat.S_IEXEC)
                elif isinstance(tp, dict):
                    # new directory
                    newsource = '%s/%s' % (source, fname)
                    newtarget = '%s/%s' % (target, fname)
                    if not os.path.exists(newtarget):
                        os.mkdir(newtarget)
                    self.handle_file_copy_move(newsource, newtarget, tp)
                else:
                    # this is just a simple command ..
                    if tp in ['F', 'O', 'U']:
                        if tp in ('O', 'U'):
                            overwrite = True
                        # a normal file
                        # only overwrite if overwrite is set
                        if overwrite and os.path.exists(tpath):
                            os.remove(tpath)
                        if overwrite or (not os.path.exists(tpath)):
                            if tp == 'O':
                                try:
                                    # make sure all placeholders are replaced
                                    data = open(spath, 'r').read(
                                    ) % self.default_values
                                    open(tpath, 'w').write(data)
                                except TypeError:
                                    shutil.copyfile(spath, tpath)
                            elif tp == 'U':
                                open(tpath, 'w').write(
                                    open(spath, 'r').read() % self.default_values)
                            else:
                                shutil.copyfile(spath, tpath)
                    elif tp == 'X':
                        # a normal file, but set execution flag
                        # only overwrite if overwrite is set
                        overwrite = True  # X always overwrites
                        if overwrite and os.path.exists(tpath):
                            os.remove(tpath)
                        if overwrite or (not os.path.exists(tpath)):
                            shutil.copyfile(spath, tpath)
                        # set executable
                        st = os.stat(tpath)
                        os.chmod(tpath, st.st_mode | stat.S_IEXEC)
                    elif tp == 'L':
                        if overwrite and os.path.exists(tpath):
                            os.remove(tpath)
                        # a link
                        if not os.path.exists(tpath):
                            shutil.copyfile(spath, tpath)
                    elif tp == 'D':
                        # a folder to create
                        # f overwrite and os.path.exists(tpath):
                            # hutil.rmtree(tpath, True)
                        if not os.path.exists(tpath):
                            os.mkdir(tpath)
                    elif tp == 'T':
                        # just touch to create
                        open(tpath, 'a').close()
            except IOError as e:
                print(str(e))
            except Exception as e:
                if self.opts.verbose:
                    print(str(e))


class SiteCreator(InitHandler, DBUpdater):

    def __init__(self, opts, sites=SITES):
        super(SiteCreator, self).__init__(opts, sites)

    # ------------------------------------
    # get_value_from_config
    # gets a value from etc/open_erp.conf
    # ------------------------------------
    def get_value_from_config(self, path, key=''):
        """
        gets a value from etc/open_erp.conf
        """
        res = {}
        for l in open(path):
            if l and l.find('=') > -1:
                parts = l.split('=', 1)
                res[parts[0].strip()] = parts[1].strip()
        if key:
            return res.get(key)
        else:
            return res

    # =============================================================
    # create site stuff
    # =============================================================
    def create_or_update_site(self):
        # read and update the data from which login_info.cfg.in will be created
        config_info = self.get_config_info()
        # check if the project in the project folder defined in the configuration exists
        # if not create the project structure and copy all files from the skeleton folder
        existed = self.check_project_exists()
        # construct list of addons read from site
        open(LOGIN_INFO_FILE_TEMPLATE % self.default_values['inner'], 'w').write(
            config_info % self.default_values)
        # overwrite requrements.txt with values from systes.py
        data = open(REQUIREMENTS_FILE_TEMPLATE %
                    self.default_values['inner'], 'r').read()
        # we want to preserve changes in the requirements.txt
        data = '\n'.join(list(dict(enumerate([d for d in data.split('\n') if d] +
                                        self.default_values['pip_modules'].split('\n'))).values()))
        # MODULES_TO_ADD_LOCALLY are allways added to a local installation
        # these are tools to help testing and such
        s = data.split('\n') + (MODULES_TO_ADD_LOCALLY and MODULES_TO_ADD_LOCALLY or [])
        s = Set(s)
        open(REQUIREMENTS_FILE_TEMPLATE % self.default_values['inner'], 'w').write(
            '\n'.join(s))  # 25.7.17 robert % self.default_values)
        return existed

    def remove_virtual_env(self, site_name):
        """remove an existing virtual env
         
         Arguments:
             site_name {string} -- the name of the virtual env to remove
        """
        cmd = ['/bin/bash', '-c', 'echo $(which virtualenvwrapper.sh)']
        p = subprocess.Popen(cmd, stdout=PIPE)
        virtualenvwrapper = p.communicate()[0].strip()
        commands = """
        export WORKON_HOME=%(home)s/.virtualenvs
        export PROJECT_HOME=/home/robert/Devel
        source %(virtualenvwrapper)s
        rmvirtualenv  %(site_name)s       
        """ % {
            'home': os.path.expanduser("~"),
            'virtualenvwrapper': virtualenvwrapper,
            'site_name': site_name
        }
        p = subprocess.Popen(
            '/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate(commands)

    def create_virtual_env(self, target, python_version='python2.7', use_workon=True):
        """
        """
        "create a virtual env within the new project"
        adir = os.getcwd()
        os.chdir(target)
        # here we have to decide whether we run flectra or odoo
        server_type = self.site.get('server_type', 'odoo')
        if 1:  # server_type == 'flectra' or use_workon:
            # need to find virtualenvwrapper.sh
            cmd = ['/bin/bash', '-c', 'echo $(which virtualenvwrapper.sh)']
            p = subprocess.Popen(cmd, stdout=PIPE)
            virtualenvwrapper = p.communicate()[0].strip()
            commands = """
            export WORKON_HOME=%(home)s/.virtualenvs
            export PROJECT_HOME=/home/robert/Devel
            source %(virtualenvwrapper)s
            mkvirtualenv -a %(inner)s -p %(python_version)s %(site_name)s       
            """ % {
                'home': os.path.expanduser("~"),
                'virtualenvwrapper': virtualenvwrapper,
                'inner': self.default_values['inner'],
                'python_version': python_version,
                'site_name': self.site_name
            }
            p = subprocess.Popen(
                '/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            out, err = p.communicate(commands)
            print(out)
            print(err)
        else:
            # create virtual env
            cmd_line = ['virtualenv', '-p', python_version, 'python']
            p = subprocess.Popen(cmd_line, stdout=PIPE, stderr=PIPE)
            if self.opts.verbose:
                print(os.getcwd())
                print(cmd_line)
                print(p.communicate())
            else:
                p.communicate()
        os.chdir(adir)

    def get_config_info(self):
        """
        collect values needed to put into the openerp.cfg file
        """
        default_values = self.default_values
        default_values['projectname'] = self.projectname
        # only set when creating or editing the site
        default_values['odoo_version'] = self.site['odoo_version']
        # read the login_info.py.in
        # in this file, all variables are of the form $(VARIABLENAME)$
        # replace_dic is constructed in get_user_info_base->build_replace_info
        # the names to replace are defined globaly as REPLACE_NAMES
        p2 = LOGIN_INFO_TEMPLATE_FILE % default_values['skeleton']
        return open(p2, 'r').read() % default_values

    def check_project_exists(self):
        """
        check if a project exists, if not create it
        """
        opts = self.opts
        default_values = self.default_values
        existed = True
        # check if project exists
        skeleton_path = default_values['skeleton']
        outer_path = default_values['outer']
        inner_path = default_values['inner']
        if not os.path.exists(inner_path):
            self.create_new_project()
            existed = False
        self.do_copy(skeleton_path, outer_path, inner_path)
        # make sure virtual env exist
        python_version = 'python2.7'
        st = self.site.get('server_type', 'odoo')
        if st == 'odoo':
            if float(self.version) > 10:
                python_version = 'python3'
        elif st == 'flectra':
            python_version = 'python3'
        self.create_virtual_env(inner_path, python_version=python_version)
        return existed

    def create_new_project(self):
        """ create a new project with all the substructures
            These are:
            - a project structure in procects
            - a folder with a predefined set of folders in
              the data directory
            - a virtual environment (done by the calling method)
        """

        opts = self.opts
        default_values = self.default_values
        "ask for project info, create the structure and copy the files"
        skeleton = default_values['skeleton']
        outer = default_values['outer']
        inner = default_values['inner']
        # create project folders
        # create sensible error message
        # check whether projects folder exists
        pp = default_values['project_path']
        if not os.path.exists(pp) and not os.path.isdir(pp):
            # try to create it
            try:
                os.makedirs(pp)
            except OSError:
                print('*' * 80)
                print('could not create %s' % pp)
                sys.exit()
        for p in [outer, inner]:
            if not os.path.exists(p):
                os.mkdir(p)
        ppath_ini = '%s/__init__.py' % outer
        if not os.path.exists(ppath_ini):
            open(ppath_ini, 'w').close()
        # reate virtualenv
        # copy files
        # reate_virtual_env(inner)

    def do_copy(self, source, outer_target, inner_target):
        opts = self.opts
        # now copy files
        from skeleton.files_to_copy import FILES_TO_COPY, FILES_TO_COPY_FLECTRA, FILES_TO_COPY_ODOO
        if self.site.get('server_type', 'odoo') == 'flectra':
            FILES_TO_COPY.update(FILES_TO_COPY_FLECTRA)
        elif 1:  # self.version != '9.0':
            FILES_TO_COPY.update(FILES_TO_COPY_ODOO)
        from pprint import pprint
        # pprint(FILES_TO_COPY)
        # odules_update = False # only copy some files so we can rerun dosetup
        self.handle_file_copy_move(
            source, inner_target, FILES_TO_COPY['project'])
        # create directories and readme in the project home
        if outer_target:
            self.handle_file_copy_move(
                '', outer_target, FILES_TO_COPY['project_home'])
            # now create a versions file
            from templates.versions import VERSIONS, VERSIONS_FLECTRA
            if self.site.get('server_type', 'odoo') == 'flectra':
                open('%s/versions.cfg' % outer_target,
                     'w').write(VERSIONS_FLECTRA[self.version])
            else:
                open('%s/versions.cfg' % outer_target,
                     'w').write(VERSIONS[self.version])
