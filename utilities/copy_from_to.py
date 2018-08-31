#!bin/python
# -*- coding: utf-8 -*-
import mimetypes
from argparse import ArgumentParser
import configparser
import sys
import os
sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
from cc_data import DB_INFO
from copy import deepcopy

"""
copy_from_to.py
---------------
Copy objects from one database to the next

"""

"""
[source]
host: localhost
dbname:breitschtraeff92
rpcuser:admin
rpcpw:admin
rpcport:8069
dbuser:odoo
dbpw:odoo
dbport:5432

[target]
host: localhost
dbname:breitschtraeff10
rpcuser:admin
rpcpw:admin
rpcport:8069
dbuser:odoo
dbpw:odoo
dbport:5432


"""
import odoorpc
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
    
hlist = [
    'host',
    'rpcuser',
    'rpcpw',
    'rpcport',
    'dbuser',
    'dbpw',
    'dbport',
]
TARGETDBNAME = 'dbname'
SOURCEDBNAME = 'dbname'


class OdooHandler(object):
    model_dic = {
        'source' : {},
        'target' : {}
        } # here we keep all models that are used during transfer
    field_infos = {}
    field_maps = {}
    handled = []
    id_map = {}
    
    def __init__(self, opts):
        self.opts = opts
        config = configparser.ConfigParser()
        cp = os.path.normpath('%s/%s' % (opts.config_path, opts.config))
        config.read(cp)
        sections = config.sections()
        if (not 'source' in sections) or (not 'target' in sections):
            print(bcolors.FAIL + 'either source or option missing in %s' % opts.config + bcolors.ENDC)
            return
        tinfo = {}
        sinfo = {}
        
        for sect in ['source', 'target']:
            idic = sinfo
            if sect == 'target':
                idic = tinfo
            for o in hlist:
                try:
                    idic[o] = config.get(sect, o)
                except:
                    print(bcolors.FAIL + 'problem with %s in section %s' % (sect, o) + bcolors.ENDC)
        sinfo['dbname'] = config.get('source', SOURCEDBNAME)
        tinfo['dbname'] = config.get('target', TARGETDBNAME)
        # if the source an target pots are the same
        # we need only one connection
        sodoo = odoorpc.ODOO(sinfo['host'], port=sinfo['rpcport'])
        todoo = odoorpc.ODOO(tinfo['host'], port=tinfo['rpcport'])
        
        sodoo.login(sinfo['dbname'], sinfo['rpcuser'], sinfo['rpcpw'])
        todoo.login(tinfo['dbname'], tinfo['rpcuser'], tinfo['rpcpw'])
        self.sodoo = sodoo
        self.todoo = todoo
        
        self.db_info = deepcopy(DB_INFO)
        
    def add_to_id_map(self, model_name, old_id, new_id):
        """
        Args:
            model_name (string) : table for which we have a set of id's
            old_id     (int)    : old id
            old_new    (int)    : new id
        """
        m = self.id_map.get(model_name)
        if m:
            m[old_id] = new_id
        else:
            self.id_map[model_name] = {old_id : new_id}
            
    def map_ids(self, model_name, ids, to_new = True):
        """
        Args:
            model_name (string) : table for which we have a set of id's
            ids        (list)   : list of integers to map
            to_new     (boolean): if set map old to new
        Returns:
            list of mapped ids
        """
        m = self.id_map.get(model_name, {})
        if to_new:
            return [m.get(i) for i in ids]
        return [k for k,i in list(m.items()) if i in ids]
            
    def get_models(self, mname):
        """
        make sure models are loaded for both source an target
        
        :mname  model name like 'res.user'
        
        sidefect: 
            models arrre loaded
        return:
            nothing
        """
        # try to load from cache
        if mname in self.model_dic['source']:
            return self.model_dic['source'][mname], self.model_dic['target'][mname]
        # load and add to cache
        self.model_dic['source'][mname] = self.sodoo.env[mname]
        self.model_dic['target'][mname] = self.todoo.env[mname]
        return self.model_dic['source'][mname], self.model_dic['target'][mname]
    
    def process_minfo(self, minfo):
        """
        """
        field_info = {
            'simple_fields' : minfo['simple_fields'],
            'one2many_fields' : [],
            'many2one_fields' : [],
            'many2many_fields' : [],
        }
        field_map = {}
        for fname in  field_info['simple_fields']:
            field_map[fname] = None
            
        # make sure all modells for all dependent records are loaded
        if 'one2many_fields' in minfo:
            for fname, finfo in list(minfo['one2many_fields'].items()):
                field_info['one2many_fields'].append(fname)
                field_map[fname] = finfo
                self.handle_block(finfo[0], process_records = False)
        if 'many2one_fields' in minfo:
            for fname, finfo in list(minfo['many2one_fields'].items()):
                field_info['many2one_fields'].append(fname)
                field_map[fname] = finfo
                self.handle_block(finfo[0], process_records = False)
        if 'many2many_fields' in minfo:
            for fname, finfo in list(minfo['many2many_fields'].items()):
                field_info['many2many_fields'].append(fname)
                field_map[fname] = finfo
                self.handle_block(finfo[0])
        return field_info, field_map
        
    def process_records(self, mname, minfo = {}, callers = [], filter = []):
        """
        Args:
            mname  (string)       : name of the module to process
            minfo  (dict)         : info about the module
            callers(list)         : list of models that called process_records
                                    stop recursion id a dependnt model is in 
                                    that list so we avoid loops
        """
        "filter records from model and transfer them to the target"
        callers.append(mname)
        smodel, tmodel = self.get_models(mname)
        #if not minfo:
            #minfo = DB_INFO[mname]
        
        if not filter:    
            filter = minfo.get('filter', [])
        source_records = smodel.search(filter)
        # loop trough records, build one after the other
        simple_fields = minfo.get('simple_fields', [])
        many2one_fields = minfo.get('many2one_fields', [])
        one2many_fields = minfo.get('one2many_fields', [])
        many2many_fields = minfo.get('many2many_fields', [])
        for sr in source_records:
            record = smodel.browse(sr)
            old_id = record.id
            print(getattr(record, filter and filter[0][0] or 'id'))
            new_r_dic = {}
            for f in simple_fields:
                new_r_dic[f] = getattr(record, f)
            # now we we have a record with all the simple fields set
            # we dig into the linked fields
            
            #'many2one_fields' : {
                #'title' : ('res.partner.title','title'),
                #'parent_id' : ('res.partner', 'id'),
                #'state_id': ("res.country.state", "state"),
                #'country_id': ('res.country', 'id'),
                #'user_id': ('res.users', 'id'), # 'Salesperson'
                #'company_id': ('res.company', 'id'), # 'Company'
            #},
            for fm2o, fm2o_info in list(many2one_fields.items()):
                # in a many2one_field the actual record points to an existing
                # record in an other table
                # we therefore have to make sure, that this other record exists
                
                # first copy the value of the field from the old record to the new
                new_val = getattr(record, fm2o)
                if len(new_val):
                    new_r_dic[fm2o] = new_val[0].id
                # before we can save the new record, the related records must  exist
                # to do so, we call process_records recursively
                pname = fm2o_info[0]
                # construct a filter, so we only get the record we are interested in
                local_filter = (fm2o_info[1], '=', new_val)
                if not fm2o_info[0] in self.handled and not fm2o_info[0] in callers:
                    self.process_records(fm2o_info[0], self.db_info[pname], filter = local_filter)               
                
            #'one2many_fields' : {
                #'child_ids': ('res.partner', 'parent_id'),
                #'bank_ids':('res.partner.bank', 'partner_id'),            
                #'user_ids' : ('res.users', 'partner_id'),
            #},
            for f2m, f2m_info in list(one2many_fields.items()):
                # in a one2many field a value in our record, is used to 
                # link a record in a foreing table to the actual record
                # we therefore have to make sure, that the foreing table is loaded
                # and all recors pointing to the actual record are copied
                
                # first copy field to actual record
                #new_r_dic[f2m] = getattr(record, f2m)
                pass
                # we will only be able to copy old records that point to the actual record
                # when we have created the actual record
            
            # now create the new record
            new_ids = self.map_ids(mname, [old_id])
            if new_ids:
                new_id = new_ids[0]
            if not new_id:
                new_id = tmodel.create(new_r_dic)
                self.add_to_id_map(mname, old_id, new_id)
            
            # make sure the records that point to this record are also created
            for f2m, f2m_info in list(one2many_fields.items()):
                # do not try to copy if it is a recursive relation like a 
                # person related to a company
                pname = f2m_info[0]
                if pname != mname:
                    if not pname in self.handled and not pname in callers:
                        self.process_records(pname, self.db_info[pname]) 
            
            # handle the many2many fields
            #'many2many_fields' : {
                #'category_id': ('res.partner.category', 'partner_id', 'category_id'),
            #}
            #'many2many_fields' : {
                #'rule_groups': ('ir.rule', 'rule_group_rel', 'group_id', 'rule_group_id', 'Rules'),
                #'users': ('res.users', 'res_groups_users_rel', 'gid', 'uid'),
                #'menu_access': ('ir.ui.menu', 'ir_ui_menu_group_rel', 'gid', 'menu_id'),
                #'view_access': ('ir.ui.view', 'ir_ui_view_group_rel', 'group_id', 'view_id'),
                #'model_access': ('ir.model.access', 'group_id', 'Access Controls'),
            #}
            for fm2m, fm2m_info in list(many2many_fields.items()):
                fm2m_info = list(fm2m_info)
                fm2m_model = fm2m_info.pop(0)
                # the second element is not allways the name of the relation
                if fm2m_info[0].endswith('_rel'):
                    rel = fm2m_info.pop(0)
                else:
                    # we have to construct rel
                    rel = ('%s_%s_rel' % (mname, fm2m_model)).replace('.', '_')
                child_id_name = fm2m_info.pop(0)
                parent_id_name = fm2m_info.pop(0)
                
                # make sure the values are copied
                if not rel in self.handled  and not rel in callers:
                    self.process_records(rel, self.db_info[rel]) 
                # collect all related ids
                # this we do by directly quering the table rel
                q = 'select %s from %s where %s = %s' % (parent_id_name, rel, child_id_name, )
                self.t_conn.execute(q)
                old_ids = self.t_conn.fetchmany()
                if old_ids:
                    old_ids = [o[0] for o in old_ids]
                # map the old ids to the new ones
                self.map_ids(mname, old_ids)
            
        # remove ourselfs from the list of callers
        callers.pop() 
        # add ourselfs to the list of handled models
        # so we do not process the same model twice
        self.handled.append(mname)
        print('hadled:', mname)
     
    def handle_block(self, mname, process_records = False):
        """
        handle a block of records from DB_INFO
        Args:
            mname (string)  : name of the module to process
            process_records (boolean):  if True process filtered records
                                        if it is False, only load model info into self.
                                        self.model_dic so we can use it while processing 
                                        single records
        """
        if mname in self.handled:
            return
        if process_records:
            # keep a copy of handled, so we can use it after finishing initilization
            handled = self.handled[:]
        self.handled.append(mname)
        opts = self.opts
        # what fields do we want to handle?
        minfo = self.db_info[mname]
        if not minfo:
            return # a model we do not want to handle like 'ir.module.category'
        # we get the source and target model
        smodel, tmodel = self.get_models(mname)
        # go recursively trough all records
        # load the needed models and build global field_infos and field_maps
        field_info, field_map = self.process_minfo(minfo)
        self.field_infos[mname] = field_info
        self.field_maps[mname] = field_map
        # if we need to process_records
        if process_records:
            # restore handled after initialization
            self.handled = handled
            self.process_records(mname, minfo)
            
    def install_languages(self):
        """
        install all languages in the target,
        that are installed in the source
        
        sidefect:
            in both db the same languages are loade
            
        return:
            nothing        
        """
        return
        self.handled.append('base.language.install')
        # what fields do we want to handle?
        # we get the source and target model
        sinstall, tinstall = self.get_models('base.language.install')        
        slang, tlang = self.get_models('res.lang')
        tls = tlang.search([('id', '>', 0)])
        not_installed = [l for l in slang.search([('id', '>', 0)]) if l not in tls]
        for l in not_installed:
            code = slang.browse(l)[0].code
            lx = tinstall.create({'lang' : code})
            tinstall.lang_install([lx])
            tlang.load_lang(code)
        a=1

def main(opts):
    handler = OdooHandler(opts)
    handler.install_languages()
    handler.handle_block('res.users', process_records = True)


if __name__ == '__main__':
    usage = "insert_media_in_cms.py -h for help on usage"
    parser = ArgumentParser(usage=usage)
    dp = '/'.join(os.path.split('%s' % (  __file__))[:-1])
    parser.add_argument("-c", "--config",
                        action="store", dest="config", default='cft.cfg',
                        help="config file to read, default=cft.cfg'")

    parser.add_argument("-cp", "--config-path",
                        action="store", dest="config_path", default='%s' % dp,
                        help="Path to the config file, default=%s" % dp)

    parser.add_argument("-H", "--host",
                        action="store", dest="host", default='localhost',
                        help="define host default localhost")

    parser.add_argument("-d", "--dbname",
                        action="store", dest="dbname", default='afbsdemo',
                        help="define host default ''")

    parser.add_argument("-U", "--rpcuser",
                        action="store", dest="rpcuser", default='admin',
                        help="define user to log into odoo default admin")

    parser.add_argument("-P", "--rpcpw",
                        action="store", dest="rpcpw", default='admin',
                        help="define password for odoo user default 'admin'")

    parser.add_argument("-PO", "--port",
                        action="store", dest="port", default=8069,
                        help="define rpc port default 8069")

    opts = parser.parse_args()
    main(opts)
