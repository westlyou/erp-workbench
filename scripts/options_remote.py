from scripts.parser_handler import ParserHandler

def add_options_remote(parser, result_dic):
    """add options to the create parser

    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parser_remote = ParserHandler(parser, result_dic)

    parser_remote.add_argument(
        "--add-apache",
        action="store_true", dest="add_apache", default=False,
        help = 'add apache.conf to the apache configuration. Name must be provided',
        need_name = True,
        name_valid = True,
    )
    parser_remote.add_argument(
        "--add-nginx",
        action="store_true", dest="add_nginx", default=False,
        help = 'add configuration to the list of nginx configurations. Name must be provided',
        need_name = True,
        name_valid = True,
    )
    parser_remote.add_argument(
        "-cert", "--create-certificate",
        action="store", dest="create_certificate",
        help = 'create or update lets encrypt ssl certificate. Name must be provided',
        need_name = True,
        name_valid = True,
    )
