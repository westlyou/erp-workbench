# -*- coding: utf-8 -*-
import xlrd
from argparse import ArgumentParser
import argparse
import os
import sys
import odoorpc
# adapt the following to the acrual sheet from which you get the input
FIELD_LIST = ['xx','Name','Vorname','Anrede','Kategorie','--','Strasse und Hausnummer','PLZ','Ort','Telefon','Mobile','Mail','Eintritt','Austritt','Rechnungsnummer',]
FIELD_MAP = {
    'xx' : None,
    'Name' : 'lastname',
    'Vorname' : 'firstname',
    'Anrede' : 'title',
    #'Kategorie' : 'Kategorie',
    'Strasse und Hausnummer' : 'street',
    'PLZ' : 'zip',
    'Ort' : 'city',
    'Telefon' : 'phone',
    'Mobile' : 'mobile',
    'Mail' : 'email',
#    'Eintritt' : 'Eintritt',
#    'Austritt' : 'Austritt',
#    'Rechnungsnummer' : 'Rechnungsnummer',
}
TAGS = [
    'Einzelmitglied',
    'Familienmitglied',
    'Gruppenmitglied',
]
TAG_DIC = {
    'Einzelmitglied' : 0,
    'Familienmitglied' : 0,
    'Gruppenmitglied' : 0,
}
ANREDEN = ['Herr', 'Frau']
ANREDEN_DIC = {
    'Herr' : 0,
    'Frau' : 0,
}
class partnerHandler(object):
    def __init__(self, opts):
        self.opts = opts
        odoo = odoorpc.ODOO(opts.host, port=opts.port)
        odoo.login(opts.name, opts.user, opts.password)
        self.odoo = odoo
        self.partners = odoo.env['res.partner']
        self.tags = odoo.env['res.partner.category']
        self.titles = odoo.env['res.partner.title']
        self.tag_dic = TAG_DIC
        self.anreden_dic = ANREDEN_DIC
        for tag in TAGS:
            self.tag_dic[tag] = self.tags.browse(self.tags.search([('name', '=', tag)])).id
        for anrede in ANREDEN:
            self.anreden_dic[anrede] = self.titles.browse(self.titles.search([('name', '=', anrede)])).id
            
        
    def search_partner(self, firstname, lastname):
        # return an existing cms page
        firstname = firstname.strip()
        lastname = lastname.strip()
        partners = self.partners
        if firstname and lastname:
            return partners.browse(partners.search([('lastname', 'ilike', lastname), ('firstname', 'ilike', firstname)]))
        else:
            return partners.browse(partners.search([('lastname', 'ilike', lastname)]))
            
    
    def empty_line(self, row):
        return not [c for c in row if c.value]
    
    def handle_excel(self, wbObject=None):
        result = ''
        opts = self.opts
        skip_lines = opts.skip_lines
        header_line = opts.header_line
        if wbObject:
            filedata = wbObject
        else:
            filedata = open(self.opts.input, 'rb').read()
        if hasattr(wbObject, 'download'):
            filedata = wbObject.download().read()
        wb = xlrd.open_workbook(file_contents=filedata)
        # get sheet from workbook
        sheet_names = wb.sheet_names()
        sheet_num = 0
        if self.opts.sheet_name in sheet_names:
            sheet_num = sheet_names.index(self.opts.sheet_name)
        
        sh = wb.sheet_by_index(int(sheet_num))
        counter = -1
        for r in range(sh.nrows):
            counter +=1
            row = sh.row(r)            
            if counter < skip_lines:
                continue
            if self.empty_line(row):
                continue
            if row[0].value:
                continue # skip marked lines
            lastname = row[FIELD_LIST.index('Name')].value
            firstname = row[FIELD_LIST.index('Vorname')].value
            records = self.search_partner(firstname, lastname)
            data = {}
            for f in FIELD_LIST:
                n = FIELD_MAP.get(f)
                if n:
                    fs = row[FIELD_LIST.index(f)].value
                    data[n] = fs
                    #m += ('%s ' % fs)
            if data:
                t_id = self.tag_dic.get(row[4].value)
                if t_id:
                    data['category_id'] = [(6, 0, [t_id])]
                # anrede ..
                data['title'] = self.anreden_dic.get(data['title'], 0)
                # membership
                data['free_member'] = 1
                records[0].write(data)
                print(data['firstname'], data['lastname'])
        #open('/home/robert/xx.txt', 'w').write(result)

def main(opts):
    handler = partnerHandler(opts)
    handler.handle_excel()

if __name__ == '__main__':
    usage = "update partner records from excel sheet\n" 
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument(
        "-n", "--name",
        action="store", dest="name", default=False,
        help = 'name of the db to handle partners for'
    )
    parser.add_argument(
        "-i", "--input",
        action="store", dest="input",
        help = 'path to the excel sheet with updated partnersto process'
    )
    parser.add_argument(
        "-s", "--sheet-name",
        action="store", dest="sheet_name", default = 'Sheet1',
        help = 'name of the sheet in the excel file. Default Sheet1'
    )
    parser.add_argument(
        "-sk", "--skip-lines",
        action="store", dest="skip_lines", default = 1,
        help = 'number of lines to skip. Default 1'
    )
    parser.add_argument(
        "-hl", "--header-line",
        action="store", dest="header_line", default = 0,
        help = 'Line where the Header is found. Must be < skip-lines, Default 0'
    )
    parser.add_argument(
        "-u", "--user",
        action="store", dest="user", default = 'admin',
        help = 'odoo user'
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
    
    args, unknownargs = parser.parse_known_args()
    # is there a valid option?
    if args.input and args.name:
        main(args) #opts.noinit, opts.initonly)
    else:
        print(parser.print_help())
        
