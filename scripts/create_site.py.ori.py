#!bin/python
# -*- encoding: utf-8 -*-

import sys
import os
# from name_completer import SimpleCompleter
sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
from scripts.bcolors import bcolors
try:
    from ruamel.std.argparse import ArgumentParser, set_default_subparser
    import argparse
except ImportError:
    print('*' * 80)
    print(bcolors.WARNING + bcolors.FAIL + 'please run bin/pip install -r install/requirements.txt' + bcolors.ENDC)
    print('could not install ruamel.std.argparse')
    print('*' * 80)
    sys.exit()

# make sure at least the bae config is accessible
from config import NEED_BASEINFO, BASE_INFO_FILENAME, BASE_DEFAULTS
if NEED_BASEINFO:
    from scripts.utilities import update_base_info
    update_base_info(BASE_INFO_FILENAME, BASE_DEFAULTS)
    sys.exit()
try:
    from config import SITES, SITES_LOCAL
except ImportError:
    from config import sites_handler
    sites_handler.check_and_create_sites_repo()
    from config import SITES, SITES_LOCAL

from config import ACT_USER, BASE_PATH, NEED_BASEINFO, FOLDERNAMES, \
    BASE_INFO_FILENAME, BASE_DEFAULTS, BASE_INFO, MARKER, \
    APACHE_PATH, DB_USER, DB_PASSWORD, LOGIN_INFO_FILE_TEMPLATE, REQUIREMENTS_FILE_TEMPLATE, DOCKER_DEFAULTS

from scripts.utilities import list_sites, \
    update_base_info, \
    module_add,  \
    checkout_sa, \
    create_server_config, collect_options, \
    check_links

from config.handlers import SiteCreator
from config.handlers import DockerHandler
from config.handlers import SupportHandler
from config.handlers import RemoteHandler
from config.handlers import MailHandler
# scripts.vcs handles git stuff
import scripts.vcs
from scripts.messages import *
from .update_local_db import DBUpdater


"""
to do:
------
- ODOO_SERVER_DATA config variable
  dumper.py should make use of this variable.
  have an alias for each remote server in local_data.py
  that allows to test things locally

- re-moddel sites in sites.py to have a mails structure
  add a version number to sites.py
- make an update script that applies changes to sites.py according to its
  actual version
- create an option that configures the mail servers on the target server

- install own needs either a string with comma separated options or all
- get_remote_server_info in update_local_db should be remove an
  remote_ser_info taken from site_defaul_data

- systematizize uses of site_defaul_data
- systematizize uses of username and password

- add port to config datarm

- option to only update changed modules (like -c but without creating the site)
- change dosetup to be an option of create, make dosetup.py in the projects
  folders bin to be able
  to collect its data from erp_workbench/sites.py ..

refresh:
- there should be an option -M that runs bin/dosetup.py -f and recreates
  etc/openerp.cfg
- why do we need login.cfg.in anymore?
  it is a leftover from svn ..
 alias:
- alias produces wrong aliasses for root. should not be in /home/root
- change alias to be only in scripts, and not in all of the projects
- alias has to read all relevant info from config and default_values
- alias should also point to ODOO_SERVER_DATA
- unalias a site
transfer:
- admin password needs to be transferred
- local_copy gets target in filestore wrong
- get list of logins/passwords to update

docker:
- when db container does not exist create it automatically
- check for dbdumper remotely and locally

datadir:
- alias
- createfolder
- create addonpaths
- create_sa
"""


"""
in default_values we have something like this:
not all values are allways set!

{'add_path': ',/mnt/extra-addons/crm_oca,/mnt/extra-addons/partner-contact,
  /mnt/extra-addons/cms-dms,/mnt/extra-addons/therp-addons,/mnt/extra-addons/oca_website',
 'addlinks': None,
 'addons': [{'add_path': 'crm_oca',
             'branch': '9.0',
             'group': 'crm_oca',
             'name': 'mass_mailing_partner',
             'subdir': 'mass_mailing_partner',
             'type': 'git',
             'url': 'https://github.com/robertrottermann/crm.git'},
            {'group': 'mapper',
             'type': 'git',
             'url': 'ssh://git@gitlab.redcor.ch:10022/afbs/afbs_import_mapper.git'},
            {'add_path': 'partner-contact',
             'branch': '9.0',
             'group': 'partner-contact',
             'name': 'partner_firstname',
             'subdir': 'partner_firstname',
             'type': 'git',
             'url': 'https://github.com/OCA/partner-contact.git'},
            {'branch': '9.0',
             'group': 'afbs_extra_data',
             'type': 'git',
             'url': 'ssh://git@gitlab.redcor.ch:10022/afbs/afbs_extra_data.git'},
            {'branch': '9.0',
             'group': 'afbs_membership',
             'type': 'git',
             'url': 'ssh://git@gitlab.redcor.ch:10022/afbs/afbs_membership.git'},
            {'add_path': 'cms-dms',
             'group': 'cms-dms',
             'names': ['document v9', 'website_dms'],
             'type': 'git',
             'url': 'ssh://git@gitlab.redcor.ch:10022/yaseenshareef91/cms-dms.git'},
            {'branch': '9.0',
             'group': 'afbs_workgroups',
             'type': 'git',
             'url': 'ssh://git@gitlab.redcor.ch:10022/afbs/afbs_workgroups.git'},
            {'add_path': 'therp-addons',
             'branch': '8.0',
             'group': 'therp-addons',
             'name': 'override_mail_recipients',
             'type': 'git',
             'url': 'https://github.com/robertrottermann/Therp-Addons.git'},
            {'group': 'mail_thread_fetchall',
             'type': 'git',
             'url': 'ssh://git@gitlab.redcor.ch:10022/open-source/mail_thread_fetchall.git'},
            {'branch': '9.0',
             'group': 'afbs_dashboard',
             'type': 'git',
             'url': 'ssh://git@gitlab.redcor.ch:10022/afbs/afbs_dashboard.git'},
            {'branch': '9.0',
             'group': 'afbs_website',
             'name': 'afbs_website',
             'type': 'git',
             'url': 'ssh://git@gitlab.redcor.ch:10022/afbs/afbs_website.git'},
            {'add_path': 'oca_website',
             'branch': '9.0',
             'group': 'oca_website',
             'name': 'website_event_register_free',
             'type': 'git',
             'url': 'https://github.com/robertrottermann/website.git'}],
 'addons_path': '/home/robert/projects/afbsdemo/parts/odoo/openerp/addons,
    /home/robert/projects/afbsdemo/parts/odoo/addons,/home/robert/odoo_projects_data/afbsdemo/addons',
 'addons_path_docker': '/mnt/extra-addons,/usr/lib/python2.7/dist-packages/openerp/addons',
 'admin_passwd': 'admin',
 'apache': {'vserveraliases': ['afbs.ch', 'afbs.redcor.ch'],
            'vservername': 'demo.afbs.ch'},
 'base_path': '/home/robert/projects/afbsdemo',
 'create_database': True,
 'csv_internal_sep': ',',
 'current_user': 'robert',
 'data_dir': '/home/robert/odoo_projects_data',
 'db_host': 'localhost',
 'db_maxconn': '64',
 'db_name': 'afbsdemo',
 'db_password': 'admin',
 'db_port': False,
 'db_template': 'template1',
 'db_user': 'robert',
 'dbfilter': 'afbsdemo',
 'debug_mode': False,
 'demo': False,
 'dev_mode': True,
 'docker': {'container_name': 'afbsdemo',
            'odoo_image_version': 'odoo:9.0',
            'odoo_port': '8073'},
 'docker_path_map': ('/home/robert/', '/root/'),
 'docker_postgres_port': '55432',
 'email_from': False,
 'email_pw_incomming': '',
 'email_pw_outgoing': '',
 'email_user_incomming': 'mailhandler@afbs.ch',
 'email_user_outgoing': 'mailhandler@afbs.ch',
 'foldernames': ['addons', 'dump', 'etc', 'filestore', 'log'],
 'geoip_database': '/usr/share/GeoIP/GeoLiteCity.dat',
 'import_partial': '',
 'inherit': 'afbs',
 'inner': '/home/robert/projects/afbsdemo/afbsdemo',
 'is_local': False,
 'limit_memory_hard': '2684354560',
 'limit_memory_soft': '2147483648',
 'limit_request': '8192',
 'limit_time_cpu': '60',
 'limit_time_real': '120',
 'list_db': True,
 'log_db': 'afbsdemo',
 'log_db_level': 'warning',
 'log_handler': ':INFO',
 'log_level': 'info',
 'logfile': 'None',
 'logrotate': True,
 'longpolling_port': '8072',
 'max_cron_threads': '2',
 'netrpc': False,
 'odoo_addons': ['crm',
                 'invoicing',
                 'online events',
                 'calendar',
                 'discuss',
                 'projects',
                 'accounting and finance ',
                 'inventory management',
                 'issue tracking',
                 'purchase management',
                 'website builder',
                 'survey',
                 'mass mailing campaigns',
                 'blogs'],
 'odoo_admin_pw': 'AfbsDemo$77',
 'odoo_server_data_path': '/home/robert/odoo_projects_data',
 'odoo_version': '9.0',
 'osv_memory_age_limit': '1.0',
 'osv_memory_count_limit': False,
 'outer': '/home/robert/projects/afbsdemo',
 'parts_dir_name': 'parts',
 'pg_password': 'odoo',
 'pg_path': 'None',
 'pidfile': 'None',
 'pip': [],
 'pip_modules':,
 'project_path': '/home/robert/projects',
 'projectname': 'afbsdemo',
 'proxy_mode': False,
 'remote_server': {'remote_data_path': '/root/odoo_instances',
                   'remote_url': '82.220.39.73',
                   'remote_user': 'root'},
 'reportgz': False,
 'server_wide_modules': 'None',
 'servername': 'afbsdemo',
 'site_addons': '    local /home/robert/odoo_projects_data/afbsdemo/addons/crm_oca
 local /home/robert/odoo_projects_data/afbsdemo/addons
 local /home/robert/odoo_projects_data/afbsdemo/addons/partner-contact
 local /home/robert/odoo_projects_data/afbsdemo/addons/cms-dms
 local /home/robert/odoo_projects_data/afbsdemo/addons/therp-addons
 local /home/robert/odoo_projects_data/afbsdemo/addons/oca_website',
 'site_name': 'afbsdemo',
 'sites_home': '/home/robert/odoo_instances',
 'sitesinfo_path': '/home/robert/odoo_instances/sites_list/',
 'sitesinfo_url': 'ssh://git@gitlab.redcor.ch:10022/redcor_customers/sites_list.git',
 'skeleton': '/home/robert/odoo_instances/skeleton',
 'skip': {'addons': ['website_dms']},
 'skip_list': ['website_dms'],
 'slave_info': {'master_domain': 'localhost', 'master_site': 'afbschweiz'},
 'smtp_password': False,
 'smtp_port': '25',
 'smtp_server': 'mail.redcor.ch',
 'smtp_ssl': False,
 'smtp_user': False,
 'syslog': False,
 'test_commit': False,
 'test_enable': False,
 'test_file': False,
 'test_report_directory': False,
 'unaccent': False,
 'username': 'robert',
 'without_demo': True,
 'xmlrpc': True,
 'xmlrpc_interface': '',
 'xmlrpc_port': '8069',
 'xmlrpcs': False}
"""

class OptsWrapper(object):
    """
    """
    def __init__(self, d):
        """
        """
        self.__d = d
    def __getattr__(self, key):
        """
        """
        return hasattr(self.__d, key) and getattr(self.__d, key)
    @property
    def _o(self):
        """
        """
        return(self.__d)


def main(opts):
    """
    """
    # reset
    # -----
    # when we start the first time or want to reset the stored config
    # these values are writen to $SITES_HOME/config/base_info.py
    # - project path: the path to the folder, where the projects are added to
    # - docker_path_map : mapping applied to the paths assigned to the
    #   docker volumes names when you run docker as a non root user.
    #   This helps to keep the same file structure on the remote and local
    #   server.
    # - serer data path: where server data is stored in a folder structure
    #   for each server
    if NEED_BASEINFO or opts.reset:
        update_base_info(BASE_INFO_FILENAME, BASE_DEFAULTS)
        return

    # check if needed links are set
    check_links() # does nothing

    # check if name is given and valid
    parsername, selected, options = collect_options(opts)
    if parsername == 'create':
        handler = SiteCreator(opts, SITES)
    elif parsername == 'support':
        handler = SupportHandler(opts, SITES)
    elif parsername == 'remote':
        handler = RemoteHandler(opts, SITES)
    elif parsername == 'docker':
        handler = DockerHandler(opts, SITES)
    elif parsername == 'mail':
        handler = MailHandler(opts, SITES)
    else:
        print(bcolors.FAIL + 'hoppalla, no handler' + bcolors.ENDC)
        sys.exit()
    opts = handler.opts

    # should never happen ..
    if not BASE_INFO:
        print("you should provide base info by using the -r option")
        return

    # --------------------------------------------------------
    # ckeck ip combination makes sense
    # --------------------------------------------------------
    if opts.new_target_site and not opts.use_ip_target:
        opts.use_ip_target = 'localhost'

    if opts.new_target_site and not (opts.dump_local or opts.dataupdate or opts.dataupdate_close_connections):
        print(bcolors.WARNING)
        print('*' * 80)
        print('the option -NTS only works in conjunction with the main command dump')
        print('like: bin/c -dump afbschweiz -NTS afbstest')
        print('*' * 80)
        print(bcolors.ENDC)
        return

    # --------------------------------------------------------
    # simple options from which we return after completion
    # therefore only one of them can be sensibly selected
    # --------------------------------------------------------


    # if we have an option that needs a name ..
    if handler.name_needed() and not handler.site_name:
        print('done..')
        did_run_a_command = True
        return

    # copy_admin_pw
    # -----------
    # copy password from one site to the other
    if opts.copy_admin_pw  or opts.docker_copy_admin_pw:
        handler.copy_admin_pw()
        did_run_a_command = True
        return

    # set_admin_pw
    # -----------
    # copy password from one site to the other
    if opts.set_admin_pw or opts.docker_set_admin_pw:
        handler.set_admin_pw()
        did_run_a_command = True
        return

    # show config
    # -----------
    # list_sites lists all existing sites both from global and local sites
    # if we have an option that needs a name ..
    if opts.show:
        handler.show_config()
        did_run_a_command = True
        return

    # set config
    # -----------
    # list_sites lists all existing sites both from global and local sites
    # if we have an option that nees a name ..
    if opts.set_config:
        handler.set_config()
        did_run_a_command = True
        return

    # list_sites
    # ----------
    # list_sites lists all existing sites both from global and local sites
    if opts.list_sites:
        list_sites(SITES)
        did_run_a_command = True
        return

    # list_ports
    # ----------
    # list ports used for remote sites
    # grouped by server
    if opts.list_ports:
        handler.list_ports()
        did_run_a_command = True
        return

    # upgrade
    # ----------
    # copy and upgrade site to new version
    if opts.upgrade:
        handler.upgrade(opts.upgrade)
        did_run_a_command = True
        return

    # showmodulediff and showmodulediff_refresh
    # -----------------------------------------
    # showmodulediff and showmodulediff_refresh are auxiliary otions that are
    # only needed to create the install block
    if opts.showmodulediff or opts.showmodulediff_refresh:
        p = os.path.normpath('%s/.installed' % handler.default_values['sites_home'])
        rewrite = False
        if opts.showmodulediff_refresh:
            rewrite = True
        handler.diff_installed_modules([], p, rewrite)
        did_run_a_command = True

    # directories
    # -----------
    # directories creates the needed directory scruture in $ODOO_SERVER_DATA
    #
    # this option is automaticall executed for all modules that rely on
    # the datastructure to exist.
    if opts.directories:
        handler.create_folders()
        did_run_a_command = True
        return

    # add_site
    # --------
    # add_site adds a site description to the sites.py file
    # add_site_local adds a site description to the sites_local.py file
    if opts.add_site or opts.add_site_local:
        handler.add_site_to_sitelist()
        did_run_a_command = True
        return

    # drop_site
    # --------
    # drop_site removes a site description from the sites.py file
    if opts.drop_site:
        handler.drop_site()
        did_run_a_command = True
        return

    # delete_site_local
    # --------
    # delete_site_local removes a site and all project files
    if opts.delete_site_local:
        handler.delete_site_local()
        did_run_a_command = True
        return

    # add_server
    # ----------
    # add_server_to_localdata
    # add new server info to localdat
    # ----------------------------------
    if opts.add_server:
        handler.add_server_to_localdata()
        did_run_a_command = True
        return

    # edit_site, edit_server
    # ----------------------
    # Lets the user edit the content of config/localdat.py to edit a server
    # description, or change the server description in LOCALDATA['sitesinfo_path']
    # add_site_local adds a site description to the sites_local.py file
    if opts.edit_site or opts.edit_server:
        handler.edit_site_or_server()
        did_run_a_command = True
        return

    # edit_site_preset
    # ----------------------
    # Lets the user edit the preset values for a site
    # the preset values are stored in  LOCALDATA['sitesinfo_path']/sites_global_preset/SITE_NAME
    # or its local equivalent
    if opts.edit_site_preset:
        handler.edit_site_preset()
        did_run_a_command = True
        return

    # add_apache
    # ----------
    # add_apache adds a virtual host to the appache configuration
    # it is meant to run as user root on the remote server
    # if it is run locally (without root permission) it only prints the
    # content it would have written to the console
    #
    # the create the virtual host stanza add_apache collects info from sites.py
    # for $SITENAME. it uses the data found with the key "apache"
    # it collects these data:
    # - vservername: the name/url to acces the virtual server like: www.redcor.ch
    # - protokols: list of protokols to use like ['http', 'https']
    # - vserveraliases: list of alias name like ['redcor.ch']
    # to calculate the port under which the server runs the key
    # docker is used.
    # - odoo_port: port the docker container exposes to acess its odoo server
    if opts.add_apache:
        handler.add_site_to_apache()
        did_run_a_command = True
        return

    if opts.add_nginx:
        handler.add_site_to_nginx()
        did_run_a_command = True
        return

    # list_modules
    # -----------
    # list_modules list defined odoo install blocks
    # each install block contains from a list of addons that and odoo module
    # like CRM installs
    if opts.listmodules:
        handler.install_own_modules(list_only=True)
        did_run_a_command = True
        return

    # listownmodules
    # --------------
    # list the modules that are declared within the selected site
    # installown install all modules declared in the selected site
    # todo: why are the two following options combined here??? !!!!!!!!!!!!
    if opts.listownmodules or opts.installodoomodules:
        handler.install_own_modules()
        did_run_a_command = True
        return

    # alias
    # -----
    # adds a number of aliases to local ~/.bash_aliases
    # these aliases are:
    # $SITENAME cd $PROJECT_HOME/$SITENAME/$SITENAME
    # $SITENAMEhome cd $PROJECT_HOME/$SITENAME
    # $SITENAMEa cd $PROJECT_HOME/$SITENAME/$SITENAME/$SITENAME_addons
    #
    # this option is run automatically when a site is built
    if opts.alias:
        handler.add_aliases()
        did_run_a_command = True
        return

    # pull_sites
    # ----------
    # pulls site descriptions from their repository
    # possible conflicts must be handeled
    if opts.pull_sites:
        handler.pull_sites()
        did_run_a_command = True
        return

    # shell
    # -----
    # shell runs and enters a shell
    # in a docker container
    if opts.shell:
        handler.run_shell()
        did_run_a_command = True
        return

    # manage_mail
    # -----------
    # handles mail settings
    # it accesses a local froxlor db running in mysql
    if opts.manage_mail:
        handler.manage_mail()
        did_run_a_command = True
        return

    # full_update
    # -----------
    # do a git pull of odoo_instances and the sites list
    # then restart odo_instances in a shell mit the option -m
    # if full_update_rebuild is asked for, the run a shell with
    # commands to create a buildout
    if opts.full_update: #or opts.full_update_rebuild or opts.full_update_rebuild_refresh:
        # step one, tell the handler to pull odoo_instances and sites_list
        handler.do_updates()
        # make sure, that changes in the sites definition are updated
        handler.rebuild_site()
        # checkout repositories
        result = checkout_sa(opts)
        failed = result.get('failed')
        did_run_a_command = True
        if failed:
            print(bcolors.FAIL)
            print('the following addons could not be pulled')
            print('----------------------------------------')
            for f in failed:
                print(f)
            print('you migth want to either push you changes, or remove the folder')
            print('---------------------------------------------------------------')
            print(bcolors.ENDC)
            return
        ## if we need a rebuild, we  now do so
        #if opts.full_update_rebuild or opts.full_update_rebuild_refresh:
            #handler.do_rebuild()
        ## it we want to pull, we finally do so also ..
        #if opts.full_update_rebuild_refresh:
            #print bcolors.WARNING
            #print 'processing: update local db for: ', handler.site_name
            #print bcolors.ENDC
            #handler.doUpdate(is_local = handler.is_local)

    # executescript
    # -------------
    #
    # run a script against a running site
    # it must have a run method
    #
    # to be able to load the script, we must have an folder defined
    # in the settings, from where to load it
    if opts.executescript:
        handler.execute_script()
        did_run_a_command = True


    # --------------------------------------------------------
    # stackable options from which we DO NOT return after completion
    # any number of them can be selected, oder of execution is not defined
    # --------------------------------------------------------

    # installown or updateown or removeown
    # ------------------------------------
    # installown install all modules declared in the selected site
    # updateown updates one or all modules declared in the selected site
    # removeown removes one or all modules declared in the selected site
    #
    # to be able to execute do this, the target server has to be running.
    # this server is accessed uding odoo's rpc_api.
    # to do so, info on user, that should access the running server needs
    # to be collected. the following values
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

    if opts.installown or opts.updateown or opts.removeown:
        handler.install_own_modules()
        did_run_a_command = True
    if opts.dinstallown or opts.dupdateown or opts.dremoveown or opts.dinstallodoomodules:
        #handler = dockerHandler(opts, default_values, site_name)
        handler.docker_install_own_modules()
        did_run_a_command = True

    # run tests
    # ---------
    #
    if opts.tests:
        handler.run_tests()
        did_run_a_command = True

    # install server settings
    # -----------------------
    # set the web.base.url and the google captcha keys
    if opts.update_install_serversetting:
        handler.update_install_serversetting()
        did_run_a_command = True

    # set_local_data
    # --------------
    # set local settings from the site description
    if opts.set_local_data or opts.set_local_data_docker:
        handler.set_local_data(use_remote_setting=opts.set_local_data_docker)
        did_run_a_command = True
        
    # set_odoo_settings
    # --------------
    # set local settings from the site description
    if opts.set_odoo_settings or opts.set_odoo_settings_docker or opts.set_odoo_settings_local:
        handler.set_odoo_settings(use_docker=opts.set_odoo_settings_docker, local=opts.set_odoo_settings_local)
        did_run_a_command = True

    # create
    # ------
    # builds or updates a server structure
    # to do so, it does a number of steps
    #   - creates the needed folders in $ODOO_SERVER_DATA
    #   - creates a build structure in $PROJECT_HOME/$SITENAME/$SITENAME
    #     where $PROJECT_HOME is read from the config file.
    #   - copies and sets up all files from skeleton directory to the build structure
    #     this is done executing create_new_project and do_copy
    #   - builds a virtualenv environment in the build structure
    #   - prepares to builds an odoo server within the build structure by
    #     execution  bin/build_odoo within the build structure.
    #     Within this bild environment odoos module path will be set
    #     that it points to the usual odoo directories within the build substructure
    #     and also to the directories within odoo_instances as dictated by the
    #     various modules installed from interpreting the site declaration
    #     in sites.py
    #   - add a "private" addons folder within the build structure called
    #     $SITENAME_addons. This folder is also added to odoos addon path.
    #   - set the data_dir to point to $ODOO_SERVER_DATA/$SITENAME/filestore
    #
    # modules_update
    # -------------
    # it is ment to update a local site.
    # it is not in a well defined state just now
    #
    if opts.create  or opts.modules_update or opts.module_update:
        if opts.create:
            existed = handler.create_or_update_site()
            if existed:
                print()
                print('%s site allredy existed' % handler.site_name)
                print(SITE_EXISTED % (handler.default_values['inner'], handler.site_name))
            else:
                print()
                print('%s site created' % handler.site_name)
                print(SITE_NEW % (handler.site_name, handler.site_name, handler.default_values['inner']))
        # create the folder structure within the datafoler defined in the config
        # this also creates the config file used by a docker server within the
        # newly created folders
        handler.create_folders(quiet=True)
        create_server_config(handler)
        did_run_a_command = True

        # make sure project was added to bash_aliases
        handler.add_aliases()
        # checkout repositories
        checkout_sa(opts)
        did_run_a_command = True

    if opts.create_db_demo or opts.docker_create_db_demo:
        handler.create_db_demo()
        did_run_a_command = True

    # docker_create_container
    # -----------------------
    # it creates and starts a docker container
    # the created container collects info from sites.py for $SITENAME
    # it uses the data found with the key "docker"
    # it collects these data:
    # - container_name: name of the container to create.
    #   must be unique for each remote server
    # - odoo_image_version: name of the docker image used to build
    #   the container
    # - odoo_port: port on which to the running odoo server within the
    #   container can be reached. must be unique for each remote server
    if opts.docker_create_container:
        # "docker -dc", "--create_container",
        handler.check_and_create_container()
        did_run_a_command = True
    if opts.docker_create_update_container:
        # "docker -dcu", "--create_update_container",
        handler.check_and_create_container(update_container=True)
        did_run_a_command = True
    if opts.docker_create_db_container:
        # "docker -dcdb", "--create_db_container",
        handler.check_and_create_container(container_name = 'db')
        did_run_a_command = True

    # docker_add_ssh
    # --------------
    # add an oppenssh server to a running container
    # so we can enter it using ssh
    if opts.docker_add_ssh:
        handler.docker_add_ssh()
        did_run_a_command = True

    # start oppenssh server in a running container
    if opts.docker_start_ssh:
        handler.docker_start_ssh()
        did_run_a_command = True

    # docker_show
    # --------------
    # show some info about a containe
    if opts.docker_show or opts.docker_show_all:
        if opts.docker_show_all:
            handler.docker_show('all')
        else:
            handler.docker_show()
        did_run_a_command = True

    # recreate container
    # ----------------
    # recreate a conainer
    if opts.docker_recreate_container:
        handler.check_and_create_container(rename_container = True)
        did_run_a_command = True
        return

    # pull image
    # ----------
    # pull an actual docker image used by a site
    if opts.docker_pull_image:
        handler.check_and_create_container(pull_image = True)
        did_run_a_command = True
        return

    # build image
    # ----------
    # build docker image used by a site
    if opts.docker_build_image:
        handler.build_image()
        did_run_a_command = True
        return

    # push image
    # ----------
    # push docker image used by a site
    if opts.docker_push_image:
        handler.push_image()
        did_run_a_command = True
        return

    # dataupdate or dataupdate_docker
    # -------------------------------
    # these options are used to copy a running remote server to a lokal
    # odoo instance
    #
    # dataupdate:
    # -----------
    # this copies both an odoo db and the related file data structure from
    # a remote server to a locally existing (buildout created) server.
    # the needed info is gathered from diverse sources:
    # local_data.py
    # -------------
    # - DB_USER: the user name with which to access the local database
    #   default: the logged in user.
    # - DB_PASSWORD: the password to access the local database server
    #   default: odoo
    #   If the option -p --password is used, the password in local_data is
    #   overruled.
    # remote data:
    # ------------
    # to collect data on the remote server the key remote_server is used
    #   to get info from sites.py for $SITENAME
    # - remote_url : the servers url
    # - remote_data_path : COLLECT it from ODOO_SERVER_DATA ??
    # local_data.REMOTE_SERVERS:
    # ---------------------------
    # from this dictonary information on the remote server is collected
    # this is done looking up 'remote_url' in local_data.REMOTE_SERVERS.
    # - remote_user: user to acces the remote server with
    # - remote_pw : password to access the remote user with. should normaly the empty
    #   as it is best only to use a public key.
    # - remote_data_path: how the odoo erverdata can be access on the remote server
    #   ??? should be created automatically
    # sites_pw.py:
    # ------------
    # the several password used for the services to be acces on the odoo instance,
    # the remote server or on the mail server can be mixed in from
    # sites_pw.py.
    # !!!! sites_pw.py should be kept separate, and should not be version controlled with the rest !!!
    #
    # it executes these steps:
    # - it executes a a command in a remote remote server in a remote shell
    #   this command starts a temporary docker container and dumps the
    #   database of the source server to its dump folder which is:
    #       $REMOTE_URL:$ODOO_SERVER_DATA/$SITENAME/dump/$SITENAME.dmp
    # - rsync this file to:
    #       localhost:$ODOO_SERVER_DATA/$SITENAME/dump/$SITENAME.dmp
    # - drop the local database $SITENAME
    # - create the local database $SITENAME
    # - restore the local datbase $SITENAME from localhost:$ODOO_SERVER_DATA/$SITENAME/dump/$SITENAME.dmp
    # - rsync the remote filestore to the local filestore:
    #   which is done with a command similar to:
    #   rsync -av $REMOTEUSER@$REMOTE_URL:$ODOO_SERVER_DATA/$SITENAME/filestore/ localhost:$ODOO_SERVER_DATA/$SITENAME/filestore/
    #
    # run_local_docker
    # ----------------
    # when the option -L --local_docker is used, data is copied from a docker container
    # running on localhost
    if opts.dataupdate or opts.dataupdate_docker or opts.dataupdate_close_connections or opts.dataupdate_no_set_localdata:
        # def __init__(self, opts, default_values, site_name, foldernames=FOLDERNAMES)
        set_local = True
        if opts.dataupdate_no_set_localdata:
            set_local = False
        handler.doUpdate(db_update = not opts.noupdatedb, norefresh=opts.norefresh, set_local = set_local)
        did_run_a_command = True
    if opts.dump_local or opts.dump_local_docker:
        # def __init__(self, opts, default_values, site_name, foldernames=FOLDERNAMES)
        handler.dump_instance()
        did_run_a_command = True

    # transferlocal or transferdocker:
    # this is similar to dataupdate or dataupdate_docker.
    # the difference is, that the the target site is recreated from a a master site.
    # to do so, the 'slave_info' key is looked up in the server info.
    # these valuse are looked up:
    # - master_site the name of the master site, the data is to be copied from
    # - master_domain is the domain from which the master is copied
    #   not used yet
    #
    # run_local_docker
    # ----------------
    # when the option -L --local_docker is used, data is copied from a docker container
    # running on localhost
    if opts.transferlocal or opts.transferdocker:
        if opts.transferlocal:
            handler = DBUpdater(opts, default_values, site_name)
        else:
            handler = dockerHandler(opts, default_values, site_name)
        handler.doTransfer(opts)
        did_run_a_command = True

    # start or restart docker
    if opts.docker_restart_container or opts.docker_start_container or opts.docker_stop_container:
#        handler = dockerHandler(opts, default_values, site_name)
        if opts.docker_start_container:
            handler.start_container()
        elif opts.docker_restart_container:
            handler.restart_container()
        else:
            handler.stop_container()
        did_run_a_command = True


class NameAction(argparse.Action):
    """
    """
    # def error(self, message):
    #     display_help()
    #     exit(1)

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """
        """
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(NameAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """
        """
        print('%r %r %r' % (namespace, values, option_string))
        setattr(namespace, self.dest, values)

class _HelpAction(argparse._HelpAction):
    """
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """
        """
        parser.print_help()

        # retrieve subparsers from parser
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]
        # there will probably only be one subparser_action,
        # but better save than sorry
        for subparsers_action in subparsers_actions:
            # get all subparsers and print help
            for choice, subparser in list(subparsers_action.choices.items()):
                print("Subparser '{}'".format(choice))
                print(subparser.format_help())

        parser.exit()

if __name__ == '__main__':
    usage = "create_system.py is a tool to create and maintain local odoo developement environment\n" \
    "**************************\n" \
    "updating the local environment:\n" \
    "update_local_db.py udates the local postgres database. \nEither in a local docker container or on localhost\n\n" + \
    "First the remote data is read by running a temporary docker container on the remote site\n" \
    "that dumps the remote database into the sites dump directory\n" \
    "then this directory together with the sites data directory is copied to local host using rsync\n\n" \
    "**************************\n" \
    "the following files are read:\n" \
    "sites_list/sites_global: This folder contains a set of site descriptions\n" \
    "sites_list/sites_local:  This folder contains local site descriptions not managed by git\n" \
    "localdata.py: It contains the name and password of the local postgres user. not managed by git\n" \
    "**************************\n" \
    "\n-h for help on usage"
    parent_parser = argparse.ArgumentParser(usage=usage, add_help=False)
    parent_parser.add_argument(
        "-n", "--name",
        action="store", dest="name", default=False,
        help = 'name of the site to create'
    )
    parent_parser.add_argument(
        "-F", "--force",
        action="store_true", dest="force", default=False,
        help = """force. this parameter is used to force setting of new keys into the configuration
            or when copying sitedata without disturbing a running odoo"""
    )
    parent_parser.add_argument(
        "-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="be verbose")

    parent_parser.add_argument(
        "-V", "--version",
        action="store", dest="odoo_version", default='10.0',
        help="odoo version to use")

    parent_parser.add_argument(
        "-N", "--norefresh",
        action="store_true", dest="norefresh", default=False,
        help = 'do not refresh local data, only update database with existing dump, this is the reverse of -nupdb'
    )
    parent_parser.add_argument(
        "-nupdb", "--noupdatedb",
        action="store_true", dest="noupdatedb", default=False,
        help = 'do not update local database, only update local data from remote site, this is the reverse of -N'
    )
    parent_parser.add_argument(
        "-skip", "--skipown",
        action="store", dest="skipown",
        help = 'provide a comma separated (no space) list of add ons to skip. used in conjuction with all.'
    )
    parent_parser.add_argument(
        "-show",
        action="store_true", dest="show", default=False,
        help = 'show configure settings.'
    )
    parent_parser.add_argument(
        "-set", "--set-config",
        action="store", dest="set_config",
        help = 'provide a comma separated (no space) list of key=value pairs to set in the config. if the value is --, the key is removed'
    )
    parent_parser.add_argument(
        "-ip", "--use-ip",
        action="store", dest="use_ip",
        help = 'use the ip provided as SOURCE instead of the one found in the site description'
    )
    parent_parser.add_argument(
        "-ipt", "--use-ip-target",
        action="store", dest="use_ip_target",
        help = 'use the ip provided to write the TARGET instead of localhost'
    )    
    parser_rpc = ArgumentParser(add_help=False)
    parser = ArgumentParser(add_help=False)# ArgumentParser(usage=usage)
    parser.add_argument('--help', action=_HelpAction, help='help for help if you need some help')  # add custom help
    parser_s = parser.add_subparsers(title='subcommands', dest="subparser_name")
    #parser_site   = parser_s.add_parser('s', help='the option -s --site-description has the following subcommands', parents=[parent_parser])

    # -----------------------------------------------
    # manage rpc stuff
    # -----------------------------------------------
    #parser_remote_s = parser_remote.add_subparsers(title='remote commands', dest="rpc_commands")
    parser_rpc.add_argument("-dbh", "--dbhost",
                            action="store", dest="dbhost", default='localhost',
                            help="on what host is database running. default localhost\nif oddo is running in a docker host, this value should be calculated automatically")
    parser_rpc.add_argument("-p", "--dbpw",
                            action="store", dest="dbpw", default='admin',
                            help="the password to access the database. default 'admin'")
    parser_rpc.add_argument("-dbu", "--dbuser",
                            action="store", dest="dbuser", default=DB_USER,
                            help="define user to log into database default %s" % DB_USER)
    parser_rpc.add_argument("-rpch", "--rpchost",
                            action="store", dest="rpchost", default='localhost',
                            help="define where odoo runs and can be accessed trough the rpc api. Default localhost")
    parser_rpc.add_argument("-rpcu", "--rpcuser",
                            action="store", dest="rpcuser", default='admin',
                            help="the user used to acces the running odo server using the rpc api. Default admin")
    parser_rpc.add_argument("-P", "--rpcpw",
                            action="store", dest="rpcpw", default='admin',
                            help="define password for the user that accesses the running odoo server trough the rpc api. default 'admin'")
    parser_rpc.add_argument("-PO", "--port",
                            action="store", dest="rpcport", default=8069,
                            help="define the port on which the odoo server that will be accessed using the rpc api. default 8069")
    parser_rpc.add_argument("-SL", "--set-local-data",
                            action="store_true", dest="set_local_data", default=False,
                            help="set local data from the site description. Together with -F it can also be used remotely")
    parser_rpc.add_argument("-SOS", "--set-odoo-settings",
                            action="store_true", dest="set_odoo_settings", default=False,
                            help="set odoo settings like the mail handlers. The script tries to define for what ip")
    parser_rpc.add_argument("-SOSL", "--set-odoo-settings-local",
                            action="store_true", dest="set_odoo_settings_local", default=False,
                            help="set odoo settings like the mail handlers. The script tries to define for what ip")
    parser_rpc.add_argument("-FL", "--force-local-data",
                            action="store_true", dest="force_local_data", default=False,
                            help="force setting local data from the site description, even when we are on a remote site")
    parser_rpc.add_argument("-E", "--execute-script",
                            action="store", dest="executescript",
                            help="Run a script against a running odoo site. Name must be given")
    parser_rpc.add_argument("-EP", "--execute-script-parameter",
                            action="store", dest="executescriptparameter",
                            help="parameters to be passed to the executed script. It must be a comma separated string of key=value pairs. No spaces!")
    #parser_rpc.add_argument("-dbp", "--dbport",
                    #action="store", dest="dbport", default=5432,
                    #help="define db port default 5432")
    # -----------------------------------------------
    # manage sites create and update sites
    # -----------------------------------------------
    #http://stackoverflow.com/questions/10448200/how-to-parse-multiple-sub-commands-using-python-argparse
    #parser_site_s = parser_site.add_subparsers(title='manage sites', dest="site_creation_commands")
    parser_manage = parser_s.add_parser(
        'create',
        help='create is used to manage local and remote sites',
        parents=[parser_rpc, parent_parser],
        prog='PROG',
        usage='%(prog)s [options]')
    parser_manage.add_argument(
        "-c", "--create",
        action="store_true", dest="create", default=False,
        help = 'create new site structure in %s. Name must be provided' % BASE_INFO.get('project_path', os.path.expanduser('projects'))
    )
    parser_manage.add_argument(
        "-cdb", "--create-db-demo",
        action="store_true", dest="create_db_demo", default=False,
        help = 'create new database with demo data. Name must be provided',
    )
    parser_manage.add_argument(
        "-capw", "--copy-admin-pw",
        action="store", dest="copy_admin_pw",
        help = 'Copy admin pw from source site. option -n must be set and valid. It is the TARGET site.',
    )
    parser_manage.add_argument(
        "-sapw", "--set-admin-pw",
        action="store_true", dest="set_admin_pw", default = False,
        help = 'Set admin password from site description. option -n must be set and valid.',
    )
    parser_manage.add_argument(
        "-D", "--directories",
        action="store_true", dest="directories", default=False,
        help = 'create local directories for site %s. option -n must be set and valid. This option is seldomly needed. Normaly directories are created when needed'  % BASE_INFO.get('odoo_server_data_path', BASE_PATH)
    )
    parser_manage.add_argument(
        "--DELETELOCAL",
        action="store_true", dest="delete_site_local", default=False,
        help = """Delete all elements of a locally installed project. Name must be provided.\n
        This includes (for Proj_Mame):\n
        - ooda/Proj_NAME folders\n
        - ~/projecty/Proj_Name folder\n
        - virtualenv Proj_Name\n
        - database Proj_Name
        """
    )
    parser_manage.add_argument(
        "-lo", "--listownmodules",
        action="store_true", dest="listownmodules", default=False,
        help = 'list installable modules from sites.py sites description. Name must be provided'
    )
    parser_manage.add_argument(
        "-io", "--installown",
        action="store_true", dest="installown", default=False,
        help = 'install all modules listed as addons'
    )
    parser_manage.add_argument(
        "-uo", "--updateown",
        action="store", dest="updateown", default='',
        help = 'update modules listed as addons, pass a comma separated list (no spaces) or all'
    )
    parser_manage.add_argument(
        "-uiss", "--update-install-serversettings",
        action="store_true", dest="update_install_serversetting", default=False,
        help = 'update serversettings like base url or recaptcha keys'
    )
    parser_manage.add_argument(
        "-ro", "--removeown",
        action="store", dest="removeown", default='',
        help = 'remove modules listed as addons, pass a comma separated list (no spaces) or all'
    )
    parser_manage.add_argument(
        "--add-addon",
        action="store", dest="add_addon",
        help = 'add addon to server-description. pass a comma separated list of addon-infos' \
        'of the form url:name;name2;nameX'
    )
    parser_manage.add_argument(
        "-I", "--installodoomodules",
        action="store_true", dest="installodoomodules", default=False,
        help = 'install modules listed as odoo addons'
    )
    parser_manage.add_argument(
        "-ls", "--list",
        action="store_true", dest="list_sites", default=False,
        help = 'list available sites'
    )
    parser_manage.add_argument(
        "-lm", "--listmodules",
        action="store_true", dest="listmodules", default=False,
        help = 'list installable odoo module sets like CRM ..'
    )
    parser_manage.add_argument(
        "-s", "--single-step",
        action="store_true", dest="single_step", default=False,
        help = 'load modules one after the other. MUCH! slower, but problems are easier to spot'
    )
    parser_manage.add_argument(
        "-u", "--dataupdate",
        action="store_true", dest="dataupdate", default=False,
        help = 'update local server from remote server. Automatically set local data'
    )
    #parser_manage.add_argument(
        #"-U", "--dataupdate-no-local-set-data",
        #action="store_true", dest="dataupdate_no_set_localdata", default=False,
        #help = 'update local server from remote server. DO NOT set local data'
    #)
    parser_manage.add_argument(
        "-uu", "--dataupdate-close-conections",
        action="store_true", dest="dataupdate_close_connections", default=False,
        help = 'update local server from remote server, Force close of all connection to the db'
    )
    parser_manage.add_argument(
        "-dump", "--dump-local",
        action="store_true", dest="dump_local", default=False,
        help = """
             dump database data into the servers dump folder. does not use docker. \n
             You can use the option -ipt (ip-target) to dump the site to a remote server.\n
             Using the option -NTS (new-target-site) you can define to what target site the data is dumped.
        """
    )
    parser_manage.add_argument(
        "-M", "--module-update",
        action="store", dest="module_update",
        help = 'Pull modules listed for a site from the repository. Provide comma separated list, no spaces. Name must be provided'
    )
    parser_manage.add_argument(
        "-m", "--modules-update",
        action="store_true", dest="modules_update", default=False,
        help = 'Pull all modules listed for a site from the repository. Name must be provided'
    )
    #parser_manage.add_argument(
        #"-f", "--full-update",
        #action="store_true", dest="full_update", default=False,
        #help = 'run a full upgrade. Name must be provided. A full upgrade consits from a git pull of both odoo_instances and sites_list'\
        #' and then option -m'
    #)
    #parser_manage.add_argument(
        #"-ff", "--full-update-rebuild",
        #action="store_true", dest="full_update_rebuild", default=False,
        #help = 'run a full update and afterwards a rebuild'
    #)
    #parser_manage.add_argument(
        #"-fff", "--full-update-rebuild-refresh",
        #action="store_true", dest="full_update_rebuild_refresh", default=False,
        #help = 'run a full update, afterwards a rebuild and finally pull the live data from the live server'
    #)
    parser_manage.add_argument(
        "-b", "--use-branch",
        action="store", dest="use_branch",
        help = """use branch for addon. pass a comma separated list of addon:branch,addon:branch .. 
                 use all:.. if you want to use the branch for all modules. 
                 It will only be applied if the branch exists for the module"""
    )
    # options -ip and -ipt moved to parent_parser
    parser_manage.add_argument(
        "-NTS", "--new-target-site",
        action="store", dest="new_target_site",
        help = """
           copy the source site identified by name to the TARGET site. 
           This mainly renames the dump file and the target folder inside filestore.
           The target site should be existing and running on the target server.
           The command does not check this!!!!
           
           If you want to copy a local site to an other local site do it like this:
           bin/c -dump SOURCE -NTS TARGET -ipt localhost
        """
    )
    # temporarily handle preset
    parser_manage.add_argument(
        "-PR", "--use_preset",
        action="store", dest="use_preset",
        help = """
        Use preset. This is a temporary solution till preset works
        """
    )
    # -----------------------------------------------
    # support commands
    # -----------------------------------------------
    #parser_manage_s = parser_manage.add_subparsers(title='manage sites', dest="site_manage_commands")
    parser_support= parser_s.add_parser('support', help='the option -sites --support has the following subcommands', parents=[parent_parser])
    parser_support.add_argument(
        "--add-site",
        action="store_true", dest="add_site", default=False,
        help = 'add site description to sites.py from template. Name must be provided'
    )
    parser_support.add_argument(
        "--add-site-local",
        action="store_true", dest="add_site_local", default=False,
        help = 'add site description to sites_local.py from template. Name must be provided'
    )
    parser_support.add_argument(
        "--drop-site",
        action="store_true", dest="drop_site", default=False,
        help = 'drop site description from sites.py. Name must be provided'
    )
    parser_support.add_argument(
        "--add-server",
        action="store", dest="add_server",
        help = 'add server to localdata. server ip and user must be provided in the form user@server_ip'
    )
    parser_support.add_argument(
        "--docker-port",
        action="store", dest="docker_port",
        help = 'provide docker post to new server.  To ckeck for availability use option -lp --list-port'
    )
    parser_support.add_argument(
        "--remote-server",
        action="store", dest="remote_server",
        help = 'provide docker post to new server.  To ckeck for availability use option -lp --list-port'
    )
    parser_support.add_argument(
        "--edit-site",
        action="store_true", dest="edit_site", default=False,
        help = 'edit site. name must be provided'
    )
    parser_support.add_argument(
        "--edit-site-preset",
        action="store_true", dest="edit_site_preset", default=False,
        help = 'edit preset values for site. name must be provided'
    )
    parser_support.add_argument(
        "--edit-server",
        action="store_true", dest="edit_server", default=False,
        help = 'edit local data with server info'
    )
    parser_support.add_argument(
        "-a", "--alias",
        action="store_true", dest="alias", default=False,
        help = 'add project site structure to aliases. create site will run this automatically'
    )
    parser_support.add_argument(
        "-lp",
        action="store_true", dest="list_ports", default=False,
        help = 'list ports used, grouped by server'
    )
    parser_support.add_argument(
        "--upgrade",
        action="store", dest="upgrade",
        help = 'upgrade site to new odoo version. Please indicate the name of the new site. The the target version will be read from there'
    )
    # never used the following, we should get rid of them
    #parser_support.add_argument(
        #"-II",
        #action="store_true", dest="showmodulediff", default=False,
        #help = 'list difference off modules installed as odoo addons, keep old list'
    #)
    #parser_support.add_argument(
        #"-III",
        #action="store_true", dest="showmodulediff_refresh", default=False,
        #help = 'list difference off modules installed as odoo addons, overwrite old list'
    #)
    #parser_support.add_argument(
        #"-r", "--reset",
        #action="store_true", dest="reset", default=False,
        #help = 'reset config settings like data- and projects-path, passwords and such'
    #)
    #parser_support.add_argument(
        #"-rg", "--reset-git",
        #action="store_true", dest="reset_git", default=False,
        #help = 'reset git remote. Used after changing the url to the'
    #)
    #parser_support.add_argument(
        #"-ps", "--pull-sites",
        #action="store_true", dest="pull_sites", default=False,
        #help = 'Pull sites list from its repository'
    #)
    #parser_support.add_argument(
        #"-t", "--test",
        #action="store", dest="tests", default=False,
        #help = 'test addons. Name needed. provide list of addons, separated by , no space. Use all to test all addons'
    #)

    # -----------------------------------------------
    # manage docker
    # -----------------------------------------------
    #parser_support_s = parser_support.add_subparsers(title='docker commands', dest="docker_commands")
    parser_docker = parser_s.add_parser(
        'docker',
        help='the option --docker has the following subcommands',
        parents=[parent_parser])
    parser_docker.add_argument(
        "-dassh", "--docker-add_ssh",
        action="store_true", dest="docker_add_ssh", default=False,
        help = 'add ssh to a docker container'
    )
    parser_docker.add_argument(
        "-duiss",
        action="store_true", dest="update_install_serversetting", default=False,
        help = 'update serversettings like base url or recaptcha keys'
    )
    parser_docker.add_argument(
        "-dsssh", "--docker-start_ssh",
        action="store_true", dest="docker_start_ssh", default=False,
        help = 'start ssh in a running docker container'
    )
    parser_docker.add_argument(
        "-dc", "--create_container",
        action="store_true", dest="docker_create_container", default=False,
        help = 'create a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dcu", "--create_update_container",
        action="store_true", dest="docker_create_update_container", default=False,
        help = 'create a docker container that runs the etc/runodoo.sh script at startup. Name must be provided'
    )
    parser_docker.add_argument(
        "-dE", "--execute-script",
        action="store", dest="executescript",
        help="Run a script against a running odoo site. Name must be given")
    parser_docker.add_argument(
        "-dEP", "--execute-script-parameter",
        action="store", dest="executescriptparameter",
        help="parameters to be passed to the executed script. It must be a comma separated string of key=value pairs. No spaces!")    
    parser_docker.add_argument(
        "-dSL", "--set-local-data-docker",
        action="store_true", dest="set_local_data_docker", default=False,
        help="force setting local data from the site description, even when we are on a remote site")
    parser_docker.add_argument(
        "-dSOS", "--set-odoo-settings-docker",
        action="store_true", dest="set_odoo_settings_docker", default=False,
        help="set odoo settings like the mail handlers. The script tries to define for what ip")
    parser_docker.add_argument(
        "-dbi", "--build_image",
        action="store_true", dest="docker_build_image", default=False,
        help = 'create a docker image. Name must be provided'
    )
    parser_docker.add_argument(
        "-dbis", "--build_image_use_sites",
        action="store", dest="use_sites",
        help = 'use sites to collect libraries to build image'
    )
    parser_docker.add_argument(
        "-dbiC", "--build_image_collect_sites",
        action="store_true", dest="use_collect_sites",
        help = 'collect all libraries from sites with same version'
    )
    parser_docker.add_argument(
        "-dpi", "--push_image",
        action="store_true", dest="docker_push_image", default=False,
        help = 'push a docker image. Name of site must be provided'
    )
    parser_docker.add_argument(
        "-dcapw", "--docker-copy-admin-pw",
        action="store", dest="docker_copy_admin_pw",
        help = 'Copy admin pw from source site in docker conatiners. option -n must be set and valid. It is the TARGET site.',
    )
    parser_docker.add_argument(
        "-dsapw", "--docker-set-admin-pw",
        action="store_true", dest="docker_set_admin_pw", default = False,
        help = 'Set admin password from site description in a docker conatiner. option -n must be set and valid.',
    )
    parser_docker.add_argument(
        "-dr", "--recreate-container",
        action="store_true", dest="docker_recreate_container", default=False,
        help = 'rename and recreate docker container. Name must be provided,'
    )
    parser_docker.add_argument(
        "-dp", "--docker-pull-image",
        action="store_true", dest="docker_pull_image", default=False,
        help = 'pull actual image used by a docker container. Name must be provided,'
    )
    parser_docker.add_argument(
        "-dcdb", "--create_db_container",
        action="store_true", dest="docker_create_db_container", default=False,
        help = 'create a docker databse container. It will be named db.  You must also set option -dcdbPG to set postgres version'
    )
    parser_docker.add_argument(
        "-dcdbPG", "--set-postgers-version",
        action="store", dest="set_postgers_version",
        help = 'define postgres version to be used. Something like 9.6 or 10.0'
    )
    parser_docker.add_argument(
        "-ds", "--start_container",
        action="store_true", dest="docker_start_container", default=False,
        help = 'start a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dshow",
        action="store_true", dest="docker_show", default=False,
        help = 'show some info about a container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dshowa",
        action="store_true", dest="docker_show_all", default=False,
        help = 'show all info about a container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dS", "--stop_container",
        action="store_true", dest="docker_stop_container", default=False,
        help = 'stop a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-drs", "--restart_container",
        action="store_true", dest="docker_restart_container", default=False,
        help = 'restart a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-ddbname", "--dockerdbname",
        action="store", dest="dockerdbname", # no default, otherwise we can not get it from the site description
        help="user to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerdb_container_name'])

    parser_docker.add_argument(
        "-ddbuser", "--dockerdbuser",
        action="store", dest="dockerdbuser", # no default, otherwise we can not get it from the site description
        help="user to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerdbuser'])

    parser_docker.add_argument(
        "-ddbpw",
        action="store", dest="dockerdbpw", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerdbpw'])

    parser_docker.add_argument(
        "-drpcuser",
        action="store", dest="drpcuser", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerrpcuser'])

    parser_docker.add_argument(
        "-drpcuserpw",
        action="store", dest="drpcuserpw", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerrpcuserpw'])

    parser_docker.add_argument(
        "-ddpo", "--dockerdbport",
        action="store", dest="dockerdbport", default='',
        help="port on which to access database in the db container\nnormally taken from config")

    #parser_docker.add_argument(
        #"-dtd", "--transferdocker",
        #action="store_true", dest="transferdocker", default=False,
        #help = 'transfer data from master to slave using docker'
    #)
    parser_docker.add_argument(
        "-dud", "--dataupdate_docker",
        action="store_true", dest="dataupdate_docker", default=False,
        help = 'update local data from remote server into local docker. Name must be provided.\nRespects -N and -nupdb options'
    )
    parser_docker.add_argument(
        "-ddump", "--dump-local-docker",
        action="store_true", dest="dump_local_docker", default=False,
        help = 'dump database data into the servers dump folder. does use docker'
    )
    parser_docker.add_argument(
        "-dio", "--dinstallown",
        action="store_true", dest="dinstallown", default=False,
        help = 'install all modules listed as addons. Name must be provided'
    )
    parser_docker.add_argument(
        "-duo", "--dupdateown",
        action="store", dest="dupdateown", default='',
        help = 'update modules listed as addons, pass a comma separated list (no spaces) or all. Name must be provided'
    )
    parser_docker.add_argument(
        "-dro", "--dremoveown",
        action="store", dest="dremoveown", default='',
        help = 'remove modules listed as addons, pass a comma separated list (no spaces) or all. Name must be provided'
    )
    parser_docker.add_argument(
        "-dI", "--dinstallodoomodules",
        action="store_true", dest="dinstallodoomodules", default=False,
        help = 'install modules listed as odoo addons into docker. Name must be provided'
    )

    # !!! local_docker is added to parent_parser, not parser_docker
    parent_parser.add_argument(
        "-L", "--local-docker",
        action="store_true", dest="local_docker", default=False,
        help = 'allways use a docker running locally as source when updating local data'
    )
    parser_docker.add_argument(
        "-shell", "--shell",
        action="store", dest="shell", default=False,
        help = 'open a shell in a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dip", "--use-ip-docker",
        action="store", dest="use_ip_docker",
        help = 'docker: use the ip provided instead of the one found in the site description'
    )

    # -----------------------------------------------
    # manage remote server (can be localhost)
    # -----------------------------------------------
    #parser_docker_s = parser_docker.add_subparsers(title='remote commands', dest="remote_commands")
    parser_remote = parser_s.add_parser(
        'remote',
        help='the command remote is used to manage the remote server.',
        parents=[parent_parser])
    parser_remote.add_argument(
        "--add-apache",
        action="store_true", dest="add_apache", default=False,
        help = 'add apache.conf to the apache configuration. Name must be provided'
    )
    parser_remote.add_argument(
        "--add-nginx",
        action="store_true", dest="add_nginx", default=False,
        help = 'add configuration to the list of nginx configurations. Name must be provided'
    )
    parser_remote.add_argument(
        "-cert", "--create-certificate",
        action="store", dest="create_certificate",
        help = 'create or update lets encrypt ssl certificate. Name must be provided'
    )
    # -----------------------------------------------
    # manage mails
    # -----------------------------------------------
    parser_mail = parser_s.add_parser(
        'mail',
        help='the command mail is used to manage mails.',
        parents=[parent_parser])

    parser_mail.add_argument(
        "-mm", "--manage_mail",
        action="store_true", dest="manage_mail", default=False,
        help = 'manage mail seting. Name must be provided'
    )
    parser_mail.add_argument(
        "-myh", "--mysql_host",
        action="store", dest="mysql_host", default='localhost',
        help = 'host on which mysql server with mail settings. Default localhost'
    )
    parser_mail.add_argument(
        "-myP", "--mysql_port",
        action="store", dest="mysql_port", default=3306,
        help = 'mysql port. Default 3306'
    )
    parser_mail.add_argument(
        "-myu", "--mysql_user",
        action="store", dest="mysql_user", default='froxlor',
        help = 'mysql user. Default froxlor'
    )
    parser_mail.add_argument(
        "-myp", "--mysql_password",
        action="store", dest="mysql_password",
        help = 'mysql_password'
    )
    parser_mail.add_argument(
        "-myd", "--mysql_db",
        action="store", dest="mysql_db", default='froxlor',
        help = 'mysql database with emails. Default froxlor'
    )

    #(opts, args) = parser.parse_args()
    command_line = ' '.join(sys.argv)
    parser.set_default_subparser('create')
    args, unknownargs = parser.parse_known_args()
    opts = OptsWrapper(args)
    opts.command_line = command_line # so we can reexecute
    if not opts.name and unknownargs:
        unknownargs = [a for a in unknownargs if a and a[0] != '-']
        if unknownargs:
            opts._o.__dict__['name'] = unknownargs[0]

    # --------------------------------------------------------
    # set a marker, so we can check if any command was executed
    # --------------------------------------------------------
    did_run_a_command = False

    main(opts) #opts.noinit, opts.initonly)

    if 0: #not did_run_a_command:
        print(bcolors.FAIL)
        print('*' * 80)
        print('it looks as if no valid comand was executed')
        print('*' * 80)
        print(bcolors.ENDC)
        
