#!bin/python
# -*- coding: utf-8 -*-
import mimetypes
from argparse import ArgumentParser
import configparser
import sys
import os
import odoorpc
from datetime import date

sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
class bcolors:
    """
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    
"""
copy site site is a simple attempt to copy a v 9 to v 10 site, without trying 
to create a 1:1 copy

what is to be copied is handcrafted, and needs to be adapted from site to site
"""  
MODELS = [
    'account.journal',
    'product.product',
    'product.template',
    'res.partner',
    'res.user',
    'res.company',
    'res.lang',
    'res.groups',
    'res.partner.title',
    'res.partner.bank',
    'res.partner.category',
    'mail.mass_mailing.list',
    'mail.mass_mailing.contact',
    'membership.membership_line',
]
base_def = {
        'tz' : 'Europe/Zurich',
        'lang' : 'de_CH',
    }
DEFAULTS = {
    'res.partner' : base_def,
    'res.user' : base_def,
    'res.company' : base_def,
    'res.lang' : {},
    'res.groups' : {},
    'res.partner.title' : {},
    'res.partner.bank' : {},
    'res.partner.category' : {},
}       


class Source(object):
    host = 'localhost'
    #db = 'breitschtraeff92'
    db = 'redcorkmu'
    user = 'admin'
    pw = 'admin' #'BreitschTraeffOnFrieda'
    port = 8070

class Target(object):
    host = 'localhost'
    #db = 'breitschtraeff10'
    db = 'redo2oo'
    user = 'admin'
    pw = 'admin'
    port = 8069

class Handler(object):
    # map of objects
    omap = {
        'res.users'   : {},
        'res.partner' : {},
    }
    #user_map = {}
    #partner_map = {}
    #title_map = {}
    mapped_emails = []
    mapped_names  = []
    map_only = False
    done_cache = {} # do not copy things twice
    
    def __init__(self):
        self.update = True # should be option
        self.sodoo, self.source = self._open(Source)
        self.todoo, self.target = self._open(Target)
        self.sodoo.env.context['lang'] = 'en_US'
        self.todoo.env.context['lang'] = 'en_US'
        self.mapper = self.todoo.env['afbs_import_mapper']
        self.build_mapper(MODELS)
        
    def _open(self, klass):
        s = klass()
        try:
            odoo = odoorpc.ODOO(s.host, port=s.port, timeout=1200)
            #login(self, db, login='admin', password='admin'
            odoo.login(s.db, s.user, s.pw)
        except:
            print(bcolors.FAIL)
            print('*' * 80)
            print('could not execute: odoorpc.ODOO(%s, port=%s, timeout=1200)' % (s.host, s.port))
            print('followed by:')
            print('login(%s, "%s", "%s")' % (s.db, s.user, s.pw))
            print('*' * 80 + bcolors.ENDC)
            sys.exit()
        finally:
            print(bcolors.ENDC)
        return odoo, s
    
    def _get_modules(self, module_name):
        return self.sodoo.env[module_name], self.todoo.env[module_name]
    
    def  _fix_date(self, dtm):
        # dates are stored as strings
        if dtm:
            try:
                return dtm.strftime('%Y/%m/%d')
            except AttributeError:
                return False
    
    def _validate_and_fix_partner_data(self, data):
        # clean partnerdata
        # for the time being we only fix the country id of swizerland from 254 to 44
        country = data.get('country_id')
        if country:
            data['country_id'] = 44
            
    def mapper_add(self, model, old_id, new_id):
        # is old id allready mapped
        # the map of existing elements is created at startup
        page = self.omap[model]
        m = page.get(old_id)
        if m:
            return m
        else:
            data = {
                'old_id' : old_id,
                'new_id' : new_id,
                'old_dbname' : model,
            }
            self.mapper.create(data)
            page[old_id] = new_id
        return new_id
            
    def mapper_get(self, model, old_id):
        # is old id allready mapped
        page = self.omap[model]
        new_id = page.get(str(old_id))
        try:
            new_id = int(new_id)
        except (ValueError, TypeError):
            pass
        return new_id
            
    
    def build_mapper(self, models):
        # build omap from target
        for m in MODELS:
            self.omap[m] = {}
            self.done_cache[m] = {}
        mapper_elements = self.mapper.browse(self.mapper.search([]))
        for me in mapper_elements:
            model = me.old_dbname
            #o_mapper_page = self.omap.get(model, {})
            #o_mapper_page[me.old_id] = me.new_id
            self.omap[model][me.old_id] = me.new_id
        
    #def _set_omaps(self, oo, no, type='user'):
        #if type == 'user':
            #partner = no.partner_id
            #self.omap['res.users'][no.id] = {
                #'name' : no.name, 
                #'partner' : partner.id, 
                #'login' : no.login,
                #'old_id': oo.id,
            #}
            ## kep map old-new user
            #self.user_map[oo.id] = no.id
            #self.omap['res.partner'][partner.id] = {
                #'user' : no.id,
                ## the id of the 
                #'old_id' : oo.partner_id[0].id
            #}
            ## kep map old-new partner
            #self.partner_map[oo.partner_id.id] = partner.id
        #if type == 'partner':
            #self.omap['res.partner'][no.id] = {
                #'user' : None,
                ## the id of the 
                #'old_id' : oo.id
            #}
            ## kep map old-new partner
            #self.partner_map[oo.id] = no.id
            
    #def _get_last_website(self, old_id):
        #return old_id
        #raise ValueError('not implemented')
            
    def _get_team(self, old_id):
        # the team hopefully has not changed
        return old_id
            
    def _get_company(self, old_id):
        # the team hopefully has not changed
        return old_id
            
    def _copy_partner_to_partner(self, s_partner, t_partner, sm, tm):
        """
        copy old partner to new partner
        both objects must exist
        also all dependend objects must exist on the target
        s_partner: res.partner object
            source object
        t_partner: res.partner object
            target object
            
        returns:
           id of new partner
        """
        model='res.partner'
        
        if isinstance(s_partner, int):
            s_partner = sm.browse([s_partner])
        
        if isinstance(t_partner, int):
            t_partner = tm.browse([t_partner])
            
        data = {
            'name' : s_partner.name,
            'comment' : s_partner.comment,
            #'create_date' : s_partner.create_date,
            'color' : s_partner.color,
            'company_type' : s_partner.company_type,
            #'date' : s_partner.date,
            'street' : s_partner.street,
            'city' : s_partner.city,
            #'display_name' : s_partner.display_name,
            'zip' : s_partner.zip,
            'supplier' : s_partner.supplier,
            'ref' : s_partner.ref,
            'email' : s_partner.email,
            'is_company' : s_partner.is_company,
            'website' : s_partner.website,
            'customer' : s_partner.customer,
            'fax' : s_partner.fax,
            'street2' : s_partner.street2,
            'barcode' : s_partner.barcode,
            'employee' : s_partner.employee,
            'credit_limit' : s_partner.credit_limit,
            #'write_date' : s_partner.write_date,
            'active' : s_partner.active,
            'tz' : 'Europe/Zurich', #s_partner.tz,
            #'write_uid' : s_partner.write_uid,
            'lang' : 'de_CH', #s_partner.lang,
            #'create_uid' : s_partner.create_uid,
            'phone' : s_partner.phone,
            'mobile' : s_partner.mobile,
            'type' : s_partner.type,
            'use_parent_address' : s_partner.use_parent_address,
            #'user_id' : s_partner.user_id,
            'birthdate' : s_partner.birthdate,
            'vat' : s_partner.vat,
            'notify_email' : s_partner.notify_email,
            'message_last_post' : s_partner.message_last_post,
            'opt_out' : s_partner.opt_out,
            #'signup_type' : s_partner.signup_type,
            #'signup_expiration' : s_partner.signup_expiration,
            #'signup_token' : s_partner.signup_token,
            #'calendar_last_notif_ack' : s_partner.calendar_last_notif_ack,
            'website_meta_title' : s_partner.website_meta_title,
            'website_meta_description' : s_partner.website_meta_description,
            'website_meta_keywords' : s_partner.website_meta_keywords,
            'website_short_description' : s_partner.website_short_description,
            'website_published' : s_partner.website_published,
            'website_description' : s_partner.website_description,
            'debit_limit' : s_partner.debit_limit,            
            #'lastname' : s_partner.lastname,
            #'firstname' : s_partner.firstname,
            #'zip_id' : s_partner.zip_id,
        }
        # handle membership
        # 'last_time_entries_checked' : s_partner.last_time_entries_checked,
        if COPY_MEMBERSHIP:
            trigger = MEMBERSHIP_ITEMS['trigger']
            if hasattr(s_partner, trigger) and getattr(s_partner, trigger) and getattr(s_partner, trigger) != 'none':   
                for elem in MEMBERSHIP_ITEMS['copy']:
                    if hasattr(s_partner, elem):
                        v = getattr(s_partner, elem)
                        if isinstance(v, date):
                            v = v.strftime('%Y/%m/%d')
            if s_partner.associate_member:
                tmp_id = s_partner.associate_member.id
                if tmp_id:
                    data['associate_member'] = self.get_new_partner(tmp_id, sm, tm)

            if s_partner.assigned_partner_id:
                tmp_id = s_partner.assigned_partner_id.id
                if tmp_id:
                    data['assigned_partner_id'] = assigned_partner_id

        #if s_partner.last_website_so_id:
            #tmp_id = s_partner.associate_member.id
            #if tmp_id:
                #data['last_website_so_id'] = self._get_last_website(tmp_id)
        #if s_partner.activation:
            ## this will allways die
            #raise ValueError('not implemented')
            #tmp_id = s_partner.activation
            #if tmp_id:
                #data['activation'] =_partner.activation.id
        #if s_partner.grade_id:
            #raise ValueError('not implemented')
            #tmp_id = s_partner.grade_id.id
            #if tmp_id:
                #data['grade_id'] = s_partner.grade_id.id
        if s_partner.team_id:
            tmp_id = s_partner.team_id.id
            if tmp_id:
                data['team_id'] = self._get_team(tmp_id)
        if s_partner.company_id:
            tmp_id = s_partner.company_id.id
            if tmp_id and tmp_id > 1: # 1 always exist
                data['company_id'] = self._get_company(tmp_id)
        if s_partner.title:
            tmp_id = s_partner.title.id
            if tmp_id:
                # should exist, as we created the map at startup
                data['title'] = self.mapper_get('res.partner.title', tmp_id)
        if s_partner.country_id:
            tmp_id = s_partner.country_id.id
            if tmp_id:
                data['country_id'] = tmp_id
        if s_partner.state_id:
            tmp_id = s_partner.state_id.id
            if tmp_id:
                data['state_id'] = tmp_id
        if s_partner.commercial_partner_id:
            tmp_id = s_partner.commercial_partner_id.id
            if tmp_id and tmp_id != s_partner.id:
                data['commercial_partner_id'] = self.get_new_partner(tmp_id, sm, tm)
        if s_partner.function:
            data['function'] = s_partner.function
        if s_partner.parent_id:
            tmp_id = s_partner.parent_id.id
            if tmp_id:
                data['parent_id'] = self.get_new_partner(tmp_id, sm, tm)
                
        # fix default values
        for k, v in list(DEFAULTS[model].items()):
            data[k] = v
        
        # validate data
        self._validate_and_fix_partner_data(data)
        
        # finaly write out the data
        t_partner.write(data)

        # now we assign all categories the old partner had
        p_ids = [p.id for p in s_partner.category_id]
        if p_ids:
            # map them to new ids
            p_ids = self._map_categories(p_ids)
            # get modules
            nope, t_cats = self._get_modules('res.partner.category')
            for p_id in p_ids:
                t_cat = t_cats.browse(p_id)
                t_cat.write({'partner_ids': [(4, t_partner.id)]})
                
        # chache id, so we do not copy it a second time
        self.done_cache[model][t_partner.id] = 1
        # return state ??
        return t_partner.id
        
    def _create_and_copy_partner(self, old_id, sm, tm, update = -1):
        """
        create partner and return its id that corresponds with the 
        old partner that has the id old_id.
        Copy values from old partner to new one
        
        old_id : integer or res_partner record
            id of the old partner
            
        returns:
            new_id: integer
            id of the coresponding new partner
            
        """
        model = 'res.partner'
        if isinstance(old_id, int):
            partner = sm.browse(old_id)
        else:
            partner = old_id
        if update == -1:
            update = self.update
        # first look the old_id up
        mapped_id = self.mapper_get(model, partner.id)
        if mapped_id:
            if update:
                return self._copy_partner_to_partner(old_id, mapped_id, sm, tm)
            else:
                self.done_cache[model][mapped_id] = 1
                return mapped_id
        
        #  we could not map the old id, maybe the partner alreday exists anyhow
        # try to find it
        # get old partner
        t_partner = []
        if partner.email and partner.email not in self.mapped_emails:
            self.mapped_emails.append(partner.email)
            t_partner = tm.search([('email', '=', partner.email)])
        if not t_partner and partner.name not in self.mapped_names:
            self.mapped_emails.append(partner.name)
            t_partner = tm.search([('name', '=', partner.name)])
        if t_partner:
            t_partner = tm.browse(t_partner[0])
        else:
            # not found, we need to create it
            # -------------------------------
            data = {
                'name' : partner.name,
            }
            t_partner = tm.browse(tm.create(data))
        t_partner = t_partner[0]
        # in any case we map the old-new partnership
        if not self.mapper_get(model, partner.id):
            self.mapper_add(model, partner.id, t_partner.id)
        #self._set_omaps(
            #partner,   #sm.bromse(sm.search(old_id))[0], 
            #t_partner, #tm.bromse(tm.search(new_id))[0], 
            #type='partner')
        
        if self._copy_partner_to_partner(partner, t_partner, sm, tm):
            return t_partner.id
        return None
       
    def get_new_partner(self, old_id, sm, tm):
        """
        return id of the new partner that corresponds with the 
        old partner that has the id old_id.
        The new partner will be created, if it does not yet exist.
        
        old_id : integer
            id of the old partner
            
        returns:
            new_id: integer
            id of the coresponding new partner
        """
        
        # first look the old_id up
        mapped_id = self.mapper_get('res.partner', old_id)
        if mapped_id:
            return mapped_id
        # the old_id has never been seen
        new_id = self._create_and_copy_partner(old_id, sm, tm)
        self.mapper_add('res.partner', old_id, new_id)               
            
    def create_and_copy_partner(self, partner, t_partner_id = None, sm = None, tm = None, update = -1):
        """
        check if all objects a partner record points to exists
        then copy the values of the old to the new one
        Afterwards all objects exist 
        
        partner: source partner object
        t_partner_id : id of target_partner, may be empty, will be created
        """
        if partner and partner.id == 1:
            # do not copy admin
            return 1 # id of admin
        model = 'res.partner'
        if not sm:
            sm, tm = self._get_modules(model)
        # copy data from partner to the target partner
        # if target partner does not exist, create it
        if not t_partner_id:
            t_partner_id = self._create_and_copy_partner(partner, sm, tm, update)
        # make sure, that the objects the partner is dependent on do exist
        # we must look up, whether we find any of the partners already in the partner map
        
        for pp in ['commercial_partner_id', 'parent_id', 'assigned_partner_id']:
            if pp in list(partner._columns.keys()):
                pp = getattr(partner, pp)
                if pp and pp.id and pp.id != partner.id:
                    if len(pp):
                        self.create_and_copy_partner(pp, None, sm, tm, update)
                        
        # now we have both a partner and a t_partner
        # so we can do the copying
        if not self.done_cache[model].get(t_partner_id):
            self._copy_partner_to_partner(partner, t_partner_id, sm, tm)
        return t_partner_id
               
    def copy_partners(self, update = -1):
        model = 'res.partner'
        sm, tm = self._get_modules(model)
        old_partners = sm.browse(sm.search([]))
        for op in old_partners:
            if op.id <= 3:
                continue
            #partner = op[0] # itterating over a record set returns recordsets
            if op.name:
                self.create_and_copy_partner(op, None, sm, tm, update)
                print(op.name)
            
    def copy_users(self):
        sm, tm = self._get_modules('res.users')
        spart, tpart = self._get_modules('res.partner')
        
        """CREATE TABLE res_users
        (
            id serial NOT NULL,
          active boolean DEFAULT true,
          login character varying(64) NOT NULL,
          password character varying,
          company_id integer NOT NULL,
          partner_id integer NOT NULL,
          create_date timestamp without time zone, -- Created on
          create_uid integer, -- Created by
          share boolean, -- Share User
          write_uid integer, -- Last Updated by
          write_date timestamp without time zone, -- Last Updated on
          signature text, -- Signature
          action_id integer, -- Home Action
          password_crypt character varying, -- Encrypted Password
          alias_id integer NOT NULL, -- Alias
          chatter_needaction_auto boolean, -- Automatically set needaction as Read
          sale_team_id integer, -- Sales Team
          target_sales_done integer, -- Activities Done Target
          target_sales_won integer, -- Won in Opportunities Target
          target_sales_invoiced integer, -- Invoiced in Sale Orders Target
          google_calendar_token_validity timestamp without time zone, -- Token Validity
          google_calendar_cal_id character varying, -- Calendar ID
          google_calendar_rtoken character varying, -- Refresh Token
          google_calendar_last_sync_date timestamp without time zone, -- Last synchro date
          google_calendar_token character varying, -- User token
          CONSTRAINT res_users_pkey PRIMARY KEY (id),
          CONSTRAINT res_users_alias_id_fkey FOREIGN KEY (alias_id)
          REFERENCES mail_alias (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE RESTRICT,
              CONSTRAINT res_users_company_id_fkey FOREIGN KEY (company_id)
          REFERENCES res_company (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE SET NULL,
              CONSTRAINT res_users_create_uid_fkey FOREIGN KEY (create_uid)
          REFERENCES res_users (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE SET NULL,
              CONSTRAINT res_users_partner_id_fkey FOREIGN KEY (partner_id)
          REFERENCES res_partner (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE RESTRICT,
              CONSTRAINT res_users_sale_team_id_fkey FOREIGN KEY (sale_team_id)
          REFERENCES crm_team (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE SET NULL,
              CONSTRAINT res_users_write_uid_fkey FOREIGN KEY (write_uid)
          REFERENCES res_users (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE SET NULL,
              CONSTRAINT res_users_login_key UNIQUE (login)
        )
        WITH (
            OIDS=FALSE
        );"""
        old_users = sm.browse(sm.search([]))
        for ou in old_users:
            login = ou.login
            # try to locate new user in target
            if login != 'admin':
                nu = tm.search([('login', '=', login)])
                if nu:
                    # the old user was found
                    # add it to the object map
                    nu = tm.browse(nu)
                    if not self.mapper_get('res.users', ou.id):
                        self.mapper_add('res.users', ou.id, nu.id)
                    print(nu.name)
                    if self.update:
                        pass
                else:
                    # we create a new user
                    partner = ou.partner_id
                    #partner = spart.browse([pid]) # must exist
                    data = {
                        'login' : ou.login,
                        'password_crypt' : ou.password_crypt,
                        'email' : partner.email,  
                        'name' : partner.name,
                    }
                    # create a user, this creates also a partner
                    # the copy data from old partner to new partner
                    # fix default values
                    for k, v in list(DEFAULTS['res.user'].items()):
                        data[k] = v                    
                    nu_id = tm.create(data)
                    nu = tm.browse([nu_id])
                    self.mapper_add('res.users', ou.id, nu.id)
                    # now fill the object maps
                    # creating a user also creates a partner
                    # so we copy the partner values
                    self.create_and_copy_partner(ou.partner_id, nu.partner_id)
                    print(ou.name)
        print(old_users)
        
    def copy_langs(self):
        sm, tm = self._get_modules('res.lang')
        old_langs = sm.browse(sm.search([]))
        for ol in old_langs:
            #ol_data = ol.read()[0]
            oc = ol.code
            if RESTRICT_LANGS and oc not in LANGS_TO_COPY:
                continue
            nl = tm.search([('code', '=', oc)])
            if not nl:
                tm.load_lang(oc)
        
    def copy_groups(self):
        sm, tm = self._get_modules('res.groups')
        old_groups = sm.browse(sm.search([]))
        for og in old_groups:
            on = og.name
            ng = tm.search([('name', '=', on)])
            if not ng:
                data = {
                    'name': og.name,
                    'comment' : og.comment,
                    'color': og.color,
                    'full_name': og.full_name,
                    'share': og.share,
                }
                
                tm.create(data)

    def copy_titles(self):
        model = 'res.partner.title'
        sm, tm = self._get_modules(model)
        titles = sm.browse(sm.search([]))
        new_titles =  {x:y for x,y in[(t.name, t.id) for t in tm.browse(tm.search([]))]}
        for t in titles:
            if t.name in new_titles:
                if not self.mapper_get(model, t.id):
                    self.mapper_add(model, t.id, new_titles[t.name])
            else:
                try:
                    new_id = tm.create({'name' : t.name, 'shortcut' : t.shortcut})
                    self.mapper_add(model, t.id, new_id)
                except:
                    pass # there are duplicates
                   
    def copy_company(self):
        model = 'res.company'
        sm, tm = self._get_modules(model)
        companies = sm.browse(sm.search([]))
        for company in companies:
            if not self.mapper_get(model, company.id):
                partner_id = self.mapper_get('res.partner', company.partner_id.id) or 1
                data = {
                    'name' : company.name,
                    'rml_footer' : company.rml_footer,
                    'rml_header' : company.rml_header,
                    'rml_paper_format' : company.rml_paper_format,
                    'logo_web' : company.logo_web,
                    'font' : company.font and company.font.id or False,
                    'account_no' : company.account_no,
                    'email' : company.email,
                    'custom_footer' : company.custom_footer,
                    'phone' : company.phone,
                    'rml_header2' : company.rml_header2,
                    'rml_header3' : company.rml_header3,
                    'rml_header1' : company.rml_header1,
                    'company_registry' : company.company_registry,
                    'fiscalyear_lock_date' : company.fiscalyear_lock_date,
                    'bank_account_code_prefix' : company.bank_account_code_prefix,
                    'cash_account_code_prefix' : company.cash_account_code_prefix,
                    'anglo_saxon_accounting' : company.anglo_saxon_accounting,
                    'fiscalyear_last_day' : company.fiscalyear_last_day,
                    'expects_chart_of_accounts' : company.expects_chart_of_accounts,
                    'period_lock_date' : company.period_lock_date,
                    'paypal_account' : company.paypal_account,
                    'accounts_code_digits' : company.accounts_code_digits,
                    'overdue_msg' : company.overdue_msg,
                    'fiscalyear_last_month' : company.fiscalyear_last_month,
                    'tax_calculation_rounding_method' : company.tax_calculation_rounding_method,
                    'sale_note' : company.sale_note,
                    # the following values are probably only when we have stock
                    #'propagation_minimum_delta' : company.propagation_minimum_delta,
                    #'security_lead' : company.security_lead,     
                    'chart_template_id' : company.chart_template_id and company.chart_template_id.id  or False,
                    #'internal_transit_location_id' : company.internal_transit_location_id and company.internal_transit_location_id.id  or False,
                    'project_time_mode_id' : company.project_time_mode_id and company.project_time_mode_id.id  or False,
                    'paperformat_id' : company.paperformat_id and company.paperformat_id.id  or False,
                    'partner_id' : company.partner_id and company.partner_id.id  or False ,
                    'currency_id' : company.currency_id and company.currency_id.id  or False,
                    'parent_id' : company.parent_id and company.parent_id.id  or False,
                    'currency_exchange_journal_id' : company.currency_exchange_journal_id and company.currency_exchange_journal_id.id  or False,
                    'transfer_account_id' : company.transfer_account_id and company.transfer_account_id.id  or False,
                    'property_stock_valuation_account_id' : company.property_stock_valuation_account_id and company.property_stock_valuation_account_id.id  or False,
                    'property_stock_account_output_categ_id' : company.property_stock_account_output_categ_id and company.property_stock_account_output_categ_id.id  or False,
                    'property_stock_account_input_categ_id' : company.property_stock_account_input_categ_id and company.property_stock_account_input_categ_id.id  or False,                    
                }
                
                # fix default values
                for k, v in list(DEFAULTS[model].items()):
                    data[k] = v
                
                if company.id == 1:
                    # this company always exists
                    tm.browse(tm.search([])).write(data)
                    new_id = company.id
                else:
                    new_id = tm.create(data)
                self.mapper_add(model, company.id, new_id)
                
    def copy_account_journals(self, force=True):
        # copy bank journals
        # this also copies the banks itself
        model = 'account.journal'
        sm, tm = self._get_modules(model)       
        accounts = sm.browse(sm.search([]))
        for account in accounts:
            if account.bank_account_id:
                if not self.mapper_get(model, account.id) or force:
                    # first check wheter ther is allready an account with the existing number
                    acn = account.bank_acc_number
                    new_id = tm.search([('bank_account_id', 'ilike', acn.strip())])
                    if not new_id:
                        data = {
                            'bank_acc_number': account.bank_acc_number,
                            #u'bank_id': account.bank_id.id, #776, #822
                            #'code': 'BNK4', # will be generated
                            #u'company_id': 1,
                            #u'currency_id': False,
                            #'default_credit_account_id': 174,
                            #'default_debit_account_id': 174,
                            'display_on_footer': account.display_on_footer,
                            #'inbound_payment_method_ids': [[6, False, [1, 3]]],
                            'name': account.name,
                            #u'outbound_payment_method_ids': [[6, False, [2]]],
                            #'sequence_id': account.sequence_id.id,
                            'type': account.type,
                        }
                        new_id = tm.create(data)
                    self.mapper_add(model, account.id, new_id)
                    # now we have to copy the bank data
                    target_line = tm.browse(new_id)
                    s_bank = account.bank_id
                    t_bank = target_line.bank_account_id
                    self.copy_bank(s_bank, t_bank)
               
    def copy_bank(self, bank, target_bank):
        # one source bank to the target bank
        spourious_fields = [
            'bank_areacode',
            'bank_bcart',
            'bank_branchid',
            'bank_clearing_new',
            'bank_eurosic',
            'bank_group',
            'bank_headquarter',
            'bank_lang',
            'bank_postaccount',
            'bank_postaladdress',
            'bank_sic',
            'bank_sicnr',
            'bank_valid_from',
            'ccp',
            'clearing',
            'code',
        ]
        data = {
            'active' : bank.active,
            #'bank_areacode' : bank.bank_areacode,
            #'bank_bcart' : bank.bank_bcart,
            #'bank_branchid' : bank.bank_branchid,
            #'bank_clearing_new' : bank.bank_clearing_new,
            #'bank_eurosic' : bank.bank_eurosic,
            #'bank_group' : bank.bank_group,
            #'bank_headquarter' : bank.bank_headquarter,
            #'bank_lang' : bank.bank_lang,
            #'bank_postaccount' : bank.bank_postaccount,
            #'bank_postaladdress' : bank.bank_postaladdress,
            #'bank_sic' : bank.bank_sic,
            #'bank_sicnr' : bank.bank_sicnr,
            #'bank_valid_from' : self._fix_date(bank.bank_valid_from),
            'bic' : bank.bic,
            #'ccp' : bank.ccp,
            'city' : bank.city,
            #'clearing' : bank.clearing,
            #'code' : bank.code,
            'country' : bank.country.id,
            #'create_uid' : bank.create_uid,
            'display_name' : bank.display_name,
            'email' : bank.email,
            'fax' : bank.fax,
            'name' : bank.name,
            'phone' : bank.phone,
            #'state' : bank.state,
            'street' : bank.street,
            'street2' : bank.street2,
            #'write_uid' : bank.write_uid,
            'zip' : bank.zip,
        }
        existing_fields = list(bank._columns.keys())
        for field in spourious_fields:
            if field in existing_fields:
                data[field] = getattr(bank, field)
            
        new_id = target_bank.write(data)
              
    def _map_categories(self, category_ids)  :
        """
        categories: list of old categories
        return: maped new ids
        """
        model = 'res.partner.category'
        result = []
        for cat_id in category_ids:
            new_id = self.mapper_get(model, cat_id)
            if new_id:
                result.append(new_id)
        return result
    
    def _copy_category(self, model, sm, tm, cat):
        parent_id = False
        if cat.parent_id:
            parent_id = self._copy_category(model, sm, tm, cat.parent_id)
        new_id = self.mapper_get(model, cat.id)
        if not new_id:
            data = {
                'name' : cat.name,
                'color' : cat.color,
                #'currency_id'  : cat.currency_id.ind,
                'active' : cat.active,
                'parent_id': parent_id, 
            }
            new_id = tm.create(data)
            self.mapper_add(model, cat.id, new_id)
        return new_id

    def copy_categories(self):        
        model = 'res.partner.category'
        sm, tm = self._get_modules(model)       
        categories = sm.browse(sm.search([]))
        for cat in categories:
            self._copy_category(model, sm, tm, cat)
                
    def copy_maillists(self):        
        model = 'mail.mass_mailing.list'
        sm, tm = self._get_modules(model)       
        maillists = sm.browse(sm.search([]))
        for ml in maillists:
            print(ml.name)
            new_id = self.mapper_get(model, ml.id)
            if not new_id:
                data = {
                    'popup_redirect_url' : ml.popup_redirect_url,
                    'name' : ml.name,
                    'popup_content' : ml.popup_content,
                    'active' : ml.active,
                }
                new_id = tm.create(data)
                self.mapper_add(model, ml.id, new_id)
            #self._copy_category(model, sm, tm, cat)
               
    def copy_maillists_contacts(self):  
        self.copy_maillists()
        model = 'mail.mass_mailing.contact'
        sm, tm = self._get_modules(model)       
        contacts = sm.browse(sm.search([]))
        for contact in contacts:
            print(contact.email)
            new_id = self.mapper_get(model, contact.id)            
            if not new_id:
                data = {
                    'opt_out' : contact.opt_out,
                    'email' : contact.email,
                    'list_id' : self.mapper_get('mail.mass_mailing.list', contact.list_id.id),
                    'message_bounce' : contact.message_bounce,
                }
                new_id = tm.create(data)
                self.mapper_add(model, contact.id, new_id)
                # now link them
                #tm.browse([new_id]).write({'list_id': [(4, t_partner.id)]})
                

    def copy_productsxx(self):
        vals = {
         'active': True,
         'categ_id': 1,
         'company_id': 1,
         'default_code': 'mio',
         'description': 'mitonikonto',
         'description_sale': 'verkufsbechr',
         'list_price': 1,
         'membership': True,
         'membership_date_from': '2017-05-19',
         'membership_date_to': '2017-05-21',
         'message_follower_ids': [[0,
                                   0,
                                   {'partner_id': 3,
                                    'res_id': 19,
                                    'res_model': 'product.template',
                                    'subtype_ids': [(6, 0, [1])]}]],
         'name': 'Mitoni',
         'property_account_income_id': 17,
         'taxes_id': [[6, False, [14]]]}
        
        model = 'product.product'
        sm, tm = self._get_modules(model)       
        products = sm.browse(sm.search([]))
        for product in products:
            print(product.name, product.price)
            new_id = self.mapper_get(model, product.id)
            if not new_id:
                data = {
                    'weight' : product.weight,
                    'default_code' : product.default_code,
                    'name' : product.name,
                    'name_template' : product.name_template,
                    #'product_tmpl_id' : product.product_tmpl_id.id,
                    'barcode' : product.barcode,
                    'volume' : product.volume,
                    'active' : product.active,
                    'is_amenity' : product.is_amenity,
                    'status' : product.status,
                    'is_service' : product.is_service,
                    'price' : product.price
                }
                new_id = tm.create(data)
                self.mapper_add(model, product.id, new_id)
        
    def copy_products(self):
        vals = {
         'active': True,
         'categ_id': 1,
         'company_id': 1,
         'default_code': 'mio',
         'description': 'mitonikonto',
         'description_sale': 'verkufsbechr',
         'list_price': 1,
         'membership': True,
         'membership_date_from': '2017-05-19',
         'membership_date_to': '2017-05-21',
         'message_follower_ids': [[0,
                                   0,
                                   {'partner_id': 3,
                                    'res_id': 19,
                                    'res_model': 'product.template',
                                    'subtype_ids': [(6, 0, [1])]}]],
         'name': 'Mitoni',
         'property_account_income_id': 17,
         'taxes_id': [[6, False, [14]]]}
        
        model = 'product.template'
        model_p = 'product.product'
        sm, tm = self._get_modules(model)       
        sp, tp = self._get_modules(model_p)       
        product_templates = sm.browse(sm.search([]))
        mtypes = MEMBERSHIP_ITEMS['membership_types']
        membership_start_end = MEMBERSHIP_ITEMS['membership_start_end']
        for pt in product_templates:
            print(pt.name)
            new_id = self.mapper_get(model, pt.id)
            if not new_id:
                # we need to get the product
                product = sp.browse(sp.search([('product_tmpl_id', '=', pt.id)]))
                data = {
                    'warranty' : pt.warranty, #warranty
                    'list_price' : pt.list_price, #list_price
                    #'weight' : pt.weight, #weight
                    'sequence' : pt.sequence, #sequence
                    'color' : pt.color, #color
                    'description_purchase' : pt.description_purchase, #description_purchase
                    'sale_ok' : pt.sale_ok, #sale_ok
                    'state' : pt.state, #state
                    'description_sale' : pt.description_sale, #description_sale
                    'description' : pt.description, #description
                    #'volume' : pt.volume, #volume
                    #'active' : pt.active, #active
                    'rental' : pt.rental, #rental
                    'name' : pt.name, #name
                    'type' : pt.type, #type
                    'track_service' : pt.track_service, #track_service
                    'invoice_policy' : pt.invoice_policy, #invoice_policy
                    'event_ok' : pt.event_ok, #event_ok
                    'website_meta_title' : pt.website_meta_title, #website_meta_title
                    'website_published' : pt.website_published, #website_published
                    'website_description' : pt.website_description, #website_description
                    'website_meta_description' : pt.website_meta_description, #website_meta_description
                    'website_size_x' : pt.website_size_x, #website_size_x
                    'website_size_y' : pt.website_size_y, #website_size_y
                    'website_meta_keywords' : pt.website_meta_keywords, #website_meta_keywords
                    'website_sequence' : pt.website_sequence, #website_sequence
                    'description_picking' : pt.description_picking, #description_picking
                    'sale_delay' : pt.sale_delay, #sale_delay
                    'tracking' : pt.tracking, #tracking
                    
                    # elements from product
                    'weight' : product.weight,
                    'default_code' : product.default_code,
                    'name' : product.name,
                    #'name_template' : product.name_template,
                    #'product_tmpl_id' : product.product_tmpl_id.id,
                    'barcode' : product.barcode,
                    'volume' : product.volume,
                    'active' : product.active,
                    'is_amenity' : product.is_amenity,
                    'is_room' : product.is_amenity,
                    'is_service' : product.is_service,
                    'status' : product.status,                    
                }
                # --------------------------------
                # links to create
                # which we do not yet handle
                # --------------------------------
                linkk_data = {
                    'categ_id' : pt.categ_id, #categ_id
                    'product_manager' : pt.product_manager, #product_manager
                    'company_id' : pt.company_id, #company_id
                    'event_type_id' : pt.event_type_id, #event_type_id
                    'uom_id' : pt.uom_id, #uom_id
                    'uom_po_id' : pt.uom_po_id, #uom_po_id
                }
                # only make member for given list:
                if COPY_MEMBERSHIP:
                    if pt.name in mtypes:
                        data['membership_date_from'] = membership_start_end[0]
                        data['membership_date_to']   = membership_start_end[1]
                        data['membership'] = True
                new_id = tm.create(data)
                self.mapper_add(model, pt.id, new_id)

    def copy_membership(self):
        model = 'membership.membership_line'
        sm, tm = self._get_modules(model)       
        membership_lines = sm.browse(sm.search([]))
        for membership_line in membership_lines:
            pass
        
# some global flags
RESTRICT_LANGS = True
LANGS_TO_COPY = ['de_CH']

MEMBERSHIP_ITEMS = {
    #membership_cancel date, -- Cancel Membership Date
    #free_member boolean, -- Free Member
    #membership_amount numeric, -- Membership Amount
    #membership_start date, -- Membership Start Date
    #membership_stop date, -- Membership End Date
    #associate_member integer, -- Associate Member
    #membership_state character varying, -- Current Membership Status
    
    # trigger say when to handle membership
    'trigger': 'membership_state',
    
    # values to copy
    'copy' : [
        'free_member',
        'membership_cancel', 
        'membership_amount',
        'membership_start',
        'membership_stop',
        'associate_member',
        'membership_state',
        'date_localization',
        'partner_latitude',
        'partner_longitude',
        'partner_weight',
        'date_review',
        'date_partnership',
        'date_review_next',        
    ],
    'membership_types' : ["Einzelmitglied", "Gruppenmitglied", "Familienmitglied"],
    'membership_start_end' : ['1.1.2017', '31.12.2017'],
}
# flag if we should handle membership
COPY_MEMBERSHIP = False
        
handler = Handler()
#handler.copy_maillists_contacts()
handler.copy_langs()
handler.copy_groups()
handler.copy_titles()
handler.copy_categories()
handler.copy_users()
handler.copy_company()
handler.copy_account_journals()
####handler.copy_banks(force=True)
handler.copy_partners(update = False)
#handler.copy_products()
#handler.copy_membership()

#create_membership_invoice