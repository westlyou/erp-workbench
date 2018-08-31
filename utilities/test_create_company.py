# -*- coding: utf-8 -*-
import argparse
import os
import sys
import glob
import re
import odoorpc
sys.path.insert(0,'.')

class partnerHandler(object):
    
    def __init__(self, opts):
        self.opts = opts

        try:
            odoo = odoorpc.ODOO(opts.host, port=opts.port)
            odoo.login(opts.name, opts.user, opts.password)
            self.odoo = odoo
            self.partners = odoo.env['res.partner']
        except Exception as e:
            print('not logged into odoo')
            if not opts.name:
                print('no database name is defined. Use -n to do so')
            
    def rmt(self):
        # remove test entities
        items = self.partners.search([('name', 'ilike', 'test%')])
        for p in self.partners.browse(items):
            p.unlink()
        
        
    def crp(self):
        # create test partner
        tc = {
            'name' : 'test-company',
            'is_company' : 1,
        }
        tp = {
            'name' : 'test-person',
        }
        tp2 = {
            'name' : 'test-person with company parent_id',
        }
        tp3 = {
            'name' : 'test-person with person parent id',
        }
        c_id = self.partners.create(tc)

        tp['commercial_partner_id'] = c_id
        p_id = self.partners.create(tp)
    
        tp2['parent_id'] = c_id
        p2_id = self.partners.create(tp2)
        
    
        tp3['parent_id'] = p_id
        p3_id = self.partners.create(tp3)        

        print(c_id, p_id)
        
def main(opts):
    handler = partnerHandler(opts)
    handler.crp()
    handler.rmt()

if __name__ == '__main__':
    usage = "update partner records from excel sheet\n"
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument(
        "-n", "--name",
        action="store", dest="name", default='leanbi',
        help = 'name of the db to handle partners for'
    )
    parser.add_argument(
        "-u", "--user",
        action="store", dest="user", default = 'admin',
        help = 'odoo user'
    )
    parser.add_argument(
        "-p", "--password",
        action="store", dest="password", default = 'admin',
        help = 'odoo password. Default admin'
    )
    parser.add_argument(
        "-P", "--port",
        action="store", dest="port", default = 8069,
        help = 'odoo port'
    )
    parser.add_argument(
        "-H", "--host",
        action="store", dest="host", default = 'localhost',
        help = 'odoo host'
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help = 'be verbose'
    )

    args, unknownargs = parser.parse_known_args()
    # is there a valid option?
    main(args)
