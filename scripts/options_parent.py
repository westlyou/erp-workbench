# all options that are added to the parent parser
# the parent parser gets incloded in some other also
# and provides common options

from config import BASE_PATH, BASE_INFO

def add_options_parent(parser):
    """add options to the create parser
    
    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parent_parser = parser

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
        "-q", "--quiet",
        action="store_true", dest="quiet", default=False,
        help="be quiet")
    parent_parser.add_argument(
        "-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="be verbose")

    parent_parser.add_argument(
        "-V", "--version",
        action="store", dest="odoo_version", default='12.0',
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
    # parent_parser.add_argument(
    #     "-skip", "--skipown",
    #     action="store", dest="skipown",
    #     help = 'provide a comma separated (no space) list of add ons to skip. used in conjuction with all.'
    # )
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
