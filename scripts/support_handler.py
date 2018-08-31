#!bin/python
# -*- encoding: utf-8 -*-
import os
import re
from config import SITES, BASE_INFO, MARKER, ODOO_VERSIONS, MIGRATE_FOLDER, sites_handler
from scripts.sites_handler import UpdateError
from scripts.create_handler import InitHandler, bcolors
from scripts.messages import *
import subprocess
import shlex
import stat
#from utilities import collect_options, _construct_sa
#from scripts.messages import *

# ----------------------------------
# diff_modules
BLOCK_TEMPLATE = """
    'XXX' : [
%s
    ],
"""

class SupportHandler(InitHandler):
    # _preset_handler will be imported and instantiated on demand
    _preset_handler = None

    def __init__(self, opts, sites=SITES):
        self.need_login_info = True
        super(SupportHandler, self).__init__(opts, sites)

    @property
    def preset_handler(self):
        """import, initiate a preset_handler
        return: preset_handler instance
        """
        if not self._preset_handler:
            import scripts.preset_handler

    @property
    def editor(self):
        # firs check whether an editor is defined in BASE_INFO
        editor = BASE_INFO.get('editor')
        if not editor:
            editor = os.environ.get('EDITOR')
            if not editor:
                #editor = '/usr/bin/atom'
                editor = '/bin/nano'
        return editor

    # ----------------------------------
    # drop_site 
    # remove site from list of site descriptions
    # ----------------------------------
    def drop_site(self):
        """
        remove site description from sites.py
        @opts             : option instance
        @default_values   : dictionary with default values
        """
        result = sites_handler.drop_site(self.site_name)
        if result:
            print "removed site %s from sites.py" % self.site_name

    # ----------------------------------
    # add_site_to_sitelist
    # add new site description to sites.py
    # @default_values   : dictionary with default values
    # ----------------------------------
    def add_site_to_sitelist(self):
        """
        add new site description to sites.py
        @opts             : option instance
        @default_values   : dictionary with default values
        """
        from config import sites_handler
        opts = self.opts
        self.default_values['marker'] = MARKER
        # check if user wants to copy an existing site
        name = self.opts.name
        template = ''
        if ':' in name:
            name, template = name.split(':')
            self.site_name = name
            self.opts.name = name
        site_name = self.site_name

        # if the site allready exist, we bail out
        if self.sites.get(self.site_name):
            print "site %s allready defined" % self.site_name
            return

        # make sure the variables for the the docker port and remote site are set
        docker_port = 9000 # just arbitrary
        docker_long_poll_port = 19000
        if opts.docker_port:
            try:
                docker_port = int(opts.docker_port)
                docker_long_poll_port = docker_port + 10000
            except Exception, e:
                print(bcolors.FAIL)
                print('*' * 80)
                print('%s is not a valid port number' % opts.docker_port)
                print(bcolors.ENDC)
                return
        else:
            docker_port = self.default_values.get('docker_port', docker_port)
            docker_long_poll_port = self.default_values.get('docker_long_poll_port', docker_long_poll_port)
        self.default_values['docker_port'] = docker_port
        self.default_values['docker_long_poll_port'] = docker_long_poll_port

        if opts.remote_server:
            self.default_values['remote_server'] = opts.remote_server
        else:
            self.default_values['remote_server'] = self.default_values.get('remote_server', '127.0.0.1')
   
        if opts.add_site:
            # before we can construct a site description we need a a file with site values
            pvals = {} # dict to get link to the preset-vals-file
            # preset_values = self.get_preset_values(pvals)
            if 1: #preset_values:
                result = sites_handler.add_site_global(handler = self, template_name=template)#, preset_values=preset_values)
                if result:
                    print "%s added to sites.py" % self.site_name
            else:
                if pvals.get('pvals_path'):
                    print(bcolors.WARNING)
                    print('*' * 80)
                    print('a file with values for the new site was created')
                    print(pvals.get('pvals_path'))
                    print('please edit and adapt it. It will be incorporated in the site description')
                    print('and will be used to set the site values')
                    print('*' * 80)
                    print(bcolors.ENDC)
            # no preset stuff yet
            return
            # before we can construct a site description we need a file with site values
            if opts.use_preset:
                pvals = {}  # dict to get link to the preset-vals-file
                preset_values = self.get_preset_values.get_preset_values(pvals)
                if preset_values:
                    result = sites_handler.add_site_global(
                        handler=self,
                        template_name=template,
                        preset_values=preset_values)
                else:
                    if pvals.get('pvals_path'):
                        print(bcolors.WARNING)
                        print('*' * 80)
                        print('a file with values for the new site was created')
                        print(pvals.get('pvals_path'))
                        print(
                            'please edit and adapt it. It will be incorporated in the site description')
                        print('and will be used to set the site values')
                        print('*' * 80)
                        print(bcolors.ENDC)
                    else:
                        print(bcolors.FAIL)
                        print('*' * 80)
                        print('could not read or generate a file with default values')
                        print('*' * 80)
                        print(bcolors.ENDC)
                    return
            else:
                result = sites_handler.add_site_global(
                    handler=self,
                    template_name=template)
                    #preset_values=preset_values)
            if result:
                print "%s added to sites.py" % self.site_name

        elif opts.add_site_local:
            # we add to sites local
            # we read untill we find an empty }
            # before we can construct a site description we need a a file with site values
            if opts.use_preset:
                pvals = {}  # dict to get link to the preset-vals-file
                preset_values = self.preset_handler.get_preset_values(pvals, is_local=True)
                result = sites_handler.add_site_local(
                    handler=self, template_name=template, preset_values=preset_values)
            else:
                result = sites_handler.add_site_local(
                    handler=self, template_name=template) #, preset_values=preset_values)
            if result:
                print "%s added to sites.py (local)" % self.site_name
    # ----------------------------------
    # add_server_to_localdata
    # add new server info to localdat
    # ----------------------------------
    def add_server_to_localdata(self):
        """
        add new site description to sites.py
        @opts             : option instance
        @default_values   : dictionary with default values
        """
        opts = self.opts
        server_info = opts.add_server.strip().split('@')
        if not len(server_info) == 2:
            print SITE_CREATED_SERVER_BAD_IP % opts.add_server
            return
        if server_info[0] == 'root':
            remote_data_path = '/root/odoo_instances'
        else:
            remote_data_path = '/home/%s/odoo_instances' % server_info[0]
        self.default_values['remote_user'] = server_info[0]
        self.default_values['use_ip'] = server_info[1]
        self.default_values['remote_data_path'] = remote_data_path
        self.default_values['marker'] = '\n' + MARKER

        template = open('%s/templates/newserver.py' %
                        self.sites_home, 'r').read() % self.default_values
        print template
        # now open sites.py as text and replace the marker with the templae which allready has a new marker
        m = re.compile(r'\n%s' % MARKER)
        localdata = open('%s/config/localdata.py' % self.sites_home).read()
        if not m.search(localdata):
            print LOCALSITESLIST_MARKER_MISSING
            return
        open('%s/config/localdata.py' % self.sites_home,
             'w').write(m.sub(template, localdata))

        print SITE_CREATED_SERVER % (server_info[1], server_info[0])

    def diff_installed_modules(self, req, mod_path, rewrite, list_only=False):
        """
        """
        opts = self.opts
        cursor = self.get_cursor()
        if not cursor:
            return
        installed = []
        uninstalled = []
        to_upgrade = []
        self.collect_info(cursor, req, installed, uninstalled, to_upgrade, [])
        bt = ''
        btl = '\n        %s,'
        if list_only:
            for t in installed:
                print t
        elif rewrite:
            f = open(mod_path, 'w')
            for t in installed:
                f.write('%s\n' % str(t))
            f.close()
        else:
            try:
                data = open(mod_path, 'r').read().split('\n')
            except IOError:
                print []
                return
            for t in installed:
                if not str(t) in data:
                    bt += btl % str(t)
            if bt:
                print 'please add the following block to templates/install_blocks.py'
                print BLOCK_TEMPLATE % bt

    def pull_sites(self):
        """
        pul site descriptions from their repository
        """
        try:
            sites_handler.pull(auto=False)
            print VCS_OK % ('sites_global', BASE_INFO['sitesinfo_url'])
        except UpdateError as e:
            print VCS_ERROR % target
            print bcolors.WARNING
            print str(e)
            print bcolors.ENDC
            print VCS_ERROR_END

    def edit_site_or_server(self):
        # first we get the editor
        editor = self.editor
        if self.opts.edit_server:
            # we are editing config/localdata.py
            fname = '%s/config/localdata.py' % self.sites_home
        elif self.opts.edit_site:
            site_name = self.site_name
            if self.site.get('is_local'):
                fname = '%s/sites_local/%s.py' % (
                    BASE_INFO['sitesinfo_path'], site_name)
            else:
                fname = '%s/sites_global/%s.py' % (
                    BASE_INFO['sitesinfo_path'], site_name)
        command = editor + " " + fname
        status = os.system(command)

    # list_ports
    # ----------
    # list ports used for remote sites
    # grouped by server
    def list_ports(self):
        """return list of all ports used in remote servers
        """
        n_map = {
            '176.9.142.21'  : 'alice2',
            '144.76.184.20' : 'frieda',
            '195.48.80.84'  : 'kinesys',
            '88.198.51.174' : 'lisa',
            '46.4.89.241'   : 'salome',
            '178.63.103.72' : 'susanne',
            'xx.xx.xx.xx' : 'xx.xx.xx.xx',
            'localhost' : 'localhost',
        }
        result = {}
        data = self.sites.items()
        data.sort()
        for sname, site in data:
            try:
                port = site['docker']['odoo_port']
                url = n_map.get(site['remote_server']['remote_url'], 'unknown-url')
                result[url] = result.get(url, []) + [(port, sname)]
            except:
                print 'no docker:', sname
        servers = n_map.values()
        servers.sort()
        for url in servers:
            print('server: %s, number of sites: %s' % (url, len(result.get(url, []))))
            result_lines = result.get(url, [])
            if result_lines:
                result_lines.sort()
                for rl in result_lines:
                    print('    %s %s' % (rl[0], rl[1]))


    # upgrade
    # ----------
    # upgrade site to new odoo version
    # using openupgrade
    def upgrade(self, target_site):
        site = self.site
        #check whether target_site exists
        if not self.sites.get(target_site):
            print bcolors.FAIL
            print '*' * 80
            print '%s is not a valid site' % target_site
            print bcolors.ENDC
            return
        target_outer = '%s/%s' % (BASE_INFO['project_path'], target_site)
        target_inner = '%s/%s' % (target_outer, target_site)
        if not os.path.exists(target_inner):
            print bcolors.FAIL
            print '*' * 80
            print '%s does not exist' % target_inner
            print 'please create it by executing bin/c -c %s' % target_site
            print bcolors.ENDC
            return
            
        # for the time beeing we only do on step upgrade
        # construct the command line like:
        # -C /home/robert/projects/breitschtraeff10/breitschtraeff10/etc/odoo.cfg -D breitschtraeff10 -B migrations -R "11.0" 
        config_path = '%s/etc/odoo.cfg' % self.default_values['inner']
        target_version = self.sites[target_site]['odoo_version']
        if not os.path.exists(config_path):
            print bcolors.FAIL
            print '*' * 80
            print 'the base project does not yet exist please create it'
            print bcolors.ENDC
            return
        result_code, result_line = self.run_upgrade('bin/python %s/migrate.py -C %s -D %s -N %s -B %s -R "%s"' % (
            MIGRATE_FOLDER,
            config_path, 
            self.site_name, 
            target_site,
            MIGRATE_FOLDER, 
            target_version)
        )
        # now a copy of the database has been created we can migrate migrate with openmigrate
        # this will be done in the target sites project environment
        # so we have to write out a script that can do this
        from templates.update_script import UPDATE_SCRIPT_TEMPLATE
        target_data = {
            'upgrade_folder' : MIGRATE_FOLDER,
            'upgrade_line' : result_line,
        }
        update_script = UPDATE_SCRIPT_TEMPLATE % target_data
        # write it out
        out_path = '%s/do_migrate.sh' % target_inner
        open(out_path, 'w').write(update_script)
        # set executable
        st = os.stat(out_path)
        os.chmod(out_path, st.st_mode | stat.S_IEXEC)

        # finaly we have to copy the filestore from the old to the new site
        lfst_path = '%s/%s/filestore/%s' % (
            BASE_INFO['odoo_server_data_path'], self.site_name, self.site_name)
        rfst_path = '%s/%s/filestore/%s' % (
            BASE_INFO['odoo_server_data_path'], target_site, target_site)
        cmdline = 'rsync -av %s/ %s/ --delete' % (lfst_path, rfst_path)
        self.run_upgrade(cmdline)
        print bcolors.OKGREEN
        print '*' * 80
        print 'halleluja, the first step is done'
        print 'now go to the target environment by executing %sw' % target_site
        print 'there you find a script called do_migrate.sh'
        print 'which you should execute'
        print bcolors.ENDC
        
        return
    
    def run_upgrade(self, command):
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                last_line = output.strip()
                print last_line
        rc = process.poll()
        return (rc, last_line)

