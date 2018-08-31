# -*- encoding: utf-8 -*-

# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes
def run(self, **kw_args):
    odoo = self.get_odoo()
    print('we run with %s' % kw_args)
    res_users = odoo.env['res.users']
    res_partners = odoo.env['res.partner']
    domain_list = odoo.env['product.domain.list']
    users = res_users.search([])
    # prepare list of domains
    companies = res_partners.browse(res_partners.search([('is_company', '=', True), ('parent_id', '=', False)]))
    c_map = {}
    for c in companies:
        email = c.email
        if email:
            domain = email.split('@')[-1]
            c_map[domain] = c.id
    # find memberships that have not assigned owners
    for dl in domain_list.browse(domain_list.search([])):
        print('handling:', dl.domain_data, dl.partner_id)
        if not dl.partner_id:
            partner_id = c_map.get(dl.domain_data)
            if partner_id and partner_id > 1:
                dl.write({'partner_id' : partner_id})
            else:
                print(dl.domain_data, c_map.get(dl.domain_data))
        
    
