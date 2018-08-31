# -*- coding: utf-8 -*-
import xlrd
from argparse import ArgumentParser
import argparse
import os
import odoorpc
#filedata = open('%s/%s' % (PATH, NAME), 'rb').read()
#SIAImportExportHandler(self.portal).handleSheet(filedata)
SITE_DEFAULT = {'redirect_to_id': False,
 'type_id': 1,
 'image': False,
 'nav_include': False,
 'no_dashboard': False,
 'is_website_images': False,
 'related_ids': [],
 'sub_page_view_id': False,
 'tag_ids': [],
 'list_types_ids': [],
 '': 5,
 'website_published': False,
 'body': '<p><br></p>',
 'description': False,
 'view_group_ids': [],
 #u'view_id': 1242,
 #u'group_public_id': 4,
 'is_public': False,
 'sub_page_type_id': False,
 'name': '',
 'work_group': [],
 'default_view_item_id': False,
 'published_date': False,}

FLAGS = ['nav_include', 'no_dashboard', 'is_public',]

class menuHandler(object):
    max_depth = 0 # no children names after that
    
    def __init__(self, opts):
        self.opts = opts
        odoo = odoorpc.ODOO(opts.host, port=opts.port)
        odoo.login(opts.name, opts.user, opts.password)
        self.odoo = odoo
        self.pages = odoo.env['cms.page']
        
    def search_root(self, name):
        # return an existing cms page
        pages = self.pages
        root = None
        result = pages.search([('name', '=', name)])
        if result:
            return pages.browse(result[0])
        # we need to create a page
        root = pages.create({'name' : name})
        return pages.browse(root)       
            
    def update_flags(self, child, flags):
        values = {}
        # reset all flags
        for f in FLAGS:
            values[f] = False #set the onses to true which are set in the excel sheet
        for f in flags:
            values[f] = True
        child.write(values)

    def search_child(self, parent, name, path, flags):
        # we go down the hierarchy and search the page pointed to by the hierarchy
        pages = self.pages
        #root = pages.browse(hierarchy[0].id)
        #parent = root
        data = SITE_DEFAULT.copy()
        data['name'] = name
        data['parent_id'] = parent.id
        data['path'] = '/'.join([p.name for p in path if p])
        new = False
        for f in flags:
            data[f] = True
        for child in parent.children_ids:
            #child = pages.browse(cid.id)
            if child.display_name == name:
                return child, new
        # we need to create a page
        child = self.pages.create(data)
        return parent.browse(child), True      
        
            
    def build_header(self, row):
        counter = 0
        depth = 0
        result = {'root' : counter, 'redirect' : 0}
        # get name
        while counter < len(row) and row[counter].value != 'name':
            counter += 1
        if row[counter].value != 'name':
            raise ValueError('column name not found')
        result['name'] = counter
        # get children
        while counter < len(row) and not row[counter].value.startswith('child'):
            counter += 1
        if not row[counter].value.startswith('child'):
            raise ValueError('no children found')
        result['childs'] = counter
        depth = 0
        while counter < len(row) and row[counter].value.startswith('child'):
            counter += 1
            depth += 1
        # get redirect
        while counter < len(row) and not row[counter].value.startswith('redirect'):
            counter += 1
        if row[counter].value.startswith('redirect'):
            result['redirect'] = counter

        # get flags
        flags = []
        while counter < len(row) and not row[counter].value.startswith('flag'):
            counter += 1
        while counter < len(row) and row[counter].value.startswith('flag'):     
            flags.append(counter)
            counter += 1
        result['flags'] = flags

        result['depth'] = depth
        self.max_depth = result['redirect']
        return result
    
    def empty_line(self, row):
        c1 = row[0].value
        if c1 and c1.strip().startswith('#'):
            return True
        return not [c for c in row[:self.max_depth] if c.value]
    
    def handle_excel(self, wbObject=None):
        opts = self.opts
        update = opts.update
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
        header = {}
        for r in range(sh.nrows):
            counter +=1
            row = sh.row(r)            
            if counter == header_line:
                header = self.build_header(row)
                break
            if counter < skip_lines:
                continue
        # now for the values
        root = None
        counter = -1
        running = [None] * 10 # current hierarchy
        for r in range(sh.nrows):
            path = []
            counter +=1
            if counter < skip_lines:
                continue
            row = sh.row(r)
            if self.empty_line(row):
                continue
            root_name = row[header['root']].value
            if root_name:
                root=self.search_root(root_name)
                running[0] = root
            # get flags:
            flags = []
            for fpos in header['flags']:
                fvalue = row[fpos].value
                if fvalue and fvalue.strip():
                    flags.append(fvalue.strip())
            if row[header['name']].value:
                entry, new = self.search_child(running[0], row[header['name']].value, running, flags)
                running[1] = entry
                if (not new) and update:
                    self.update_flags(entry, flags)
            for ci in range(header['depth']):
                pos = header['name'] + 1 + ci
                n = row[pos].value
                if n:
                    entry, new = self.search_child(running[1+ci], n, running, flags)
                    running[2+ci] = entry
                    if (not new) and update:
                        self.update_flags(entry, flags)
                
                
            
            


def main(opts):
    handler = menuHandler(opts)
    handler.handle_excel()

if __name__ == '__main__':
    usage = "add menues to an odoo instance\n" 
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument(
        "-n", "--name",
        action="store", dest="name", default=False,
        help = 'name of the db to add menu items to'
    )
    parser.add_argument(
        "-i", "--input",
        action="store", dest="input",
        help = 'path to the excel sheet to process'
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
        help = 'Line where the Header is founf. Must be < skip-lines, Default 0'
    )
    parser.add_argument(
        "-u", "--user",
        action="store", dest="user", default = 'admin',
        help = 'odoo user'
    )
    parser.add_argument(
        "-U", "--update",
        action="store_true", dest="update", default = False,
        help = 'update pages'
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
        
    