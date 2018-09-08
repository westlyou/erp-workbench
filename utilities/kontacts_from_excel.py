# -*- coding: utf-8 -*-
"""
$header?3 -> skip 3 lines till data starts

sampe field description:

    $parent?1:res_partner.name,res_partner.is_company=1
    $parent: this is the parent object
        ?1 : if must exist to process the child entities
    res_partner.name: the content of the field will be used for the model
        restartner, and be written into the field 'name'
    res_partner.is_company=1: the value of the field is_company will be set to 1
"""
import xlrd
from argparse import ArgumentParser
import argparse
import os
import sys
import glob
import re
import odoorpc
from copy import deepcopy
from configparser import SafeConfigParser
from collections import OrderedDict
import psycopg2
import psycopg2.extras
import datetime

sys.path.insert(0,'.')

from templates.excel_reader_files import HEAD, FILE_BLOCK, PAGE_BLOCK

# some file types are not supported
USUPPORTED_TYPES = ['.xlsb', '.docx', '.ods', '.cfg', '.ori']

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
    
FIELDS = """
# res_user
# --------
res_user.firstname :                 character varying NOT NULL,      -- first name of partner assigned to user

# crm_lead                           
# --------
crm_lead.name :                      character varying,               -- Name of the lead
crm_lead.stage_id :                  integer,                         -- Stage
crm_lead.medium_id :                 integer,                         -- Medium
crm_lead.referred :                  character varying,               -- Referred By
crm_lead.partner_id :                integer,                         -- Customer
crm_lead.create_date :               timestamp without time zone,     -- Create Date
crm_lead.description :               text,                            -- Notes
crm_lead.type        :               character varying NOT NULL,      -- Type

# crm_stage
# ---------
crm_stage.name :                     character varying NOT NULL,      -- Stage Name
crm_stage.probability :              double precision NOT NULL,       -- Probability
crm_stage.team_id :                  integer,                         -- Team
crm_stage.legend_priority :          text,                            -- Priority Management Explanation

# partner (customer, suplier, ...)
# --------------------------------
res_partner.comment :                text,                            -- Notes
res_partner.website :                character varying,               -- Website
res_partner.street :                 character varying,               -- Street
res_partner.supplier :               boolean,                         -- Is a Vendor
res_partner.city :                   character varying,               -- City
res_partner.zip :                    character varying,               -- Zip
#res_partner.title :                  integer,                         -- Title
res_partner.country_id :             integer,                         -- Country
res_partner.name :                   character varying,               -- Name
res_partner.company_name :           character varying,               -- Company Name
res_partner.email :                  character varying,               -- Email
res_partner.is_company :             boolean,                         -- Is a Company
res_partner.function :               character varying,               -- Job Position
res_partner.lang :                   character varying,               -- Language
res_partner.fax :                    character varying,               -- Fax
res_partner.street2 :                character varying,               -- Street2
res_partner.barcode :                character varying,               -- Barcode
res_partner.phone :                  character varying,               -- Phone
res_partner.tz :                     character varying,               -- Timezone
res_partner.customer :               boolean,                         -- Is a Customer
res_partner.user_id :                integer,                         -- Salesperson
res_partner.mobile :                 character varying,               -- Mobile
res_partner.vat :                    character varying,               -- TIN
res_partner.state_id :               integer,                         -- State
res_partner.team_id :                integer,                         -- Sales Team
res_partner.firstname :              character varying,               -- First name
res_partner.lastname :               character varying,               -- Last name

""" 
STATES_MAP = {
    # this is a mapping from possible german names in lowercas
    # to the database name
    "aargau"                    : "Argovia",
    "appenzell inner rhoden"    : "Appenzell Inner Rhodes",
    "appenzell ausser rhoden"   : "Appenzell Outher Rhodes",
    "bern"                      : "Bern",
    "basel-land"                : "Basel-Country",
    "basel-stadt"               : "Basel-City",
    "basel"                     : "Basel-City",
    "germany"                   : "Germany",
    "fürstentum liechtenstein"  : "Principality of Liechtenstein",
    "freiburg"                  : "Fribourg",
    "genf"                      : "Geneva",
    "glarus"                    : "Glarus",
    "graubünden"                : "Grisons",
    "italy"                     : "Italy",
    "jura"                      : "Jura",
    "luzern"                    : "Luzern",
    "neuenburg"                 : "Neuchâtel",
    "nidwalden"                 : "Nidwald",
    "obwalden"                  : "Obwald",
    "st. gallen"                : "St. Gallen",
    "schaffhausen"              : "Schaffhausen",
    "solothurn"                 : "Solothurn",
    "schwyz"                    : "Schwyz",
    "thurgau"                   : "Thurgovia",
    "tessin"                    : "Ticino",
    "uri"                       : "Uri",
    "wadt"                      : "Vaud",
    "vallis"                    : "Valais",
    "zug"                       : "Zug",
    "zürich"                    : "Zurich",
}
# defaults are used in leu of actual values when creating a
# new record.
DEFAULTS = {
    'tz' : 'Europe/Zurich',
    'country_id' : 44,
    'lang' : 'de_CH',
}
CDEFAULTS = {
    'tz' : 'Europe/Zurich',
    'country_id' : 44,
    'lang' : 'de_CH',
    'is_company' : 0,
}
ODEFAULTS = {
    'type' : 'lead',
}
# object map describes the possible generations
OBJECT_MAP  = {
    '$parent' : {
        'model' : 'res.partner', 
        'key' : '$parent', 
        'search' : {'key' : 'email', 'fields' : ('name', 'zip')},
        'need_key' : {'type' : 'email', 'fields' : ('name', 'zip')},
        'min_fields' : ['name'],
        'defaults' : DEFAULTS,
    },
    '$child' : {
        'model' : 'res.partner', 
        'key' : '$child', 
        'search' : {'key' : 'email', 'fields' : ('lastname', 'firstname')},
        'need_key' : {'type' : 'email', 'fields' : ('lastname', 'firstname')},
        'min_fields' : ['lastname', 'firstname'],
        'child_of' : [{'parent' : '$parent', 'parent_rel' : 'id', 'child_rel' : 'parent_id'}],
        'defaults' : CDEFAULTS,
    },
    '$child2' : {
        'model' : 'res.partner', 
        'key' : '$child2', 
        'search' : {'key' : 'email', 'fields' : ('lastname', 'firstname')},
        'need_key' : {'type' : 'email', 'fields' : ('lastname', 'firstname')},
        # if record has not at leas minfields, do not event ry to save
        'min_fields' : ['lastname', 'firstname'],        
        'child_of' : [{'parent' : '$parent', 'parent_rel' : 'id', 'child_rel' : 'parent_id'}],
        'defaults' : CDEFAULTS,
    },
    '$user' : {
        'model' : 'res.users', 
        'key' : '$user', 
        'search' : {'key' : 'email', 'fields' : ('name')},
        'need_key' : {'key' : 'email', 'fields' : ('name')},
        # we do not create a user, we just want it as parent
        'donotcreate' : True,
    },
    '$lead' : {
        'model' : 'crm.lead',
        'exta_models' : ['crm_stage',],
        'key' : '$lead',
        #'childof' : ['$parent','$user'],
        'child_of' : [
            {'parent' : '$parent', 'parent_rel' : 'id', 'child_rel' : 'partner_id'},
            {'parent' : '$user', 'parent_rel' : 'id', 'child_rel' : 'user_id'},
        ],
        'min_fields' : ['name',], 
        'search' : {'fields' : ('name', 'description',)},
        'defaults' : ODEFAULTS,
        'tag_obj' : 'crm_lead_tag',
    },
    'categories'  : {'model' : 'res.partner.category'},
    'title'  : {'model' : 'res.partner.title'},
}
# map fields to functions to get/set the value
FIELD_FUNCTIONS = {
    'res_partner.state' : '_lookup_state_id',
    'res_partner.title' : '_lookup_title_id',
    'crm_lead.create_date'    : '_crm_fixup_date',
    'res_user.firsname' : '_res_user_lookup_firstname',
    'res_user.firsname' : '_res_user_lookup_firstname',
    'crm_lead.stage_id' : '_lookup_crm_stage_id',
}
AUTO_EMAIL_DOMAIN = '@excelreader.ch'

class Dummy(object):
    """
    used instead of an odoo object
    """
    pass

class partnerHandler(object):
    gen_map = None
    fields = None
    modules_map = {}
    key_rule = None # used to generate keys when they are missing
    error_list = []
    
    def __init__(self, opts):
        self.opts = opts
        # read the config file
        parser = SafeConfigParser()
        parser.optionxform = str
        config_path = os.path.normpath(os.path.expanduser('%s/%s' % (opts.path, opts.config)))
        if not os.path.exists(config_path):
            print(bcolors.WARNING + '*' * 80)
            print(config_path, 'does not exist' + bcolors.ENDC)
        parser.read(config_path)
        self.parser = parser

        try:
            odoo = odoorpc.ODOO(opts.host, port=opts.port)
            odoo.login(opts.name, opts.user, opts.password)
            self.odoo = odoo
            self.odoo.env.context['lang'] = 'en_US'
            # make sure we have all models loaded so we can use to search them or create objects
            for k,v in list(OBJECT_MAP.items()):
                models = [v['model']] + v.get('extra_models', [])
                for m in models:
                    m = v['model']
                    if m not in self.modules_map:
                        self.modules_map[m] = (odoo.env[m], m, k)
                clist = v.get('child_of', [])
                for c in clist:
                    m = OBJECT_MAP[c.get('parent')]['model']
                    if m not in self.modules_map:
                        self.modules_map[m] = (odoo.env[m], m, c.get('parent'))
        except Exception as e:
            print(bcolors.WARNING + '*' * 80)
            print('not logged into odoo')
            if not opts.name:
                print('no database name is defined. Use -n to do so')
            if opts.verbose:
                print(str(e))
                tmp = sys.exc_info()
                print(tmp[0], tmp[1])
                print(str(tmp[2]))
                del tmp
            print('*' * 80 + bcolors.ENDC)
            
        if opts.dbpassword:
            conn_string = "dbname='%s' user=%s host='%s' password='%s'" % (opts.name, opts.dbuser,  opts.dbhost, opts.dbpassword)
        else:
            conn_string = "dbname='%s' user=%s host='%s'" % (opts.name, opts.dbuser,  opts.dbhost)
    
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor_d = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.connection = conn
        
        #self.tag_dic = TAG_DIC
        #self.anreden_dic = ANREDEN_DIC
        #for tag in TAGS:
            #self.tag_dic[tag] = self.tags.browse(self.tags.search([('name', '=', tag)])).id
        #for anrede in ANREDEN:
            #self.anreden_dic[anrede] = self.titles.browse(self.titles.search([('name', '=', anrede)])).id
            
            
    def _res_user_lookup_firstname(self, model, value):
        # we know the firstname of the user
        # actually of the partnerobject assigned to the user
        field_name = 'id'
        if not value:
            value = 'administrator'
        cursor = self.connection.cursor()
        query = 'select res_users.id from res_users, res_partner where res_partner.firstname ilike %s and res_users.partner_id = res_partner.id'
        cursor.execute(query, (value,))
        result = cursor.fetchall()
        ids = [1] #administrator
        if result:
            ids = [r[0] for r in result]
        else:
            self.add_to_error(value, '', 'is not an existing user')
        users = model.browse(model.search([('id', 'in', ids)]))
        return (field_name, users[0].id)
                
    def _crm_stage_name(self, model, value):
        pass
    
    def _crm_fixup_date(self, model, value):
        """
        we must convert date to a date object
        15.02.2017 -> date(...)
        """
        field_name = 'create_date'
        if value:
            d = datetime.datetime.strptime('15.02.2017', '%d.%m.%Y').date()
            return(field_name, d.isoformat())
        return(field_name, '')     

    def _lookup_title_id(self, model, value):
        # value is the name of a state like Neuenburg
        # which we will look in the STATES_MAP, and then in res_country_state
        # if not found there we look it up unaltered
        # model we do not use but build our own
        if not value:
            return (None, None)
        model = self.odoo.env['res.partner.title']
        field_name = 'title'    
        try:
            title_map = self.title_map
        except:
            self.title_map = {}
            title_map = self.title_map
        if value in title_map:
            return (field_name, title_map[value])
        titles = model.search([('name', '=', value)])
        if titles:
            return (field_name, titles[0])
        return (field_name, model.create({'name': value}))
    
    def _lookup_crm_stage_id(self, model, value):
        """
        model: model which is actual when called
        value: value to deal with
        """
        self.odoo.env.context['lang'] = 'en_US'
        model = self.odoo.env['crm.stage']
        # value is the name of a stage
        field_name = 'stage_id'
        result = model.search([('name', '=', value)])
        stage_id = None
        if result:
            stage_id = result[0]
        else:
            a=1
            pass
        return (field_name, stage_id)
        
    def _lookup_state_id(self, model, value):
        # value is the name of a state like Neuenburg
        # which we will look in the STATES_MAP, and then in res_country_state
        # if not found there we look it up unaltered
        # model we do not use but build our own
        model = self.odoo.env['res.country.state']
        field_name = 'state_id'
        try:
            state_map = self.state_map
        except:
            self.state_map = {}
            state_map = self.state_map
        if value in state_map:
            return (field_name, state_map[value])
        # look up value in STATES_MAP
        value_m = STATES_MAP.get(str(value).lower())
        if value_m:
            try:
                state_id = model.search([('name', '=', value_m)])[0] # should allways exist
            except:
                #print ('name', '=', value_m)
                return (None,None)
                #raise
                #print bcolors.FAIL + '*' * 80
                #print 'the states map for switzerland is not installed'
                #print '*' * 80 + bcolors.ENDC
                #sys.exit()
                
            state_map[value] = state_id
            state_map[value_m] = state_id
        else:
            state_id = model.search([('name', 'ilike', value)])
            if state_id:
                state_map[value] = state_id[0]
        if state_id:
            return (field_name, state_id)
        return (None,None)
    
    def check_email(self, email):
        match = re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)    
        if match:
            return True
        else:
            return False
            
    def add_to_error(self, line, data, reason, extra=None):
        if self.opts.verbose:
            print(reason, data, extra)
        self.error_list.append((line, data, reason, extra or ''))

    def get_fields(self):
        if not self.fields:
            self.fields = dict(self.parser.items('fields'))
        return self.fields

    def get_gen_map(self):
        if not self.gen_map:
            gm = {}
            for k, v in list(OBJECT_MAP.items()):
                if 'key' in v:
                    gm[v['key']] =  v
            self.gen_map = gm
        return self.gen_map

    def search_partner(self, firstname, lastname):
        # return an existing cms page
        firstname = firstname.strip()
        lastname = lastname.strip()
        partners = self.partners
        if firstname and lastname:
            return partners.browse(partners.search([('lastname', 'ilike', lastname), ('firstname', 'ilike', firstname)]))
        else:
            return partners.browse(partners.search([('lastname', 'ilike', lastname)]))

    def empty_line(self, row, my_fields):
        # skip lines starting with #
        first_cell = row[0].value
        if first_cell:
            if str(first_cell).strip().startswith('#'):
                return True
        mks = list(my_fields.keys())
        for ki in mks:
            if row[int(ki)].value:return False
        return True
        #return not [c for c in row if c.value]

    def check_name(self, name):
        # chek if name is known in list of fields
        fields = self.get_fields()
        try:
            assert name in list(fields.keys()) or name in list(FIELD_FUNCTIONS.keys())
        except:
            raise ValueError('%s not valid' % name)
        
    def create_key(self, info, data):
        # create a unique key in the case of missing key for a record (normaly an email)
        key_rule = self.key_rule
        if not key_rule:
            key_rule = info.get('need_key')
            if key_rule and key_rule.get('type') == 'email':
                d = {}
                for k,v in list(data.items()):
                    d[k.split('.')[-1]] = v
                fields = key_rule.get('fields', [])
                key = '.'.join([str(d.get(f, '')) for f in fields]) + AUTO_EMAIL_DOMAIN
                return key
        return 
    
    def search_object(self, info, data, line, defaults, page_name):
        """
        info : description of the "generation" read from OBJECT_MAP
            '$parent' : {
                'model' : 'res.partner', 
                'key' : '$parent', 
                'search' : {'key' : 'email', 'fields' : ('name', 'zip')},
                'need_key' : {'type' : 'email', 'fields' : ('name', 'zip')},
                'min_fields' : ['name'],
                'defaults' : DEFAULTS,
            },
              
        data: a dict with fieldnames and the values to assign
        line: the actual line from the excel sheet to add to an ev. error message
        defaults: values to be allways set, will be overwritten by data
        """
        # search or create object
        error_message = ''
        result = None
        m = info.get('model')
        if 'model_obj' not in info:
            model = self.modules_map[m][0]
            info['model_obj'] = model
        else:
            model = info['model_obj']
        # the key is used to uniquely identify an object, mostly email
        key = info.get('search', {}).get('key', {})
        search_fields = info.get('search', {}).get('fields', {})
        # split fields bei punkt
        # suche ob key übergeben wurde und wert hat
        key_name = '_'.join(m.split('.')),key
        k_val = data.get('%s.%s' % (key_name))
        new_key = None
        key_info = {}
        if k_val:
            # check whether that key is well formed
            if 'need_key' in info:
                key_info = info['need_key']
                if key_info.get('type') == 'email':
                    k_val = k_val.replace('(at)', '@').replace('[at]', '@').replace(' ', '').replace('[aet]', '@').replace('[dot]', '.').strip()
                    if not self.check_email(k_val):
                        error_message = '%s for %s in line %s is not valid' % (k_val, key_name, line)
                        return (None, error_message)
            result = model.search([(key, '=', k_val)])
            if result:
                return (model.browse(result[0]), '')
        else:
            # we have no value for the key
            # maybe we created a key ourself
            new_key = self.create_key(info, data)
            if new_key:
                result = model.search([(key, '=', new_key)])
                if result:
                    return (model.browse(result[0]), '')
                # still not found
                # set the key into the defaults,  so it will be written to the new object
                defaults[key] = new_key
        # we have now a either a key or a new_key
        # now we check for more search fields, and check whether we find a unique 
        if search_fields:
            domain = []
            if not isinstance(search_fields, (list, tuple)):
                search_fields = [search_fields]
            for f in search_fields:
                v = data.get('%s.%s' % ('_'.join(m.split('.')),f))
                if v:
                    domain.append((f, '=', v,))
            if domain:
                result = model.search(domain)
                if result:
                    if len(result) > 1:
                        self.add_to_error(line, data, reason='more than one record found searching %s' % str(domain), extra=page_name)
                        return (None, '') # error is allready handled
                    obj = model.browse(result[0])
                    # now we have a record, but if has avalue for the key
                    if k_val:
                        obj.write({key:k_val})
                    # search again, so that we for sure have the key in the resulting obj
                    return (model.browse(result[0]), '')
        # when we come here, we did not find the object, so create it
        # we only handle fields of the actual model
        
        values = defaults
        mm = m.replace('.', '_')
        for k,v in list(data.items()):
            # does the field need some lookup ?
            if k in FIELD_FUNCTIONS:
                fun = getattr(self, FIELD_FUNCTIONS[k], None)
                if fun:
                    f_name, f_value = fun(model, v)
                    if f_name:
                        values[f_name] = f_value
                    continue
            if k.startswith(mm):
                n = k.split('.')[-1]
                values[n] = v
        if values:
            # check whether we have at least min fields
            found_all = True
            for f in info.get('min_fields', []):
                if not values.get(f):
                    found_all = False
                    if error_message:
                        error_message += ', ' + f
                    else:
                        error_message = 'record at line %s has no %s' % (line, f)
            if found_all:
                # if donotcreate is set, we want this object only as referenz
                if info.get('donotcreate', False):
                    domain = []
                    for k,v in list(defaults.items()):
                        domain.append((k, '=', v))
                    result = model.search(domain)
                else:
                    try:
                        result = model.create(values)                    
                    except:
                        error_message = 'object could not be created'
            if result:
                return (model.browse(result), error_message,)
        return (None, error_message)
        
    def check_keyrule(self, key_rule):
        return
        
    def process_page(self, wb, page_name, section_name):
        # gen map tells us what generation exist like $parent, c$childi1 ..
        # and maps them with 
        gen_map = self.get_gen_map()
        opts = self.opts
        parser = self.parser
        # collect values like skip ..
        values = OrderedDict(parser.items(section_name))
        # collect the fields we use for this sheet
        my_fields = OrderedDict(parser.items(section_name + ':fields'))
        # o_map keeps a list of objects generated for a line
        # for each generation we have an object (parent, children ..)
        # each fields definition is generation:fields ..
        o_map = OrderedDict()
        for val in list(my_fields.values()):
            parts = val.split(':') 
            if len(parts) == 1:
                gen = parts[0]
            else:
                gen = parts.pop(0)
            if gen not in o_map:
                # genmap was generated from OBJECT_MAP
                if gen in gen_map:
                    o_map[gen] = {}
                else:
                    raise ValueError('%s is not a valid generation field' % gen)
        
        # collect flags
        flags = dict(parser.items(section_name + ':flags'))
        # collect flags we have to assign to all entities
        fs = flags.get('all')
        categories_all = []
        if fs:
            parts = fs.split(',')
            fl = []
            for part in parts:
                pps = part.split('?')
                name = pps.pop(0)
                if pps:
                    fl.append((name, pps[0],)) 
            if fl:
                m = self.modules_map[OBJECT_MAP['categories']['model']][0]
                for fn in fl:
                    # we start with the value of the tag
                    fs = m.search([('name', '=', fn[1])])
                    if fs:
                        categories_all.append(m.browse(fs).id) 
                    else:
                        # the value of the tag does not exist, so check if its parent exists
                        fs = m.search([('name', '=', fn[0])])
                        if not fs:
                            fs = m.create({'name' : fn[0]})
                        if isinstance(fs, list):
                            fs = fs[0]
                        categories_all.append(m.create({'name' : fn[1], 'parent_id' : fs}))
        
        key_rule = values.get('key_rule', None)
        if key_rule and self.check_keyrule(key_rule):
            self.key_rule = key_rule
        try:
            skip = int(values.get('skip', 0))
        except ValueError:
            skip = 0
            
        # only collect errors for records that must exist
        must_exist = values.get('must_exist', [])
        if must_exist:
            must_exist = must_exist.split(',')
            
        # get the sheet we want to deal with
        sheet = wb.sheet_by_name(page_name)
       
        def process_field(value, description):
            # check whether a field description is decorated with values to set
            # we split them of the name and set the value in the dictonary that will
            # be used to create a new record 
            parts = description.split(':') 
            if len(parts) == 1:
                gen = parts[0]
            else:
                gen = parts.pop(0)                
            description = parts.pop(0)
            # split the description to find my_fields
            parts = [n.strip() for n in description.split(',')]
            for part in parts:
                if part.find('=') > -1:
                    n,v = part.split('=')[:2] # dont die with two =
                    self.check_name(n) # die if bad
                    o_map[gen]['values'][n] = v
                elif part.find(' ') > -1: 
                    # we split the value to the fields
                    names = part.split(' ')
                    values = value.split(' ')
                    if len(values) > len(names):
                        # something like hans w. meier, or dr. ueli gruber
                        diff = len(values) - len(names) + 1
                        first = ' '.join(values[:diff])
                        values = [first] + values[diff:]
                    for name in names:
                        self.check_name(name) # die if bad
                        if values:
                            # assign to child or parent
                            o_map[gen]['values'][name] = values.pop(0)
                    # if there are stil values ... 
                else:
                    self.check_name(part) # die if bad
                    o_map[gen]['values'][part] = value
            
        for row_i in range(sheet.nrows):
            if row_i < skip -1:
                continue
            # clean out items fromm the previous line
            for k,v in list(o_map.items()):
                v['obj'] = None
                v['values'] = {}
            row = sheet.row(row_i)
            if self.empty_line(row, my_fields):
                continue
            l_counter = 0
            for i in range(sheet.ncols):
                if str(i) in my_fields:
                    ldata = row[i].value
                    if isinstance(ldata, str):
                        ldata = ldata.replace('\n', ' ')
                    # now get rid of trailing 0 in numbers
                    try:
                        if row[i].ctype in (2,3) and int(ldata) == ldata:
                            ldata = int(ldata) 
                    except:
                        pass
                    if isinstance(ldata, str) and ldata.strip().startswith('#'):
                        continue
                    process_field(ldata, my_fields[str(i)])
            if self.opts.verbose:
                print('-->', row_i, page_name)
            # now create all the objects
            #gmr = dict([(v,k) for k,v in gen_map.items()]) # reverse gen map
            error_found = False
            for k,v in list(o_map.items()):
                info = gen_map[k]
                defaults = deepcopy(OBJECT_MAP[k].get('defaults', {}))
                obj, err_message = self.search_object(info, v['values'], row_i, defaults, page_name) # find existing or create one
                if err_message:
                    if k in must_exist:
                        self.add_to_error(row_i, v, reason=err_message, extra=page_name)
                        if self.opts.verbose:
                            print('-->', row_i, k, err_message)
                if not obj:
                    if info.get('must_exist'):
                        error_found = True
                        break
                v['obj'] = obj
            if error_found:
                continue
            # now we collected all records for this line
            # so we can assign parrent to children
            # and also assign flags, title et al
            for k, v in list(o_map.items()):
                obj = v['obj']
                if not obj:
                    continue
                # we have to refresh the obj, it could have been deleted
                if not OBJECT_MAP.get(k)['model_obj'].search([('id', '=', obj.id)]):
                    continue
                # set categories
                if not OBJECT_MAP.get(k).get('donotcreate'):
                    for c in categories_all:
                        ignored = 0
                        obj.write({'category_id' : [[4, c, ignored]]})
                # are we a child
                # 'child_of' : [{'parent' : 'parent', 'parent_rel' : 'id', 'child_rel' : 'parent_id'}],
                child_of = OBJECT_MAP.get(k).get('child_of', [])
                # assign the correct relation with each object we are a child of 
                # is it at all possibe to bi child of more tan one?)
                for child_info in child_of:
                    # get parent object
                    parent = o_map[child_info['parent']]['obj']
                    if parent and obj:
                        if parent.id == obj.id:
                            # avoid recursion
                            self.add_to_error(row_i, v['values'], reason='child and parent are identical', extra=page_name)
                            continue 
                    if not parent:
                        self.add_to_error(row_i, v['values'], reason='parent object does not exists', extra=page_name)
                        try:
                            obj.unlink()
                        except:
                            self.add_to_error(row_i, '', 'could not delete object', extra=page_name)
                    else:
                        try:
                            obj.write({child_info['child_rel'] : getattr(parent, child_info['parent_rel'])})
                        except:
                            self.add_to_error(row_i, {child_info['child_rel'] : getattr(parent, child_info['parent_rel'])}, 'could not be writen to %s' % obj.name, extra=page_name)
                # do we need to assign a title ..
        
    def process_file(self, file_name, section_name):
        # every excel file has pages
        # with its own structure
        parser = self.parser
        opts = self.opts
        pages = parser.get(section_name, 'pages')
        # pages are the list of pages withing the excel file we want to read
        # each one of them has a structure, for which we have to access a section that is named
        # section_name:pagename
        
        # open the excel file
        file_path =  os.path.normpath('%s/%s' % (opts.path, file_name))
        if not os.path.exists(file_path):
            print(bcolors.WARNING + '*' * 80)
            print('file %s does not exist' % file_path)
            print('*' * 80 + bcolors.ENDC)
            return

        if os.path.splitext(file_path)[-1] in USUPPORTED_TYPES:
            print(bcolors.WARNING + '*' * 80)
            print('files of type %s are not supported' % os.path.splitext(file_path)[-1])
            print('*' * 80 + bcolors.ENDC)
            return
                       
        wb = xlrd.open_workbook(file_path)
        # get sheet from workbook
        sheet_names = wb.sheet_names()
        pages = pages.split(',')
        errors_found = False
        for page in pages:
            if page not in sheet_names:
                print(bcolors.WARNING + '*' * 80)
                print('page %s does not exist in %s' % (page, file_path))
                print('*' * 80 + bcolors.ENDC)
                errors_found = True
        if errors_found:
            return
        
        filter_pages = []
        if opts.sheetnames:
            filter_pages = [p.lower() for p in opts.sheetnames.split(',')]
        for page in pages:
            page_section = '%s:%s' % (section_name, page)
            if parser.has_section(page_section):
                if filter_pages:
                    if page.lower() not in filter_pages:
                        continue
                self.process_page(wb, page, page_section)
                values = parser.items(page_section)
            else:
                print(bcolors.WARNING + '*' * 80)
                print('section %s is missing' % page_section)
                print('*' * 80 + bcolors.ENDC)
            
    
    def is_processed(self, file_name):
        # is the file allready processed?
        file_path =  os.path.normpath('%s/.processed' % self.opts.path)
        if not os.path.exists(file_path):
            return False
        return file_name in open(file_path).read().split('\n')
        
    def add_processed(self, file_name):
        # add file to the allready processed
        file_path =  os.path.normpath('%s/.processed' % opts.path)
        open(file_path, 'a').write('\n%s' % file_name)
    
    def reset_processed(self):
        # add file to the allready processed list
        open(file_path, 'w').write('')
        
    # files have a structure like this
    # [files]
    # Kampagne2_email01.xlsb:Kampagne2_email01
    # Kampagne3_email01.xlsb:Kampagne2_email01
    # so the value of Kampagne3_email01.xlsb
    # is Kampagne2_email01 for which we find an own section
    def process_files(self):
        parser = self.parser
        try:
            file_list = parser.items('files')
        except:
            print(bcolors.FAIL + '*' * 80)
            print('is odoo running ??')
            print('*' * 80 + bcolors.ENDC)
            return
        force = self.opts.force
        for file_name, section_name in file_list:
            if not force and self.is_processed(file_name):
                continue
            self.process_file(file_name, section_name)        

    def process_name(self, name, act_vals):
        # split extra values from the name and add it to act_vals
        # $parent?ex=1:res_partner.name,res_partner.is_company=1
        parts = name.split(':')
        name = parts.pop(0)
        rest = ':'.join(parts)
        parts = name.split('?')
        name = parts.pop(0)
        while parts:
            # we check whether there are extra elements
            elem = parts.pop(0)
            elems = elem.split('=')
            n = elems.pop(0)
            if elems: # if it still exists, we have extra values
                v = elems[0]
            if n == 'ex':
                # ex indicates if object must exist for others to be processed
                must_exist = act_vals['value_list']['must_exist']
                must_exist.append(name)
        if rest:
            name = '%s:%s' % (name, rest)
        return name
        
    def construct_config(self):
        opts = self.opts
        files = glob.glob('%s/*' % opts.path)
        # clean filelist
        if opts.construct_config == 'all':
            files = [os.path.split(f)[-1] for f in files if not(os.path.splitext(f)[-1] in USUPPORTED_TYPES)]
            config_name = opts.config
        else:
            files = [opts.construct_config]
            config_name = '%s/%s.cfg' % (opts.path, os.path.split(files[0])[-1].split('.')[0].split()[0])
        
        # do we want to repeat the same config for all pages of a file
        repeat_config = opts.repeat
            
        files_sects = ['%s:%s' % (f, os.path.split(f)[-1].split('.')[0]) for f in files]
        act_vals = {
            'fields' : FIELDS,
            'value_list' : {'skip' : 0, 'must_exist' : []},
            'file_list' : '\n'.join(files_sects),
        }
        # normalise the name
        config_name = os.path.normpath(config_name)
        
        open(config_name, 'w').write(HEAD % act_vals)
        for f in files_sects:
            file_name, section_name = f.split(':')
            act_vals['file_name'] = file_name
            act_vals['section_name'] = section_name
            act_vals['flag_list'] = 'all : source ? %s' % f
            file_path =  os.path.normpath('%s/%s' % (opts.path, file_name))
            wb = xlrd.open_workbook(file_path)
            # get sheet names from workbook
            sheet_names = wb.sheet_names()
            act_vals['pages'] =  ','.join(sheet_names)
            open(config_name, 'a').write(FILE_BLOCK % act_vals)
            # now write the pages
            for page in sheet_names:
                act_vals['page_name'] = page
                sheet = wb.sheet_by_name(page)
                row = sheet.row(0)
                counter = 0
                names = []
                is_first_page = (page == sheet_names[0])
                if (is_first_page and repeat_config) or (not repeat_config):
                    while counter < len(row):
                        n = row[counter].value
                        if n and n.strip():
                            
                            if counter == 0 and n.lower().startswith('$header'):
                                parts = n.split(':')
                                evals = parts[0].split('?')
                                if len(evals) > 1:
                                    skip = evals[-1]
                                    act_vals['value_list']['skip'] = 'skip:%s\n' % skip
                                n = ':'.join(parts[1:])
                            n = n.replace('\n', ' ').strip()
                            if n and n not in names:
                                # check whether more info is appended to the name like
                                # if record is mandatory (eg a parent)
                                if not n.strip().startswith('#'):                                    
                                    n = self.process_name(n, act_vals)
                                    names.append('%s : %s' % (counter, n)  )
                        counter += 1
                    act_vals['names_list'] = '\n'.join(names)
                    # construct a string from value_list
                    value_list =  act_vals['value_list']
                    result_str = ''
                    for k, v in list(value_list.items()):
                        if isinstance(v, str):
                            result_str += v
                        elif isinstance(v, list):
                            result_str += '%s:%s\n' % (k, ','.join(v))
                act_vals['value_list'] = result_str                                
                open(config_name, 'a').write(PAGE_BLOCK % act_vals)
                if not repeat_config:
                    act_vals['value_list'] = {} # for the next run
            
def main(opts):
    handler = partnerHandler(opts)
    if opts.construct_config:
        handler.construct_config()
        return
    handler.process_files()
    # self.error_list.append((line, data, reason,))
    open('errlist.csv', 'w').write('\n'.join([';'.join([str(ll) for ll in l]) for l in handler.error_list]))
    

if __name__ == '__main__':
    usage = "update partner records from excel sheet\n"
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument(
        "-c", "--config",
        action="store", dest="config",
        default = os.path.expanduser('leanbi_excel.cfg'),
        help = 'path to the config file'
    )
    parser.add_argument(
        "-cc", "--construct-config",
        action="store", dest="construct_config",
        default = False,
        help = """construct config file. Either all for all found files, or the name of a file to create 
            a config file for.
            In the case of all, the name of the config file defined with option -c will be used.
            otherwise a config file named similar to the processed file will be stored next to it
        """  
    )
    parser.add_argument(
        "-n", "--name",
        action="store", dest="name",
        help = 'name of the db to handle partners for'
    )
    parser.add_argument(
        "-s", "--sheetnames",
        action="store", dest="sheetnames",
        help = 'sheetnames to handle. One or more sheetnames, split by comma'
    )
    parser.add_argument(
        "-f", "--file-path",
        action="store", dest="path",
        default = os.path.expanduser('~/erp_workbench/customers/leanbi/excelfiles/'),
        help = 'path to the excel files'
    )
    parser.add_argument(
        "-F", "--force",
        action="store_true", dest="force",
        default = False,
        help = 'force reprocessing of a file'
    )
    parser.add_argument(
        "-r", "--reset",
        action="store_true", dest="reset", default = False,
        help = 'reset list of processed files'
    )
    parser.add_argument(
        "-R", "--repeat",
        action="store_true", dest="repeat", default = False,
        help = 'repeat settings for all pages  of a file'
    )
    parser.add_argument(
        "-u", "--user",
        action="store", dest="user", default = 'admin',
        help = 'odoo user'
    )
    parser.add_argument(
        "-dbu", "--dbuser",
        action="store", dest="dbuser", default = 'robert',
        help = 'data base user'
    )
    parser.add_argument(
        "-dbp", "--dbpassword",
        action="store", dest="dbpassword", default = 'admin',
        help = 'data base password'
    )
    parser.add_argument(
        "-dbh", "--dbhost",
        action="store", dest="dbhost", default = 'localhost',
        help = 'data host, default localhost'
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
    if args.config and args.name:
        main(args) #opts.noinit, opts.initonly)
    elif args.construct_config:
        main(args)
    else:
        print(parser.print_help())
