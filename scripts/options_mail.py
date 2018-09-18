from scripts.parser_handler import ParserHandler

def add_options_mail(parser, result_dic):
    """add options to the create parser

    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parser_mail = ParserHandler(parser, result_dic)

    parser_mail.add_argument(
        "-mm", "--manage_mail",
        action="store_true", dest="manage_mail", default=False,
        help='manage mail seting. Name must be provided'
    )
