# -*- encoding: utf-8 -*-
"""
transfer.py
this is a wrapper around transfer_to_odoo.transfer
it collects data from the old afbs database and transfers it to odoo
"""
from transfer_to_odoo.scripts import transfer

# construc dummy argparse
class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes
def run(self, **kw_args):
    odoo = self.get_odoo()
    #self.site_name
    #'afbschweiz'
    #self.user
    #'robert'
    #self.db_name
    #'afbschweiz'
    #self.db_password
    #'admin'
    #self.db_user
    #'robert'
    #opts.dbname, opts.user,  opts.host, opts.pw
    #(False, False, False, False)
    #self.dbhost
    #'localhost'
    
    print('we run with %s' % kw_args)
    opts = Namespace(
        host = self.dbhost,
        dbname = self.db_name,
        user = self.db_user,
        rpcuser = self.user,
        pw = self.db_password,
        rpcpw = self.rpc_pw,
        testmode = kw_args.get('testmode'),        
        rpchost = 'localhost',
        create_workgroups = False,
        deletefrommapper = False,
        listmodules = False,
        transfersteps = 'l:f:p:s:P:m:w:e',
        copytestdata = False,
        port = self.rpcport,
        verbose = True,
        aoi = False,
        data_home = '%s/transfer_to_odoo' % self.sites_home,
        list_old_ids = True,
    )
    transfer.main(opts, odoo)
