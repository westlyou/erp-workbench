#!bin/python
import os
import sys
# BASE_PATH is the home directory of odoo_instances
BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
MIGRATE_FOLDER = '%s/upgrade/' % BASE_PATH
BASE_INFO = {}
import getpass
ACT_USER = getpass.getuser()
from scripts.bcolors import bcolors
BASEINFO_CHANGED = """
%s--------------------------------------------------
The structure of the config files have changed.
You will be asked to provide some config data again.
--------------------------------------------------%s
""" %(bcolors.FAIL, bcolors.ENDC)

# base defaults are the defaults we are using for the base info if they where not set
user_home = os.path.expanduser('~')
BASE_DEFAULTS = {
    #name, explanation, default
    'sitesinfo_path' : (
        'sitesinfo path',                 # display
        """path to the folder where sites.py and sites_local.py is found
        This folder should be maintained by git""",    # help
        '%s/sites_list/' % BASE_PATH  # default
    ),
    'sitesinfo_url' : (
        'sitesinfo url',                 # display
        """url to the repository where sites.py and sites_local.py is maintained.
        If it is localhost it will be created for you but not added to a repo'""", # help
        'localhost',
        # 'https://gitlab.redcor.ch/redcor_customers/sites_list.git'   # default
    ),
    'project_path' : (
        'project path',                 # display
        """path to the projects
        Here a structure for each odoo site is created to build and run odoo servers""", # help
        '%s/projects' % user_home  # default
    ),
    'odoo_server_data_path' : (
        'server data path',              # display
        """path to server data. Here for every site a set of folders is created
        that will contain the servers config filestore, log- and dump-files.""", # help
        BASE_PATH  # default
    ),
    'docker_dumper_image' : (
        'Image to be used to create a dumper container',              # display
        """When transfering data between sites we need a helper docker container
        that can access the database and dump the data into a file""", # help
        'robertredcor/dumper',
    ),
    'repo_mapper' : (
        'Access Urls to the source code repositories',              # display
        """What is the urls to use when accesing github or gitlab.
        provide a comma separated list of repository=url pairs
        default "gitlab.redcor.ch=ssh://git@gitlab.redcor.ch:10022/""", # help
        'gitlab.redcor.ch=ssh://git@gitlab.redcor.ch:10022/',
    ),
    'local_user_mail' : (
        'mail address of the local user',              # display
        'mail address of the local user', # help
        '%s@redo2oo.ch' % ACT_USER,
    )
}
try:
    from .base_info import base_info as BASE_INFO
    NEED_BASEINFO = False
    # check whether BASE_DEFAULTS has new keys
    for k in list(BASE_DEFAULTS.keys()):
        if k not in BASE_INFO:
            NEED_BASEINFO = True
            print()
except ImportError:
    NEED_BASEINFO = True
# what folders do we need to create in odoo_sites for a new site
FOLDERNAMES = ['addons','dump','etc','filestore', 'log', 'ssl', 'start-entrypoint.d', 'presets']
# base info filename points to file where some default values are stored
# base_info = {'project_path': '/home/robert/projects', 'skeleton': 'odoo/skeleton'}
BASE_INFO_NAME = 'base_info'
BASE_INFO_FILENAME = '%s/config/%s.py' % (BASE_PATH, BASE_INFO_NAME)

PROJECT_DEFAULTS = {
    #name, explanation, default
    'projectname' : ('project name', 'what is the project name', 'projectname'),
    'odoo_version' : ('odoo version', 'version of odoo', '12'),
    'odoo_minor' : ('minor part of odoo version', 'minor part version of odoo', '.0'),
    'flectra_version' : ('odoo version', 'version of flectra', '1.1'),
    'flectra_minor' : ('minor part of flectra version', 'minor part version of flectra', '.4'),
}
# sites is a combination created from "regular" sites listed in sites.py
# an a list of localsites listed in local_sites.py
#from sites import SITES, SITES_L as SITES_LOCAL
# start with checking whether installation is finished
try:
    pwd = os.getcwd()
    from scripts.sites_handler import SitesHandler
    sites_handler = SitesHandler(BASE_PATH) # will exit when installation not yet finished
    SITES, SITES_LOCAL = sites_handler.get_sites()
    # MARKER is used to mark the position in sites.py to add a new site description
    MARKER = sites_handler.marker # from messages.py
    try:
        from config.localdata import REMOTE_USER_DIC, APACHE_PATH, DB_USER, DB_PASSWORD
    except ImportError:
        print('please create config/localdata.py')
        print('it must have values for REMOTE_USER_DIC, APACHE_PATH, DB_USER, DB_PASSWORD, DB_PASSWORD_LOCAL')
        print('use template/localdata.py as template')
        DB_USER = ACT_USER
        DB_PASSWORD = 'admin'
        DB_PASSWORD_LOCAL = 'admin'
        raise ImportError
        #sys.exit()
    except SyntaxError as e:
        print('please edit config/localdata.py. It seems to have a syntax error\n' + str(e) )
    os.chdir(pwd)
except ImportError as e:
    APACHE_PATH = ''
    SITES, SITES_LOCAL = {},{}
    MARKER = ''
    sites_handler = None
    print(str(e))
except OSError:
    # we probably runing from within docker
    print('-------------------------------------->>>>', os.getcwd())
    BASE_INFO['odoo_server_data_path'] = '/mnt/sites'
    if os.getcwd() == '/mnt/sites':
        print('------------------------------')
        raise ImportError()
    
# try to get also NGINX_PATH
# if not possible, provide warning and assume standard location
try:
    from config.localdata import NGINX_PATH
except ImportError as e:
    print(bcolors.WARNING + '*' * 80)
    print('could not read nginx path from config.localdata')
    print('assuming it is: /etc/nginx/')
    print('you can fix this by executing: bin/e')
    print("and adding: NGINX_PATH = '/etc/nginx/'")
    print('*' * 80 + bcolors.ENDC)
    NGINX_PATH = '/etc/nginx/'
except Exception as e:
    pass
    
try:
    from config.localdata import DB_PASSWORD_LOCAL
except ImportError:
    # BBB
    DB_PASSWORD_LOCAL = 'admin'

if sites_handler:
    # automatically update sites list only, when BASE_INFO[''] is set
    sites_handler.pull()

# file to which site configuration will be written
LOGIN_INFO_FILE_TEMPLATE = '%s/login_info.cfg.in'

# file to which pip requirements will be written
REQUIREMENTS_FILE_TEMPLATE = '%s/install/requirements.txt'
# elements we add with pip install when we are in a local environment
MODULES_TO_ADD_LOCALLY = ['pytest-odoo']

SITES_HOME =  os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

try:
    from .version_info import *
except:
    version_info = None

#p =  ''#os.path.split(os.path.realpath(__file__))[0]
if not os.path.exists('%s/config/globaldefaults.py' % BASE_PATH):
    ## silently copy the defualts file
    #act = os.getcwd()
    #os.chdir(p)
    open('%s/config/globaldefaults.py' % BASE_PATH, 'w').write(open('%s/templates/globaldefaults.py' % BASE_PATH, 'r').read())
    #os.chdir(act)
try:   
    from globaldefaults import GLOBALDEFAULTS
except ImportError:
    sys.path.insert(0, '%s/config' % BASE_PATH)
    from globaldefaults import GLOBALDEFAULTS

# NEED_NAME is a list of options that must provide a name
NEED_NAME = [
    "add_apache",
    "add_site",
    "add_site_local",
    "create",
    "create_certificate",
    "create_container",
    'copy_admin_pw',
    "dataupdate",
    "dataupdate_close_connections",
    "directories",
    "docker_add_ssh",
    #"docker_show",
    "edit_site",
    "module_add",
    "module_update",
    "modules_update",
    "name",
    "norefresh",
    'full_update',
    'full_update_rebuild',
    'full_update_rebuild_refresh',
    'update_install_serversetting',
]

# NO_NEED_NAME is a list of options that do not need to provide a name
NO_NEED_NAME = [
    "add_server",
    "alias",
    "docker_create_db_container",
    "edit_server",
    "list_sites",
    "listmodules",
    "module_create",
    "pull",
    "reset",
    "set_config",
    "shell",
    "show",
    "use_branch",
    "list_ports"
]
# need name and target 
NEED_TARGET = [
    'copy_admin_pw',
]
# is know IP to remote server needed
NO_NEED_SERVER_IP = [
    'edit_site',
]
FLECTRA_VERSIONS = {
    '1.0' : {
        'python_ver' : 'python3', 
        'python_path' : '/usr/bin/python3',
        'branch' : '1.0',
        'tag' : 'v1.0.0',
    },
    '1.1.0' : {
        'python_ver' : 'python3', 
        'python_path' : '/usr/bin/python3',
        'branch' : '1.0',
        'tag' : 'v1.1.0',
    },
    '1.2.0' : {
        'python_ver' : 'python3', 
        'python_path' : '/usr/bin/python3',
        'branch' : '1.0',
        'tag' : 'v1.2.0',
        'pip' : [
            'phonenumbers',
            ''
        ]

    },
}


ODOO_VERSIONS_ = {
    '7.0' : { # elfero
        'python_ver' : 'python2',
        'python_path' : '/usr/bin/python2',
    },
    '9.0' : {
        'python_ver' : 'python2',
        'python_path' : '/usr/bin/python2',
    },
    '10.0' : {
        'python_ver' : 'python2',
        'python_path' : '/usr/bin/python2',
    },
    '11.0' : {
        'python_ver' : 'python3',
        'python_path' : '/usr/bin/python3',
    },
}
ODOO_VERSIONS = {
    '7.0' : ODOO_VERSIONS_['7.0'],
    '9.0' : ODOO_VERSIONS_['9.0'],
    '10.0' : ODOO_VERSIONS_['10.0'],
    '11.0' : ODOO_VERSIONS_['11.0'],
    '7' : ODOO_VERSIONS_['7.0'],
    '9' : ODOO_VERSIONS_['9.0'],
    '10' : ODOO_VERSIONS_['10.0'],
    '11' : ODOO_VERSIONS_['11.0'],
    '12' : {
        'python_ver' : 'python3',
        'python_path' : '/usr/bin/python3',
    },
}

# commands to use within a dockerfile to pull aditional libraries
APT_COMMAND = 'apt'
PIP_COMMAND = 'pip'
