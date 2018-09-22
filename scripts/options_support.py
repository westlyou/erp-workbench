# all options that are added to the parent parser
# the parent parser gets incloded in some other also
# and provides common options

from config import BASE_PATH, BASE_INFO
from scripts.parser_handler import ParserHandler

def add_options_support(parser, result_dic):
    """add options to the create parser

    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parser_support = ParserHandler(parser, result_dic)

    parser_support.add_argument(
        "--add-site",
        action="store_true", dest="add_site", default=False,
        help='add site description to sites.py from template. Name must be provided',
        need_name=True
    )
    parser_support.add_argument(
        "--add-site-local",
        action="store_true", dest="add_site_local", default=False,
        help='add site description to sites_local.py from template. Name must be provided',
        need_name=True
    )
    parser_support.add_argument(
        "--drop-site",
        action="store_true", dest="drop_site", default=False,
        help='drop site description from sites.py. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_support.add_argument(
        "--add-server",
        action="store", dest="add_server",
        help='add server to config/servers.yaml. server ip and user must be provided in the form user@server_ip',
    )
    parser_support.add_argument(
        "--docker-port",
        action="store", dest="docker_port",
        help='provide docker port to new server.  To ckeck for availability use option -lp --list-port'
    )
    parser_support.add_argument(
        "--remote-server",
        action="store", dest="remote_server",
        help='provide docker post to new server.  To ckeck for availability use option -lp --list-port'
    )
    parser_support.add_argument(
        "--edit-site",
        action="store_true", dest="edit_site", default=False,
        help='edit site. name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_support.add_argument(
        "--edit-site-preset",
        action="store_true", dest="edit_site_preset", default=False,
        help='edit preset values for site. name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_support.add_argument(
        "--edit-server",
        action="store_true", dest="edit_server", default=False,
        help='edit local data with server info',
        need_name=True,
        name_valid=True,
    )
    parser_support.add_argument(
        "-a", "--alias",
        action="store_true", dest="alias", default=False,
        help='add project site structure to aliases. create site will run this automatically'
    )
    parser_support.add_argument(
        "-lp",
        action="store_true", dest="list_ports", default=False,
        help='list ports used, grouped by server'
    )
    parser_support.add_argument(
        "--upgrade",
        action="store", dest="upgrade",
        help='upgrade site to a new erp version. Please indicate the name of the new site. The the target version will be read from its site description',
        need_name=True,
        name_valid=True,
    )
    # parser_support.add_argument(
    #     "-show",
    #     action="store_true", dest="show", default=False,
    #     help='show configure settings.'
    # )
    # parser_support.add_argument(
    #     "-set", "--set-config",
    #     action="store", dest="set_config",
    #     help='provide a comma separated (no space) list of key=value pairs to set in the config. if the value is --, the key is removed'
    # )

