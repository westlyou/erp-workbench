# -*- encoding: utf-8 -*-
"""
set all partners to customers
"""

# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes
import sys, os
from scripts.bcolors import bcolors

def run(self, **kw_args):
    try:
        odoo = self.get_odoo()
        partners = odoo.env['res.partner']
    except:
        print("Database is not running")
    
    
    # second last argument must be name of the newslist
    print(kw_args)
    args = sys.argv
    n_name = kw_args.get('name','')
    n_file = kw_args.get('path','')
    # rpath is optional, if it exists, emails found there are removed from the email list
    # either path or rpath has to exist
    r_file = kw_args.get('rpath','')
    
    nl_id = odoo.env['mail.mass_mailing.list'].search([('name', '=', n_name)])
    if not nl_id:
        print(bcolors.FAIL)
        print('mailing-list %s does not exist' % n_name)
        print('run bin/c -E import_nl_email SITE-NAME -EP name=NL_NAME,path=PATH-TO-DATA')
        print(bcolors.ENDC)
        return
    else:
        nl_id = nl_id[0]
    
    if not (os.path.exists(n_file) or os.path.exists(r_file)):
        print(bcolors.FAIL)
        print('datafile %s does not exist' % n_file)
        print('run bin/c -E import_nl_email SITE-NAME -EP name=NL_NAME,path=PATH-TO-DATA')
        print(' -OR- ')
        print('run bin/c -E import_nl_email SITE-NAME -EP name=NL_NAME,rpath=PATH-TO-DATA')
        print('in the second case, the emails found in rpath are REMOVED from the email list')
        print(bcolors.ENDC)
        return
    
    contacts = odoo.env['mail.mass_mailing.contact']
    if r_file:
        with open(r_file) as f: 
            lines = f.readlines()
        for email in lines:
            if not (email and ('@' in email)):
                continue
            email = email.split(',')[0].strip()
            l_object = contacts.search([('email', '=', email), ('list_id', '=', nl_id)])
            
            if l_object:
                contacts.browse(l_object).unlink()
                print('removed:', email)
    else:
        with open(n_file) as f: 
            lines = f.readlines()
        for email in lines:
            email = email.split(',')[0].strip()
            if email and not contacts.search([('email', '=', email), ('list_id', '=', nl_id)]) and ('@' in email):
                contacts.create({'email' : email, 'list_id' : nl_id})
                print(email)
                
        
    
        
    
    