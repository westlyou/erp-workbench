# -*- encoding: utf-8 -*-


"""
>>> for gid in robert.groups_id:
...   print  gid.id, groups.browse(gid.id).full_name
... 
1 1 Administration / Configuration
 2 Administration / Access Rights
 3 Administration / Settings
 4 Human Resources / Employee
 8 Extra Rights / Technical Features
 9 Sales / See Own Leads
10 Sales / Manager
11 Other Extra Rights / Contact Creation
14 Lead Automation / User
15 Lead Automation / Manager
16 Sales / See all Leads
27 Accounting & Finance / Billing
28 Accounting & Finance / Accountant
29 Accounting & Finance / Adviser
35 Events / User
36 Events / Manager
38 Mass Mailing / User
41 Website / Editor
42 Website / Editor and Designer
48 Survey / User
49 Survey / Manager
50 group_afbs_extra_data
68 AFBS Membership public
71 CMS Management / CMS Manager
72 CMS Management / CMS Media Category Manager
 4 Human Resources / Employee
68 AFBS Membership public
82 Afbs_Workgroup / User
83 Afbs_Workgroup / Manager

>>> for gid in peter.groups_id:
...   print  gid.id, groups.browse(gid.id).full_name
... 
68 AFBS Membership public
11 Other Extra Rights / Contact Creation
4 Human Resources / Employee
82 Afbs_Workgroup / User


"""
BASE_GROUP_IDS = [4, 11, 68, 82]
AFBS_MANAGER = 83

# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes
def run(self, **kw_args):
    odoo = self.get_odoo()
    res_users = odoo.env['res.users']
    res_groups = odoo.env['res.groups']
    base_groups = res_groups.browse(BASE_GROUP_IDS)
    users = res_users.browse(res_users.search([]))
    for user in users:
        if AFBS_MANAGER in [gid.id for gid in user.groups_id]:
            print('manager:', user.name)
            continue
        print(user.name, user.groups_id, end=' ') 
        user.groups_id = base_groups
        print(user.groups_id)
    