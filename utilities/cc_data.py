# -*- coding: utf-8 -*-
"""
        'name': fields.char('Name', select=True),
        'display_name': fields.function(_display_name, type='char', string='Name', store=_display_name_store_triggers, select=True),
        'date': fields.date('Date', select=1),
        'title': fields.many2one(', 'Title'),
        'parent_id': fields.many2one('res.partner', 'Related Company', select=True),
        'parent_name': fields.related('parent_id', 'name', type='char', readonly=True, string='Parent name'),
        'child_ids': fields.one2many('res.partner', 'parent_id', 'Contacts', domain=[('active','=',True)]), # force "active_test" domain to bypass _search() override
        'ref': fields.char('Internal Reference', select=1),
        'lang': fields.selection(_lang_get, 'Language',
            help="If the selected language is loaded in the system, all documents related to this contact will be printed in this language. If not, it will be English."),
        'tz': fields.selection(_tz_get,  'Timezone', size=64,
            help="The partner's timezone, used to output proper date and time values inside printed reports. "
                 "It is important to set a value for this field. You should use the same timezone "
                 "that is otherwise used to pick and render date and time values: your computer's timezone."),
        'tz_offset': fields.function(_get_tz_offset, type='char', size=5, string='Timezone offset', invisible=True),
        'user_id': fields.many2one('res.users', 'Salesperson', help='The internal user that is in charge of communicating with this contact if any.'),
        'vat': fields.char('TIN', help="Tax Identification Number. Fill it if the company is subjected to taxes. Used by the some of the legal statements."),
        'bank_ids': fields.one2many('res.partner.bank', 'partner_id', 'Banks'),
        'website': fields.char('Website', help="Website of Partner or Company"),
        'comment': fields.text('Notes'),
        'category_id': fields.many2many('res.partner.category', id1='partner_id', id2='category_id', string='Tags'),
        'credit_limit': fields.float(string='Credit Limit'),
        'barcode': fields.char('Barcode', oldname='ean13'),
        'active': fields.boolean('Active'),
        'customer': fields.boolean('Is a Customer', help="Check this box if this contact is a customer."),
        'supplier': fields.boolean('Is a Vendor', help="Check this box if this contact is a vendor. If it's not checked, purchase people will not see it when encoding a purchase order."),
        'employee': fields.boolean('Employee', help="Check this box if this contact is an Employee."),
        'function': fields.char('Job Position'),
        'type': fields.selection(
            [('contact', 'Contact'),
             ('invoice', 'Invoice address'),
             ('delivery', 'Shipping address'),
             ('other', 'Other address')], 'Address Type',
            help="Used to select automatically the right address according to the context in sales and purchases documents."),
        'street': fields.char('Street'),
        'street2': fields.char('Street2'),
        'zip': fields.char('Zip', size=24, change_default=True),
        'city': fields.char('City'),
        'state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
        'country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
        'email': fields.char('Email'),
        'phone': fields.char('Phone'),
        'fax': fields.char('Fax'),
        'mobile': fields.char('Mobile'),
        'birthdate': fields.char('Birthdate'),
        'is_company': fields.boolean(
            'Is a Company',
            help="Check if the contact is a company, otherwise it is a person"),
        'company_type': fields.selection(
            selection=[('person', 'Individual'),
                       ('company', 'Company')],
            string='Company Type',
            help='Technical field, used only to display a boolean using a radio '
                 'button. As for Odoo v9 RadioButton cannot be used on boolean '
                 'fields, this one serves as interface. Due to the old API '
                 'limitations with interface function field, we implement it '
                 'by hand instead of a true function field. When migrating to '
                 'the new API the code should be simplified. Changing the'
                 'company_type of a company contact into a company will not display'
                 'this contact as a company contact but as a standalone company.'),
        'use_parent_address': fields.boolean('Use Company Address', help="Select this if you want to set company's address information  for this contact"),
        'company_id': fields.many2one('res.company', 'Company', select=1),
        'color': fields.integer('Color Index'),
        'user_ids': fields.one2many('res.users', 'partner_id', 'Users', auto_join=True),
        'contact_address': fields.function(_address_display,  type='char', string='Complete Address'),

        # technical field used for managing commercial fields
        'commercial_partner_id': fields.function(_commercial_partner_id, type='many2one', relation='res.partner', string='Commercial Entity', store=_commercial_partner_store_triggers, index=True)
"""
DB_INFO = {
    'res.partner' :
    {
        'filter' : [('id', '>', 0)],
        # simple fields we just copy the values
        'simple_fields' : [
            'name',
            'display_name',
            'date',
            'parent_name',
            'ref',
            'lang',
            'tz',
            'tz_offset',
            'vat',
            'website',
            'comment',
            'credit_limit',
            'barcode',
            'active',
            'customer',
            'supplier',
            'employee',
            'function',
            'type',
            'street',
            'street2',
            'zip',
            'city',
            'email',
            'phone',
            'fax',
            'mobile',
            'birthdate',
            'is_company',
            'company_type',
            'use_parent_address',
            'color',
            'contact_address',
        ],
        'one2many_fields' : {
            'child_ids': ('res.partner', 'parent_id'),
            'bank_ids':('res.partner.bank', 'partner_id'),            
            'user_ids' : ('res.users', 'partner_id'),
        },
        'many2one_fields' : {
            'title' : ('res.partner.title','title'),
            'parent_id' : ('res.partner', 'id'),
            'state_id': ("res.country.state", "state"),
            'country_id': ('res.country', 'id'),
            'user_id': ('res.users', 'id'), # 'Salesperson'
            'company_id': ('res.company', 'id'), # 'Company'
        },
        'many2many_fields' : {
            'category_id': ('res.partner.category', 'partner_id', 'category_id'),
        }
    },
    'res.partner.category' : {
        'simple_fields' : [
            'active',
            'color',
            'complete_name',
            'name',
        ],
        'one2many_fields' : {
            'child_ids': ('res.partner.category', 'parent_id'),
        },
        'many2one_fields' : {
            'parent_id': ('res.partner.category', 'id'),
        },
        'many2many_fields' : {
            'partner_ids': ('res.partner', 'category_id', 'partner_id'),
        }
    },
    'res.bank' : {
        'simple_fields' : [
            'name',
            'street', 
            'street2', 
            'zip',
            'city',
            'email',
            'fax',
            'active',
            'bic',
        ],
        'many2one_fields' : {
            'state' : ('res.country.state', 'id'),
            'country' : ('res.country', 'id'),
        }
    },
    'res.country' : {
        'simple_fields' : [
            'name', 
            'code',
            'address_format',
            #'image', ??should we use it??
            'phone_code',
        ],
        'one2many_fields' : {
            'state_ids': ('res.country.state', 'country_id'),
        },
        'many2one_fields' : {
            'currency_id': ('res.currency', 'id'),
        },
        'many2many_fields' : {
            'country_group_ids': ('res.country.group', 'res_country_res_country_group_rel', 'res_country_id', 'res_country_group_id'),
        },
    },
    'res.country.state' : {
        'simple_fields' : [
            'name',
            'code',
        ],
        'many2one_fields' : {
            'country_id' : ('res.country', 'id'),            
        }
    },
    'res.partner.bank' : {
        'simple_fields' : [
            'acc_number',
            'sequence',
        ],
        'many2one_fields' : {
            'partner_id' : ('res.partner', 'id'),
            'bank_id' : ('res.bank', 'id'),
            'currency_id' : ('res.currency', 'id'),
            'company_id' : ('res.company', 'id')
        }
    },
    'res.partner.title' : {
        'simple_fields' : [
            'name',
            'shortcut',
        ] 
    },
    # res_users
    #_columns = {
        #'name': fields.char('Name', required=True, translate=True),
        #'users': fields.many2many('res.users', 'res_groups_users_rel', 'gid', 'uid', 'Users'),
        #'model_access': fields.one2many('ir.model.access', 'group_id', 'Access Controls', copy=True),
        #'rule_groups': fields.many2many('ir.rule', 'rule_group_rel',
            #'group_id', 'rule_group_id', 'Rules', domain=[('global', '=', False)]),
        #'menu_access': fields.many2many('ir.ui.menu', 'ir_ui_menu_group_rel', 'gid', 'menu_id', 'Access Menu'),
        #'view_access': fields.many2many('ir.ui.view', 'ir_ui_view_group_rel', 'group_id', 'view_id', 'Views'),
        #'comment' : fields.text('Comment', size=250, translate=True),
        #'category_id': fields.many2one('ir.module.category', 'Application', select=True),
        #'color': fields.integer('Color Index'),
        #'full_name': fields.function(_get_full_name, type='char', string='Group Name', fnct_search=_search_group),
        #'share': fields.boolean('Share Group',
                    #help="Group created to set access rights for sharing data with some users.")
    #}
    
    'res.users' : {
        'simple_fields' : [
            'name',
            'comment',
            'color',
            'share',
        ],
        'many2one_fields' : {
            'parent_id': ('res.partner.category', 'id'),
            'category_id': ('ir.module.category', 'id'),
        },
        'many2many_fields' : {
            'rule_groups': ('ir.rule', 'rule_group_rel', 'group_id', 'rule_group_id', 'Rules'),
            'users': ('res.users', 'res_groups_users_rel', 'gid', 'uid'),
            'menu_access': ('ir.ui.menu', 'ir_ui_menu_group_rel', 'gid', 'menu_id'),
            'view_access': ('ir.ui.view', 'ir_ui_view_group_rel', 'group_id', 'view_id'),
            'model_access': ('ir.model.access', 'group_id', 'Access Controls'),
        }
    },
    'ir.module.category' : {}, # do not handle it
    'ir.rule' : {},
    'ir.ui.view' : {},
    'ir.model.access' : {},
    'ir.ui.menu' : {},
    'res.currency' : {},
    'res.country.group' : {},
    'res.company' : {},

}
