#!/usr/bin/env python
# -*- coding: utf-8 -*-
# make sure we are in a virtualenv
import os, sys, time
# robert: i usualy thest in wingide
if not os.environ.get('VIRTUAL_ENV') and not os.environ.get('WINGDB_ACTIVE'):
    print('not running in a virtualenv')
    print('activate the worbench environment executing:')
    print('workon workbench')
    sys.exit()
from argparse import RawTextHelpFormatter, ArgumentParser
import readline, glob
import subprocess
#import xml.dom.minidom
import re
import argparse
import argcomplete

try:
    from scripts.bcolors import bcolors
except ImportError:
    sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])

from scripts.bcolors import bcolors
from scripts.banner import BANNER_HEAD, BANNER_TEXT

from scripts.messages import *

from scripts.utilities import create_server_config, checkout_sa, list_sites

try:
    from config import SITES, SITES_LOCAL
except ImportError:
    from config import sites_handler
    sites_handler.check_and_create_sites_repo()
    from config import SITES, SITES_LOCAL
    
from config import ACT_USER, BASE_PATH, FOLDERNAMES, \
    BASE_INFO, MARKER, LOGIN_INFO_FILE_TEMPLATE, \
    REQUIREMENTS_FILE_TEMPLATE, DOCKER_DEFAULTS

from config.handlers import SiteCreator
from config.handlers import DockerHandler
from config.handlers import SupportHandler
from config.handlers import RemoteHandler
from config.handlers import MailHandler

# get config options
from scripts.options_create import add_options_create
from scripts.options_docker import add_options_docker
from scripts.options_parent import add_options_parent
from scripts.options_rpc import add_options_rpc
from scripts.options_support import add_options_support
from scripts.options_remote import add_options_remote
from scripts.options_mail import add_options_mail

banner = bcolors.red + BANNER_HEAD  + bcolors.normal + BANNER_TEXT

#ascii art by: Cara Pearson
colors = bcolors

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



def main(opts, parsername, need_names_dic):
    """
    """
    # default_handler = SiteCreator
    try:
        import wingdbstub
    except:
        pass
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


    # ckeck whether the used option needs a name to work
    handler.check_name(need_names_dic=need_names_dic)

    # ----------------------
    # create commands
    # ----------------------
    if parsername == 'create':

        # create
        # ------
        # builds or updates a server structure
        # to do so, it does a number of steps
        #   - creates the needed folders in $ERP_SERVER_DATA
        #   - creates a build structure in $PROJECT_HOME/$SITENAME/$SITENAME
        #     where $PROJECT_HOME is read from the config file.
        #   - copies and sets up all files from skeleton directory to the build structure
        #     this is done executing create_new_project and do_copy
        #   - builds a virtualenv environment in the build structure
        #   - prepares to builds an erp server within the build structure by
        #     execution  bin/build_erp within the build structure.
        #     Within this bild environment the erp's module path will be set
        #     that it points to the usual erp-workbench directories within the build substructure
        #     and also to the directories within erp_workbench as dictated by the
        #     various modules installed from interpreting the site declaration
        #     in sites.py
        #   - add a "private" addons folder within the build structure called
        #     $SITENAME_addons. This folder is also added to the erp-site's addon path.
        #   - set the data_dir to point to $ERP_SERVER_DATA/$SITENAME/filestore
        #
        # modules_update
        # -------------
        if opts.create  or opts.modules_update or opts.module_update:
            info_dic = {
                'project_path' : handler.default_values['inner'],
                'erp_version' : BASE_INFO.get('erp_version'),
                'site_name' : handler.site_name
            }
            if opts.create:
                existed = handler.create_or_update_site()
                if existed:
                    if not opts.quiet:
                        print()
                        print('%s site allredy existed' % handler.site_name)
                        print(SITE_EXISTED % info_dic)
                else:
                    if handler.site_name:
                        if not opts.quiet:
                            print()
                            print('%s site created' % handler.site_name)
                            print(SITE_NEW % info_dic)
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
            list_sites(SITES, opts.quiet)
            did_run_a_command = True
            return
        
        # delete_site_local
        # --------
        # delete_site_local removes a site and all project files
        if opts.delete_site_local:
            handler.delete_site_local()
            did_run_a_command = True
            return

    # ----------------------
    # docker commands
    # ----------------------
    if parsername == 'docker':
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
            handler.check_and_create_container(container_name='db')
            did_run_a_command = True

        # build image
        # ----------
        # build docker image used by a site
        if opts.docker_build_image:
            handler.build_image()
            did_run_a_command = True
            return

    # ----------------------
    # support commands
    # ----------------------
    if parsername == 'support':
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

        # edit_site, edit_server
        # ----------------------
        # Lets the user edit the content of config/localdat.py to edit a server
        # description, or change the server description in LOCALDATA['sitesinfo_path']
        if opts.edit_site or opts.edit_server:
            if opts.edit_site:
                handler.check_name(must_match=True)
            handler.edit_site_or_server()
            did_run_a_command = True
            return

    
def parse_args():
    argparse.ArgumentParser.set_default_subparser = set_default_subparser
    usage = ""
    need_names_dic = {
        'need_name' : [], # we need a name
        'name_valid': [], # given name must be valid  
    }
    # -----------------------------------------------
    # parent parser holds arguments, that are used for all subparsers 
    parent_parser = ArgumentParser(usage=usage, add_help=False)
    # set options for parent_parser
    add_options_parent(parent_parser, need_names_dic)
    # parser_rpc is also used in several parsers to provide default values
    parser_rpc = ArgumentParser(add_help=False)
    # set options for parser_rpc
    add_options_rpc(parser_rpc, need_names_dic)


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
    add_options_support(parser_support, need_names_dic)
    # -----------------------------------------------
    # manage docker
    parser_docker = subparsers.add_parser(
        'docker',
        help='docker provides commands to handle docker containers',
        parents=[parent_parser])
    add_options_docker(parser_docker, need_names_dic)
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
    add_options_mail(parser_mail, need_names_dic)

    # -----------------------------------------------
    # manage sites create and update sites
    # -----------------------------------------------
    #http://stackoverflow.com/questions/10448200/how-to-parse-multiple-sub-commands-using-python-argparse
    #parser_site_s = parser_site.add_subparsers(title='manage sites', dest="site_creation_commands")
    add_options_create(parser_manage, need_names_dic)
    # -----------------------------------------------
    # manage remote server (can be localhost)
    # -----------------------------------------------
    add_options_remote(parser_remote, need_names_dic)
    
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
    return args, sub_parser, need_names_dic
    
    
    opts = OptsWrapper(args)
    opts.command_line = command_line # so we can reexecute
    if not opts.name and unknownargs:
        unknownargs = [a for a in unknownargs if a and a[0] != '-']
        if unknownargs:
            opts._o.__dict__['name'] = unknownargs[0]


if __name__ == '__main__':
    #print(banner)
    args, sub_parser_name, need_names_dic = parse_args()


    #(opts, args) = parser.parse_args()

    # --------------------------------------------------------
    # set a marker, so we can check if any command was executed
    # --------------------------------------------------------
    did_run_a_command = False

    main(args, sub_parser_name, need_names_dic) #opts.noinit, opts.initonly)

    if 0: #not did_run_a_command:
        print(bcolors.FAIL)
        print('*' * 80)
        print('it looks as if no valid comand was executed')
        print('*' * 80)
        print(bcolors.ENDC)
        
