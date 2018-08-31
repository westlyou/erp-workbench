#!bin/python
# -*- coding: utf-8 -*-
import mimetypes
from argparse import ArgumentParser

import odoorpc
import os

class OdooHandler(object):
    def __init__(self, opts):
        self.opts = opts
        odoo = odoorpc.ODOO(opts.host, port=opts.port)
        odoo.login(opts.dbname, opts.rpcuser, opts.rpcpw)
        self.odoo = odoo
        self.modules = odoo.env['ir.module.module']
        
    def list_installed(self):
        opts = self.opts
        modules = self.modules
        if opts.all:
            mlist = modules.search([('state', '=', 'installed')])
        else:
            mlist = modules.search([('state', '=', 'installed'), ('application', '=', True)])
        for mid in mlist:
            m = modules.browse(mid)
            print("'%s', # %s" % (m.name, m.shortdesc))


def main(opts):
    handler = OdooHandler(opts)
    handler.list_installed()


if __name__ == '__main__':
    usage = "insert_media_in_cms.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument("-a", "--all",
                        action="store_true", dest="all", default=False,
                        help="list all installed modules, not only applications")

    parser.add_argument("-H", "--host",
                        action="store", dest="host", default='localhost',
                        help="define host default localhost")

    parser.add_argument("-d", "--dbname",
                        action="store", dest="dbname", default='afbsdemo',
                        help="define host default ''")

    parser.add_argument("-U", "--rpcuser",
                        action="store", dest="rpcuser", default='admin',
                        help="define user to log into odoo default admin")

    parser.add_argument("-P", "--rpcpw",
                        action="store", dest="rpcpw", default='admin',
                        help="define password for odoo user default 'admin'")

    parser.add_argument("-PO", "--port",
                        action="store", dest="port", default=8069,
                        help="define rpc port default 8069")

    opts = parser.parse_args()
    main(opts)
