#!/usr/bin/env python
#import argparse
from argparse import ArgumentParser
#import argcomplete
usage = 'holderihoo'
# -----------------------------------------------
# parent parser holds arguments, that are used for all subparsers 
parent_parser = ArgumentParser(usage=usage, add_help=False)
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


parser_rpc = ArgumentParser(add_help=False)
parser = ArgumentParser()#add_help=False)# ArgumentParser(usage=usage)
subparsers = parser.add_subparsers(help='commands')
#parser.add_argument('--help', action=_HelpAction, help='help for help if you need some help')  # add custom help
#parser_s = parser.add_subparsers(title='subcommands', dest="subparser_name")


# support commands
parser_support= subparsers.add_parser('support', help='the option -sites --support has the following subcommands', parents=[parent_parser])
# -----------------------------------------------
# manage docker
parser_docker = subparsers.add_parser(
    'docker',
    help='the option --docker has the following subcommands',
    parents=[parent_parser])
# -----------------------------------------------
# manage remote server (can be localhost)
parser_remote = subparsers.add_parser(
    'remote',
    help='the command remote is used to manage the remote server.',
    parents=[parent_parser])
# -----------------------------------------------
# manage mails
parser_mail = subparsers.add_parser(
    'mail',
    help='the command mail is used to manage mails.',
    parents=[parent_parser])

print(parser.parse_args())
