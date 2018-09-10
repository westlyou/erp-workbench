#!bin/python
import os
import sys
# BASE_PATH is the home directory of erp_workbench
BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
MIGRATE_FOLDER = '%s/upgrade/' % BASE_PATH
BASE_INFO = {}
import getpass
ACT_USER = getpass.getuser()
from scripts.bcolors import bcolors

# first thing we do, is make sure there is a config.yaml file
# if it does not exist, we copy it from config.yaml.in
config_yaml = '%s/config/config.yaml' % BASE_PATH
data_path = os.path.normpath('%s/config_data' % BASE_PATH)
user_home = os.path.expanduser('~')
if not os.path.exists(config_yaml):
    from shutil import copyfile
    copyfile('%s.in' % config_yaml, config_yaml)

# the base info we need to access the various parts of erp-workbench 
# is in some yaml file in erp-workbench the config folder
from scripts.construct_defaults import check_and_update_base_defaults
construct_result = {}
must_reload = check_and_update_base_defaults(
    BASE_PATH,
    user_home,
    ACT_USER,
    [(
        config_yaml,
        '%s/data_path, achtung testen was richtig ist
        # if one of the values got "configured away"
        '%s/templates/config.yaml' % BASE_PATH,
    )],
    construct_result
)

BASEINFO_CHANGED = """
%s--------------------------------------------------
The structure of the config files have changed.
please check %s if everything ist correct.
--------------------------------------------------%s
""" %(bcolors.FAIL, config_yaml, bcolors.ENDC)

# base defaults are the defaults we are using for the base info if they where not set
NEED_BASEINFO = False
try:
    from .config_data.base_info import base_info as BASE_INFO
except ImportError:
    NEED_BASEINFO = True
if NEED_BASEINFO or must_reload:
    print(BASEINFO_CHANGED)
if must_reload:
    BASE_INFO = construct_result[config_yaml]['base_info']

# what folders do we need to create in odoo_sites for a new site
FOLDERNAMES = ['addons','dump','etc','filestore', 'log', 'ssl', 'start-entrypoint.d', 'presets']

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
sites_handler = None
APACHE_PATH = ''
DB_USER = ACT_USER
DB_PASSWORD = 'admin'
DB_PASSWORD_LOCAL = 'admin'
SITES, SITES_LOCAL = {},{}
MARKER = ''
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
    print(str(e))
except OSError:
    # we probably runing from within docker
    BASE_INFO['erp_server_data_path'] = '/mnt/sites'
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
