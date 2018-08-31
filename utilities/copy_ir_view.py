#!bin/python
# -*- coding: utf-8 -*-
import mimetypes
from argparse import ArgumentParser
import configparser
import sys
import os
sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
import csv
import psycopg2
import psycopg2.extras

SOURCE = {
    'host': 'localhost',
    'dbname':'afbslocal',
    'user':'robert',
    'pw':'admin',
    'rpcport':8070,
    'dbuser':'odoo',
    'dbpw':'odoo',
    'dbport':5432,
}
TARGET = {
    'host': 'localhost',
    'dbname':'afbschweiz',
    'user':'robert',
    'pw':'admin',
    'rpcport':8069,
    'dbuser':'odoo',
    'dbpw':'odoo',
    'dbport':5432,
}


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
    
tlist = [
    ('name:=:event.event.kanban', 'model:=:event.event'),
    ('name:=:event.event.form', 'model:=:event.event', 'inherit_id:IS:NULL:int'),
]

TABLE = {
    'ir_ui_view' : ['arch_db',],
}

class OdooHandler(object):
    model_dic = {
        'source' : {},
        'target' : {}
        } # here we keep all models that are used during transfer
    field_infos = {}
    field_maps = {}
    handled = []
    
    def __init__(self, opts):
        self.opts = opts
        s = SOURCE
        t = TARGET
        
        conn_string_s = "dbname='%s' user=%s host='%s' password='%s'" % (s['dbname'], s['user'], s['host'], s['pw'])
        conn_string_t = "dbname='%s' user=%s host='%s' password='%s'" % (t['dbname'], t['user'], t['host'], t['pw'])
    
        self.conn_s = psycopg2.connect(conn_string_s)
        self.conn_t = psycopg2.connect(conn_string_t)
        a=1

    def process(self):
        #cs = self.conn_s.cursor()
        cs_d = self.conn_s.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ct_d = self.conn_t.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor = self.conn_t.cursor()
        for table_name, fields in list(TABLE.items()):
            for t in tlist:
                where = ''
                for st in t:
                    if where:
                        where += ' and '
                    f = tuple(st.split(':'))
                    if len(f) > 3:
                        where += "%s %s %s" % f[:3]
                    else:
                        where += "%s %s '%s'" % f
                q = 'select * from %s where %s;' % (table_name, where)
                cs_d.execute(q)
                ct_d.execute(q)
                record_s = cs_d.fetchall()
                record_t = ct_d.fetchall()
                if len(record_s) > 1 or len(record_t) > 1:
                    print('*' * 80)
                    print(q)
                    print('returned more than one record')
                record_s = record_s[0]
                record_t = record_t[0]
                must_commit = False
                # loop over the fields of the record
                for k, v in list(record_s.items()):
                    if isinstance(v, str):
                        print(k, len(v), len(record_t[k]))
                    t_id = record_t['id']
                    if k in fields:
                        if len(v) != len(record_t[k]):
                            uq = 'update %s set %s' % (table_name, k) + ' = %s where id = %s'
                            vals = (v, t_id)
                            cursor.execute(uq, vals)
                            must_commit = True
                if must_commit:
                    self.conn_t.commit()
                    
    def dump_record(self):
        opts = self.opts
        dbname = opts.dbname
        t = TARGET
        conn_string_t = "dbname='%s' user=%s host='%s' password='%s'" % (dbname, t['user'], t['host'], t['pw'])
        conn = psycopg2.connect(conn_string_t)
        cursor = conn.cursor()
        record = opts.record
        query = 'select %s, name, id from %s where id = %s' % (opts.field, opts.table, opts.record)
        cursor.execute(query)
        data = cursor.fetchone()
        df = os.path.expanduser(opts.dumpfile)
        open(df, 'w').write(data[0])
        
    def delete_record(self):
        opts = self.opts
        dbname = opts.dbname
        t = TARGET
        conn_string_t = "dbname='%s' user=%s host='%s' password='%s'" % (dbname, t['user'], t['host'], t['pw'])
        conn = psycopg2.connect(conn_string_t)
        cursor = conn.cursor()
        record = opts.record

        query = 'delete from %s where id in (%s)' % (opts.table, opts.record)
        cursor.execute(query)
        conn.commit()

    def update_record_from_dump(self):
        opts = self.opts
        dbname = opts.dbname
        t = TARGET
        conn_string_t = "dbname='%s' user=%s host='%s' password='%s'" % (dbname, t['user'], t['host'], t['pw'])
        conn = psycopg2.connect(conn_string_t)
        cursor = conn.cursor()
        record = opts.record

        df = os.path.expanduser(opts.dumpfile)
        data = open(df, 'r').read()

        query = 'update %s set %s' % (opts.table, opts.field) + ' = %s where id = %s'
        vals = (data, opts.record)
        cursor.execute(query, vals)
        conn.commit()
        
    def print_all_records(self):
        opts = self.opts
        all_rec = opts.record == 'all'
        t = TARGET
        dbname = opts.dbname
        conn_string_t = "dbname='%s' user=%s host='%s' password='%s'" % (dbname, t['user'], t['host'], t['pw'])
        conn = psycopg2.connect(conn_string_t)
        cursor = conn.cursor()
        if opts.like:
            query = "select %s, name, id from %s where name ilike '%%%s%%';" % (opts.field, opts.table, opts.like)
        elif opts.like:
            query = "select %s, name, id from %s where name ilike '%%%s%%';" % (opts.field, opts.table, opts.like)
        elif opts.viewname:
            query = "select %s, name, id from %s where name = '%s';" % (opts.field, opts.table, opts.viewname)
        elif not all_rec:
            query = 'select %s, name, id from %s where id = %s' % (opts.field, opts.table, opts.record)            
        else:
            query = 'select %s, name, id from %s' % (opts.field, opts.table)  
        cursor.execute(query)
        records = cursor.fetchall()
        reslist = []
        search_list = []
        
        if opts.search:
            search_list = opts.search.split(',')
            
        def check_line(line):
            for search in search_list:
                if line.find(search) > -1:
                    return search
        
        do_remove = opts.remove
        replace_str = ''
        if do_remove and (opts.remove != 'xx'):
            replace_str = opts.remove
            
        for r in records:
            out_string = ''
            if not(search_list) or check_line(r[0]):
                print(bcolors.HEADER + '*' * 80)
                print(r[2], r[1])   
                print('*' * 80, bcolors.ENDC)       
                lines = r[0].split('\n')
                for line in lines:
                    search_found = check_line(line)
                    if search_found:
                        if replace_str:
                            line = line.replace(search_found, replace_str)
                        print(bcolors.FAIL + line + bcolors.ENDC)
                    else:
                        if opts.remove:
                            out_string += line + '\n'
                        print(line)
                print(bcolors.HEADER + '*' * 80)
                print(r[2], r[1])   
                print('*' * 80, bcolors.ENDC)
                reslist.append([r[2], r[1]])
                if opts.remove:
                    uq = 'update %s set %s' % (opts.table, opts.field) + ' = %s where id = %s'
                    vals = (out_string, r[2])
                    cursor.execute(uq, vals)
                    conn.commit()

        print(reslist)
                
    def print_record(self):
        opts = self.opts
        t = TARGET
        dbname = opts.dbname
        conn_string_t = "dbname='%s' user=%s host='%s' password='%s'" % (dbname, t['user'], t['host'], t['pw'])
        conn = psycopg2.connect(conn_string_t)
        cursor = conn.cursor()
        query = 'select %s, name from %s where id = %s' % (opts.field, opts.table, opts.record)
        cursor.execute(query)
        r = cursor.fetchone()
        if r:
            print(bcolors.HEADER + '*' * 80)
            print(r[1])   
            print('*' * 80, bcolors.ENDC)       
            if opts.search:
                lines = r[0].split('\n')
                for line in lines:
                    if line.find(opts.search) > -1:
                        print(bcolors.FAIL + line + bcolors.ENDC)
                    else:
                        print(line)
            else:
                print(r[0])                
            print(bcolors.HEADER + '*' * 80)
            print(r[1])   
            print('*' * 80, bcolors.ENDC)       

def main(opts):
    handler = OdooHandler(opts)
    if opts.dump:
        if not opts.record:
            print(bcolors.FAIL + 'you must specify record' + bcolors.ENDC)
        else:
            handler.dump_record()            
        return
    if opts.updaterecord:
        if not opts.record:
            print(bcolors.FAIL + 'you must specify record' + bcolors.ENDC)
        else:
            handler.update_record_from_dump()            
        return
    if opts.delete_record:
        if not opts.record:
            print(bcolors.FAIL + 'you must specify record' + bcolors.ENDC)
        else:
            handler.delete_record()            
        return
    if opts.record:
        handler.print_all_records()
        return
    if opts.process:
        handler.process()


if __name__ == '__main__':
    usage = "insert_media_in_cms.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument("-t", "--table",
                        action="store", dest="table", default='ir_ui_view',
                        help="define table default ir_ui_view")

    parser.add_argument("-d", "--dbname",
                        action="store", dest="dbname", default='afbschweiz',
                        help="define dbname default 'afbschweiz'")

    parser.add_argument("-dr", "--delete_record",
                        action="store_true", dest="delete_record", default = False,
                        help="delete record from database")

    parser.add_argument("-D", "--dump",
                        action="store_true", dest="dump", default=False,
                        help="dump record into dumpfile")

    parser.add_argument("-df", "--dumpfile",
                        action="store_true", dest="dumpfile", default='~/dump.xml',
                        help="dump record into dumpfile")

    parser.add_argument("-f", "--field",
                        action="store", dest="field", default='arch_db',
                        help="define field to print default arch_db")

    parser.add_argument("-l", "--like",
                        action="store", dest="like", 
                        help="define like for selection of all records")

    parser.add_argument("-N", "--view-name",
                        action="store", dest="viewname", 
                        help="define view name for selection of record")

    parser.add_argument("-r", "--record",
                        action="store", dest="record", 
                        help="define record to print")

    parser.add_argument("-p", "--process",
                        action="store_true", dest="process", default = False,
                        help="copy views from vanilla")

    parser.add_argument("-R", "--remove",
                        action="store", dest="remove", default = '',
                        help="remove/replace lines with searched element, use xx to just remove")

    parser.add_argument("-s", "--search",
                        action="store", dest="search", 
                        help="define search to higligth")

    parser.add_argument("-U", "--updaterecord",
                        action="store_true", dest="updaterecord", default=False,
                        help="update record from dumpfile")

    opts = parser.parse_args()
    main(opts)
