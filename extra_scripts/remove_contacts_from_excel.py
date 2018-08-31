# -*- encoding: utf-8 -*-
"""
read contacts from excel file
for this to work ssh://git@gitlab.redcor.ch:10022/redcor-team/marketing.git
must be added as submodule
"""

from marketing.scripts import makeusers_rc

def run(self, **kw_args):
    try:
        odoo = self.get_odoo()
        partners = odoo.env['res.partner']
    except:
        print("Database is not running")
        
    handler = makeusers_rc.Handler(odoo=odoo)
    done = False
    partners = odoo.env['res.partner']
    
    while not done:
        pids = partners.search([('id', '>', 130), ('id', '<', 75190)], limit=1000)
        print(pids)
        if pids:
            handler.unlink_partner(pids)
        else:
            done = True

    print('>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<<')
 