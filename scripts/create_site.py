#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import RawTextHelpFormatter, ArgumentParser
import readline, glob
import sys, time, os
import subprocess
#import xml.dom.minidom
import re
import argparse
import argcomplete
from bcolors import bcolors
from banner import BANNER_HEAD, BANNER_TEXT

sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
from scripts.messages import *
from config import NEED_BASEINFO, BASE_INFO_FILENAME, BASE_DEFAULTS

from scripts.utilities import update_base_info, \
     create_server_config, checkout_sa, \
     list_sites

if NEED_BASEINFO:
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
    APACHE_PATH, DB_USER, DB_PASSWORD, LOGIN_INFO_FILE_TEMPLATE, \
    REQUIREMENTS_FILE_TEMPLATE, GLOBALDEFAULTS

from config.handlers import SiteCreator
from config.handlers import DockerHandler
from config.handlers import SupportHandler
from config.handlers import RemoteHandler
from config.handlers import MailHandler

# get config options
from scripts.options_create import add_options_create
from scripts.options_parent import add_options_parent
from scripts.options_rpc import add_options_rpc
from scripts.options_support import add_options_support

banner = bcolors.red + BANNER_HEAD  + bcolors.normal + BANNER_TEXT

#ascii art by: Cara Pearson
colors = bcolors
class tabCompleter(object):

    def pathCompleter(self, text, state):
        line = readline.get_line_buffer().split()

        return [x for x in glob.glob(text+'*')][state]

def interactive():
    t = tabCompleter()
    singluser = ""
    if args.interactive is True:
        print(colors.white + "\n\nWelcome to interactive mode!\n\n" + colors.normal)
        print(colors.red + "WARNING:" + colors.white + " Leaving an option blank will leave it empty and refer to default\n\n" + colors.normal)
        print("Available services to brute-force:")
        for serv in services:
            srv = serv
            for prt in services[serv]:
                iplist = services[serv][prt]
                port = prt
                plist = len(iplist)
                print("Service: " + colors.green + str(serv) + colors.normal + " on port " + colors.red + str(port) + colors.normal + " with " + colors.red + str(plist) + colors.normal + " hosts")

        args.service = input('\n' + colors.lightblue + 'Enter services you want to brute - default all (ssh,ftp,etc): ' + colors.red)

        args.threads = input(colors.lightblue + 'Enter the number of parallel threads (default is 2): ' + colors.red)

        args.hosts = input(colors.lightblue + 'Enter the number of parallel hosts to scan per service (default is 1): ' + colors.red)

        if args.passlist is None or args.userlist is None:
            customword = input(colors.lightblue + 'Would you like to specify a wordlist? (y/n): ' + colors.red)
        if customword == "y":
            readline.set_completer_delims('\t')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(t.pathCompleter)
            if args.userlist is None and args.username is None:
                args.userlist = input(colors.lightblue + 'Enter a userlist you would like to use: ' + colors.red)
                if args.userlist == "":
                    args.userlist = None
            if args.passlist is None and args.password is None:
                args.passlist = input(colors.lightblue + 'Enter a passlist you would like to use: ' + colors.red)
                if args.passlist == "":
                    args.passlist = None

        if args.username is None or args.password is None: 
            singluser = input(colors.lightblue + 'Would to specify a single username or password (y/n): ' + colors.red)
        if singluser == "y":
            if args.username is None and args.userlist is None:
                args.username = input(colors.lightblue + 'Enter a username: ' + colors.red)
                if args.username == "":
                    args.username = None
            if args.password is None and args.passlist is None:
                args.password = input(colors.lightblue + 'Enter a password: ' + colors.red)
                if args.password == "":
                    args.password = None

        if args.service == "":
            args.service = "all"
        if args.threads == "":
            args.threads = "2"
        if args.hosts == "":
            args.hosts = "1"

    print(colors.normal)


    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.file is None and args.modules is False:
        parser.error("argument -f/--file is required")
    return args

#https://stackoverflow.com/questions/6365601/default-sub-command-or-handling-no-sub-command-with-argparse
def set_default_subparser(self, name, args=None):
    """default subparser selection. Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    , tested with 2.7, 3.2, 3.3, 3.4
    it works with 2.6 assuming argparse is installed
    """
    subparser_found = False
    name_to_return = ''
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
                    name_to_return = sp_name
        if not subparser_found:
            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if args is None:
                sys.argv.insert(1, name)
            else:
                args.insert(0, name)
            name_to_return = name
    return name_to_return



def main(opts, parsername):
    """
    """
    default_handler = SiteCreator
    opts.subparser_name = parsername
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
        handler = SiteCreator(opts, SITES)

    # ----------------------
    # create commands
    # ----------------------
    if parsername == 'create':
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
        if opts.create  or opts.modules_update or opts.module_update:
            if opts.create:
                existed = handler.create_or_update_site()
                if existed:
                    print()
                    print('%s site allredy existed' % handler.site_name)
                    print(SITE_EXISTED % (handler.default_values['inner'], handler.site_name))
                else:
                    if handler.site_name:
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
            
        # list_sites
        # ----------
        # list_sites lists all existing sites both from global and local sites
        if opts.list_sites:
            list_sites(SITES)
            did_run_a_command = True
            return
        
        
    # ----------------------
    # support commands
    # ----------------------
    if parsername == 'support':
        # edit_site, edit_server
        # ----------------------
        # Lets the user edit the content of config/localdat.py to edit a server
        # description, or change the server description in LOCALDATA['sitesinfo_path']
        # add_site_local adds a site description to the sites_local.py file
        if opts.edit_site or opts.edit_server:
            if opts.edit_site:
                handler.check_name(must_match=True)
            handler.edit_site_or_server()
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

    
def parse_args():
    argparse.ArgumentParser.set_default_subparser = set_default_subparser
    usage = ""

    # -----------------------------------------------
    # parent parser holds arguments, that are used for all subparsers 
    parent_parser = ArgumentParser(usage=usage, add_help=False)
    # set options for parent_parser
    add_options_parent(parent_parser)
    # parser_rpc is also used in several parsers to provide default values
    parser_rpc = ArgumentParser(add_help=False)
    # set options for parser_rpc
    add_options_rpc(parser_rpc)


    # parser is the main parser
    parser = ArgumentParser()
    subparser_help = """
    erp workbench provides commands to manage erp sites.
    These commands ares grouped into several groups of subcommands.
    use {SUBCOMMAND} --help to see the subcommans options.
    """
    subparsers = parser.add_subparsers(help=subparser_help)

    # -----------------------------------------------
    # create commands
    parser_manage = subparsers.add_parser(
        'create',
        help="""
        create is used to manage local and remote sites by reading 
        site descrition created using the sites command set
        """,
        parents=[parser_rpc, parent_parser],
        #prog='PROG',
        usage='%(prog)s [options]')
    # -----------------------------------------------
    # support commands
    parser_support = subparsers.add_parser(
        'support', 
        help="""
        support provides commands to handle site descriptions from which sites are constructed
        and other support commands.
        """, 
        parents=[parent_parser])
    add_options_support(parser_support)
    # -----------------------------------------------
    # manage docker
    parser_docker = subparsers.add_parser(
        'docker',
        help='docker provides commands to handle docker containers',
        parents=[parent_parser])
    # -----------------------------------------------
    # manage remote server (can be localhost)
    parser_remote = subparsers.add_parser(
        'remote',
        help='remote provides commands to manage elements of the remote server.',
        parents=[parent_parser])
    # -----------------------------------------------
    # manage mails
    parser_mail = subparsers.add_parser(
        'mail',
        help='mail provides commands to manage mail accounts.',
        parents=[parent_parser])

    # -----------------------------------------------
    # manage sites create and update sites
    # -----------------------------------------------
    #http://stackoverflow.com/questions/10448200/how-to-parse-multiple-sub-commands-using-python-argparse
    #parser_site_s = parser_site.add_subparsers(title='manage sites', dest="site_creation_commands")
    add_options_create(parser_manage)

    # -----------------------------------------------
    # support commands
    # -----------------------------------------------
    #parser_manage_s = parser_manage.add_subparsers(title='manage sites', dest="site_manage_commands")

    # -----------------------------------------------
    # manage docker
    # -----------------------------------------------
    #parser_support_s = parser_support.add_subparsers(title='docker commands', dest="docker_commands")
    parser_docker.add_argument(
        "-dassh", "--docker-add_ssh",
        action="store_true", dest="docker_add_ssh", default=False,
        help = 'add ssh to a docker container'
    )

    # -----------------------------------------------
    # manage remote server (can be localhost)
    # -----------------------------------------------
    #parser_docker_s = parser_docker.add_subparsers(title='remote commands', dest="remote_commands")
    parser_remote.add_argument(
        "--add-apache",
        action="store_true", dest="add_apache", default=False,
        help = 'add apache.conf to the apache configuration. Name must be provided'
    )
    # -----------------------------------------------
    # manage mails
    # -----------------------------------------------
    
    sub_parser = parser.set_default_subparser('create')
    args, unknownargs = parser.parse_known_args()
    command_line = ' '.join(sys.argv)
    args.command_line = command_line
    unknownargs = [a for a in unknownargs if a and a[0] != '-']
    if not args.name:
        if unknownargs:
            args.name = unknownargs[0]
        else:
            args.name = ''
    return args, sub_parser
    
    
    opts = OptsWrapper(args)
    opts.command_line = command_line # so we can reexecute
    if not opts.name and unknownargs:
        unknownargs = [a for a in unknownargs if a and a[0] != '-']
        if unknownargs:
            opts._o.__dict__['name'] = unknownargs[0]


if __name__ == '__main__':
    #print(banner)
    args, sub_parser_name = parse_args()


    #(opts, args) = parser.parse_args()

    # --------------------------------------------------------
    # set a marker, so we can check if any command was executed
    # --------------------------------------------------------
    did_run_a_command = False

    main(args, sub_parser_name) #opts.noinit, opts.initonly)

    if 0: #not did_run_a_command:
        print(bcolors.FAIL)
        print('*' * 80)
        print('it looks as if no valid comand was executed')
        print('*' * 80)
        print(bcolors.ENDC)
        
