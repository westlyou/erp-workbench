# -*- encoding: utf-8 -*-
"""
set all partners to customers
"""

# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes


def run(self, **kw_args):
    try:
        odoo = self.get_odoo()
        partners = odoo.env['res.partner']
    except:
        print("Database is not running")
    counter = 0
    counter2 = 0
    partner = ""
    for ps in partners.search([]):
        counter2 += 1
        print(counter2)
        print(partner)
        print(partners)
        partner = partners.browse(ps)
        if not partner.customer:
            partner.write({'customer' : True})
            counter += 1
    print("")
    print("===================================")
    print(counter)
    print("Changed partner records customer to true")
    print("===================================")
    print("")
