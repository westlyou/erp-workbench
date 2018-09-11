#!bin/python
import os
import sys
import getpass
from scripts.bcolors import bcolors

"""
rename files config/localdata.py -> confid/local_data/servers_info.py
    GLOBALDEFAULTS --> docker_info.DOCKER_DEFAULTS

"""

# ACT_USER is the actualy logged in user
ACT_USER = getpass.getuser()
# BASE_PATH is the home directory of erp_workbench
BASE_PATH  = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
SITES_HOME = BASE_PATH #os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
# migrate folder will be used when migrating to a new odoo version
MIGRATE_FOLDER = '%s/upgrade/' % BASE_PATH
BASE_INFO = {}
#DB_USER = ACT_USER
DB_PASSWORD = 'admin'
SITES, SITES_LOCAL = {},{}
MARKER = ''
# what folders do we need to create in odoo_sites for a new site
FOLDERNAMES = ['addons','dump','etc','filestore', 'log', 'ssl', 'start-entrypoint.d', 'presets']

# first thing we do, is make sure there exists all *.yaml files
# if it does not exist, we copy it from ??.yaml.in

data_path = os.path.normpath('%s/config_data' % BASE_PATH)
user_home = os.path.expanduser('~')
yaml_dic = {}
for y_info in  (
        ('config', 'base_info.py'), 
        ('servers', 'servers_info.py'), 
        ('docker', 'docker_info.py'), 
        ('project', 'project_info.py')
    ):
    y_name, file_name = y_info
    config_yaml = '%s/config/%s.yaml' % (BASE_PATH, y_name)
    if not os.path.exists(config_yaml):
        from shutil import copyfile
        copyfile('%s.in' % config_yaml, config_yaml)
    # build a list to be sent to check_and_update_base_defaults
    yaml_dic[y_name] = (
        config_yaml,
        '%s/config/config_data/%s' % (BASE_PATH, file_name),
        '%s/templates/%s.yaml' % (BASE_PATH, y_name), 
    )

# the base info we need to access the various parts of erp-workbench 
# is in some yaml file in erp-workbench the config folder
from scripts.construct_defaults import check_and_update_base_defaults
construct_result = {}
vals = {
    'USER_HOME' : user_home, 
    'BASE_PATH' : BASE_PATH,
    'ACT_USER'  : ACT_USER,
    'DB_USER'   : ACT_USER,
}
# from pprint import pformat
# print(pformat(yaml_dic))
must_reload = check_and_update_base_defaults(
    yaml_dic.values(),
    vals,
    construct_result
)

# now we can load the files we just created
BASEINFO_CHANGED = """
%s--------------------------------------------------
The structure of the config files have changed.
please check %s if everything ist correct.
--------------------------------------------------%s
""" %(bcolors.FAIL, config_yaml, bcolors.ENDC)

# base defaults are the defaults we are using for the base info if they where not set
NEED_BASEINFO = False
try:
    from config.config_data.base_info import BASE_DEFAULTS as BASE_INFO
except ImportError:
    NEED_BASEINFO = True
if NEED_BASEINFO or must_reload:
    print(BASEINFO_CHANGED)
if must_reload:
    if construct_result[yaml_dic['config'][0]]:
        BASE_INFO = construct_result[yaml_dic['config'][0]]['BASE_DEFAULTS']
# load docker info
if must_reload and construct_result[yaml_dic['docker'][0]]:
    DOCKER_DEFAULTS = construct_result[yaml_dic['docker'][0]]['DOCKER_DEFAULTS']
else:
    from config.config_data.docker_info import DOCKER_DEFAULTS
# load project defaults
if must_reload and construct_result[yaml_dic['project'][0]]:
    PROJECT_DEFAULTS = construct_result[yaml_dic['project'][0]]['PROJECT_DEFAULTS']
else:
    from config.config_data.project_info import PROJECT_DEFAULTS

# sites is a combination created from "regular" sites listed in sites.py
# an a list of localsites listed in local_sites.py
#from sites import SITES, SITES_L as SITES_LOCAL
# start with checking whether installation is finished
sites_handler = None

try:
    pwd = os.getcwd()
    from scripts.sites_handler import SitesHandler
    sites_handler = SitesHandler(BASE_PATH) # will exit when installation not yet finished
    SITES, SITES_LOCAL = sites_handler.get_sites()
    # MARKER is used to mark the position in sites.py to add a new site description
    MARKER = sites_handler.marker # from messages.py
    os.chdir(pwd)
except ImportError as e:
    print(str(e))
except OSError:
    # we probably runing from within docker
    BASE_INFO['erp_server_data_path'] = '/mnt/sites'
    if os.getcwd() == '/mnt/sites':
        print('------------------------------')
        raise ImportError()

# file to which site configuration will be written
LOGIN_INFO_FILE_TEMPLATE = '%s/login_info.cfg.in'

# file to which pip requirements will be written
REQUIREMENTS_FILE_TEMPLATE = '%s/install/requirements.txt'
# elements we add with pip install when we are in a local environment
MODULES_TO_ADD_LOCALLY = ['pytest-odoo']

try:
    from .version_info import *
except:
    version_info = None

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
