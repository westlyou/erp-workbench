# -*- encoding: utf-8 -*-
import xlwt
import os
file_path = os.path.expanduser('~/afbs_user_list.xls')

"""


"""
BASE_GROUP_IDS = [4, 11, 68, 82]
AFBS_MANAGER = 83
ID_COL = 0
OID_COL = 1
MAIN_COL = 2
BRANCH_COL = 3
PERS_COL = 4
MEMBER_COL = 5
STAFF_COL = 6
EMAIL_COL = 7
HEADER_LINE = ['id', 'old_id','Hauptsitz', 'Filiale', 'Mitarbeiter/in', 'Mitgliedschaft', 'Staff', 'email']

# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes
def run(self, **kw_args):
    odoo = self.get_odoo()
    # some fonts
    font0 = xlwt.Font()
    font0.name = 'Helvetica'
    font0.colour_index = 2
    font0.bold = True    
    st_bold = xlwt.XFStyle()
    st_bold.font = font0  
    
    # check whether there is already the output file, if yes, delete it
    if os.path.exists(file_path):
        os.unlink(file_path)
    # create ne workbook
    wb = xlwt.Workbook()    
    # create a new sheet
    new_sheet = wb.add_sheet('memberlist')
    # write header
    c_index = 0
    for f in HEADER_LINE:
        new_sheet.write(0, c_index, f)
        c_index += 1
    
    # get all odoo objects
    partners = odoo.env['res.partner']
    res_users = odoo.env['res.users']
    res_groups = odoo.env['res.groups']
    # product.name, product.domain_list
    products = odoo.env['product.template']
    product_domains = odoo.env['product.domain.list']
    #p=product_domains.browse(56)
    #pd=p.partner_dom[0]
    #pd.name
    base_groups = res_groups.browse(BASE_GROUP_IDS)
    users = res_users.browse(res_users.search([]))
    # keep a list of handled id's
    seen_ids = {}
    seen_domains = {}
    line_counter = 0
    #run trough all partner
    #for partner in partners:
    # we start with companies not having a parent
    main_companies = partners.search([('is_company','=', True), ('parent_id', '=', False)], order='name')
    for cm in partners.browse(main_companies):
        line_counter += 1
        # write ids's name
        c_index = 0
        seen_ids[cm.id] = 1
        for f in [cm.id, cm.old_id, cm.name]:
            new_sheet.write(line_counter, c_index, f, st_bold)
            c_index += 1
        # collect membership data
        # there could be more than one domain per company
        # if this is the case, we have to advance
        domains = product_domains.search([('partner_id','=', cm.id)])
        if domains:
            d_counter = 0
            for dom in product_domains.browse(domains):
                if d_counter:
                    line_counter += 1
                d_counter += 1
                # collect the name of the product. this is the name of the membership
                membership_name = products.browse(dom.partner_dom.id).name
                new_sheet.write(line_counter, MEMBER_COL, membership_name, st_bold)
                new_sheet.write(line_counter, EMAIL_COL, 'DOMAIN: %s' % dom.domain_data, st_bold)
                
        # now collect persons of this company
        employees = partners.search([('is_company','=', False), ('parent_id', '=', cm.id)], order='name')
        c_index = PERS_COL
        for emp in partners.browse(employees):
            seen_ids[emp.id] = 1
            line_counter += 1
            new_sheet.write(line_counter, c_index, emp.name)
            new_sheet.write(line_counter, ID_COL, emp.id)
            new_sheet.write(line_counter, OID_COL, emp.old_id)
            new_sheet.write(line_counter, EMAIL_COL, emp.email)
            # to know whether a user is assigned to the employee
            # we have to loock it up in res.users
            user = res_users.search([('partner_id','=', emp.id)])
            if user:
                uo = res_users.browse(user[0])
                if AFBS_MANAGER in [gid.id for gid in uo.groups_id]:
                    new_sheet.write(line_counter, STAFF_COL, 'staff')
                else:
                    new_sheet.write(line_counter, STAFF_COL, 'user')

        # now repeat everything with the branches
        print(cm.id, cm.name)
        branches = partners.search([('is_company','=', True), ('parent_id', '=', cm.id)], order='name')
        for bm in partners.browse(branches):
            line_counter += 1
            # write ids's name
            c_index = 0
            seen_ids[bm.id] = 1
            for f in [bm.id, bm.old_id]:#, bm.name]:
                new_sheet.write(line_counter, c_index, f)
                c_index += 1
            new_sheet.write(line_counter, BRANCH_COL, bm.name)
            new_sheet.write(line_counter, EMAIL_COL, bm.email)
            # now collect persons of this company
            employees = partners.search([('is_company','=', False), ('parent_id', '=', bm.id)], order='name')
            c_index = PERS_COL
            for emp in partners.browse(employees):
                seen_ids[emp.id] = 1
                line_counter += 1
                new_sheet.write(line_counter, c_index, emp.name)
                new_sheet.write(line_counter, ID_COL, emp.id)
                new_sheet.write(line_counter, OID_COL, emp.old_id)
                new_sheet.write(line_counter, EMAIL_COL, emp.email)
                # to know whether a user is assigned to the employee
                # we have to loock it up in res.users
                user = res_users.search([('partner_id','=', emp.id)])
                if user:
                    uo = res_users.browse(user[0])
                    if AFBS_MANAGER in [gid.id for gid in uo.groups_id]:
                        new_sheet.write(line_counter, STAFF_COL, 'staff')
                    else:
                        new_sheet.write(line_counter, STAFF_COL, 'user')
            # now repeat everything for the branches
            print('branch', bm.id, bm.name)
    # now collect all partners we have not seen yet
    line_counter += 2
    new_sheet.write(line_counter, MAIN_COL, 'Nicht zugeordnete Partner')
    line_counter += 1            
    new_sheet.write(line_counter, MAIN_COL, '-------------------------')
    seen = list(seen_ids.keys())
    not_seen = [p for p in partners.search([]) if p not in seen]
    for ns in partners.browse(not_seen):
        line_counter += 1
        c_index = 0
        for f in [ns.id, ns.old_id, ns.name]:
            new_sheet.write(line_counter, c_index, f)
            c_index += 1
        # to know whether a user is assigned to the employee
        # we have to loock it up in res.users
        user = res_users.search([('partner_id','=', ns.id)])
        if user:
            uo = res_users.browse(user[0])
            if AFBS_MANAGER in [gid.id for gid in uo.groups_id]:
                new_sheet.write(line_counter, STAFF_COL, 'staff')
            else:
                new_sheet.write(line_counter, STAFF_COL, 'user')

        new_sheet.write(line_counter, EMAIL_COL, ns.email)
        # collect membership data
        # there could be more than one domain per company
        # if this is the case, we have to advance
        domains = product_domains.search([('partner_id','=', ns.id)])
        if domains:
            d_counter = 0
            for dom in product_domains.browse(domains):
                if d_counter:
                    line_counter += 1
                d_counter += 1
                # collect the name of the product. this is the name of the membership
                membership_name = products.browse(dom.partner_dom.id).name
                new_sheet.write(line_counter, MEMBER_COL, membership_name)
        
    
    wb.save(file_path)    
    #for user in users:
        #if AFBS_MANAGER in [gid.id for gid in user.groups_id]:
            #print 'manager:', user.name
            #continue
        #print user.name, user.groups_id, 
        #user.groups_id = base_groups
        #print user.groups_id
    