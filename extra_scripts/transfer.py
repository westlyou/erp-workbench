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
    # get the start options that where passed to the calling script
    opts_orig_data = self.opts.__dict__['_OptsWrapper__d'].__dict__
    
    # make sure scripts run both run against a docker hosted site and a command line site
    site = self.sites[self.db_name]
    #port = self.rpcport
    dbname = self.db_name
    dbhost = 'localhost'
    dbuser = self.user
    dbpw = 'admin'    
    rpchost = 'localhost'
    rpcport = self.rpcport
    rpcuser = self.rpc_user
    rpcpw = 'admin'
    # we must distinguish if we rund against a docker container or not
    if getattr(self, 'docker_db_admin', None):
        dbhost = self.db_host # ip of the docker container
        dbuser = self.docker_db_admin
        dbpw   = self.docker_db_admin_pw
        rpchost = self.docker_rpc_host
        rpcuser = self.docker_rpc_user
        rpcport = self.docker_rpc_port
     
    #self.docker_rpc_port
    #'8072'
    #self.docker_db_admin
    #'odoo'
    #self.docker_rpc_user_pw
    #'AfbsDemo$77'
    #self.db_host
    #u'172.17.0.2'
    #self.docker_db_ip
    #u'172.17.0.2'
    
    # conn_string = "dbname='%s' user=%s host='%s' password='%s'" % (opts.dbname, opts.user,  opts.host, opts.pw)
    # nsp_data will be used to construct a namespace
    nsp_data = {
        'dbhost' : dbhost,
        'dbname' : dbname,
        'dbuser' : dbuser,
        'dbpw' : dbpw,
        'rpchost' : rpchost,
        'rpcport' : rpcport,
        'rpcuser' : rpcuser,
        'rpcpw' : self.rpc_pw,
        'create_workgroups' : False,
        'deletefrommapper' : False,
        'listmodules' : False,
        'transfersteps' : 'l:f:p:s:P:m:w:e',
        'copytestdata' : False,
        'verbose' : opts_orig_data.get('verbose', True),
        'aoi' : False,
        'data_home' : '%s/transfer_to_odoo' % self.sites_home,
        'list_old_ids' : False,
        'testmode' : False,        
    }
    # now collect parameter passed in the 'executescriptparameter' if any
    extra_params = opts_orig_data.get('executescriptparameter', '')
    if extra_params:
        extra_params = extra_params.split(',')
        for ep in extra_params:
            eps = ep.split('=')
            if len(eps) == 2:
                nsp_data[eps[0]] = eps[1]
                print('setting param:%s to %s' % ((eps[0], eps[1])))
            else:
                print('%s is not a valid parameter to transfer.py' % ep)
    # create a namespace object that will be used as opts in transfer.py run method
    opts = Namespace(**nsp_data)
    # now do the transfer    
    transfer.main(opts, odoo)
