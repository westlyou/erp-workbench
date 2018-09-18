from config import BASE_INFO
from utilities.parser_handler import ParserHandler

def add_options_rpc(parser, result_dic):
    """add options to the rpc parser
    
    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parser_rpc = ParserHandler(parser, result_dic)

    dbh_help = """
    on what host is the database running. default localhost
    if oddo is running in a docker host, this value should be
    calculated automatically
    """
    parser_rpc.add_argument("-dbh", "--dbhost",
                            action="store", dest="db_host", default='localhost',
                            help=dbh_help)
    parser_rpc.add_argument("-p", "--dbpw",
                            action="store", dest="db_password", default='admin',
                            help="the password to access the database. default 'admin'")
    parser_rpc.add_argument("-dbu", "--dbuser",
                            action="store", dest="db_user", default=BASE_INFO['db_user'],
                            help="define user to log into database default %s" % BASE_INFO['db_user'])
    parser_rpc.add_argument("-rpch", "--rpchost",
                            action="store", dest="rpc_host", default='localhost',
                            help="define where odoo runs and can be accessed trough the rpc api. Default localhost")
    parser_rpc.add_argument("-rpcu", "--rpcuser",
                            action="store", dest="rpc_user", default='admin',
                            help="the user used to acces the running odo server using the rpc api. Default admin")
    parser_rpc.add_argument("-P", "--rpcpw",
                            action="store", dest="rpc_password", default='admin',
                            help="define password for the user that accesses the running odoo server trough the rpc api. default 'admin'")
    parser_rpc.add_argument("-PO", "--port",
                            action="store", dest="rpc_port", default=8069,
                            help="define the port on which the odoo server that will be accessed using the rpc api. default 8069")


    