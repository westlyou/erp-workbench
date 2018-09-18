import os
from config import BASE_PATH, BASE_INFO
from scripts.parser_handler import ParserHandler

def add_options_create(parser, result_dic):
    """add options to the create parser
    
    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parser_manage = ParserHandler(parser, result_dic)

    parser_manage.add_argument(
        "-c", "--create",
        action="store_true", dest="create", default=False,
        help='create new site structure in %s. Name must be provided' % BASE_INFO.get(
            'project_path', os.path.expanduser('projects')),
        need_name=True
    )
    parser_manage.add_argument(
        "-D", "--directories",
        action="store_true", dest="directories", default=False,
        help='create local directories for site %s. option -n must be set and valid. This option is seldomly needed. Normaly directories are created when needed'  % BASE_INFO.get('erp_server_data_path', BASE_PATH),
        need_name=True        
    )
    parser_manage.add_argument(
        "--DELETELOCAL",
        action="store_true", dest="delete_site_local", default=False,
        help="""Delete all elements of a locally installed project. Name must be provided.\n
        This includes (for Proj_Mame):\n
        - ooda/Proj_NAME folders\n
        - ~/projecty/Proj_Name folder\n
        - virtualenv Proj_Name\n
        - database Proj_Name
        """,
        need_name=True        
    )
    parser_manage.add_argument(
        "-lo", "--listownmodules",
        action="store_true", dest="listownmodules", default=False,
        help='list installable modules from sites.py sites description. Name must be provided',
        need_name=True        
    )
    parser_manage.add_argument(
        "-io", "--installown",
        action="store_true", dest="installown", default=False,
        help='install all modules listed as addons',
        need_name=True        
    )
    parser_manage.add_argument(
        "-uo", "--updateown",
        action="store", dest="updateown", default='',
        help='update modules listed as addons, pass a comma separated list (no spaces) or all',
        need_name=True
    )
    parser_manage.add_argument(
        "-ro", "--removeown",
        action="store", dest="removeown", default='',
        help='remove modules listed as addons, pass a comma separated list (no spaces) or all',
        need_name=True
    )
    parser_manage.add_argument(
        "-I", "--installodoomodules",
        action="store_true", dest="installodoomodules", default=False,
        help='install modules listed as odoo addons',
        need_name=True
    )
    parser_manage.add_argument(
        "-ls", "--list",
        action="store_true", dest="list_sites", default=False,
        help='list available sites'
    )
    parser_manage.add_argument(
        "-s", "--single-step",
        action="store_true", dest="single_step", default=False,
        help='load modules one after the other. MUCH! slower, but problems are easier to spot'
    )
    parser_manage.add_argument(
        "-u", "--dataupdate",
        action="store_true", dest="dataupdate", default=False,
        help='update local server from remote server. Automatically set local data'
    )
    parser_manage.add_argument(
        "-uu", "--dataupdate-close-conections",
        action="store_true", dest="dataupdate_close_connections", default=False,
        help='update local server from remote server, Force close of all connection to the db'
    )
    parser_manage.add_argument(
        "-dump", "--dump-local",
        action="store_true", dest="dump_local", default=False,
        help="""
             dump database data into the servers dump folder. does not use docker. \n
             You can use the option -ipt (ip-target) to dump the site to a remote server.\n
             Using the option -NTS (new-target-site) you can define to what target site the data is dumped.
        """,
        need_name=True
    )
    parser_manage.add_argument(
        "-M", "--module-update",
        action="store", dest="module_update",
        help='Pull modules listed for a site from the repository. Provide comma separated list, no spaces. Name must be provided',
        need_name=True
    )
    parser_manage.add_argument(
        "-m", "--modules-update",
        action="store_true", dest="modules_update", default=False,
        help='Pull all modules listed for a site from the repository. Name must be provided',
        need_name=True
    )
    parser_manage.add_argument(
        "-b", "--use-branch",
        action="store", dest="use_branch",
        help="""use branch for addon. pass a comma separated list of addon:branch,addon:branch .. 
                 use all:.. if you want to use the branch for all modules. 
                 It will only be applied if the branch exists for the module"""
    )
    # options -ip and -ipt moved to parent_parser
    parser_manage.add_argument(
        "-NTS", "--new-target-site",
        action="store", dest="new_target_site",
        help="""
           copy the source site identified by name to the TARGET site. 
           This mainly renames the dump file and the target folder inside filestore.
           The target site should be existing and running on the target server.
           The command does not check this!!!!
           
           If you want to copy a local site to an other local site do it like this:
           bin/c -dump SOURCE -NTS TARGET -ipt localhost
        """,
        need_name=True
    )
