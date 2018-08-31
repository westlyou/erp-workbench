# -*- encoding: utf-8 -*-
import xlwt
import os
file_path = os.path.expanduser('~/afbs_cms_pages_list.xls')

"""


"""
BASE_GROUP_IDS = [4, 11, 68, 82]
AFBS_MANAGER = 83
ID_COL = 0
SEQ_COL = 1
PATH_COL = 2
VIEW_COL = 3
MLIST_COL = 4
GROUPS_COL = 5
START_COL = 6
HEADER_LINE = ['id', 'seq', 'path', 'view', 'mailing list', 'groups']
MODEL_NAMES = [('pages', 'cms.page'), ('mlists', 'mail.mass_mailing.list'), ('newsletter', 'cms.mailing.list'),]

def get_models(self, models):
    "build list of models"
    odoo = self.get_odoo()
    for k,m in MODEL_NAMES:
        if k not in models:
            models[k] = odoo.env[m] 
            
def get_view(cms_page, models):
    "get name of view for cms page"
    return name

def output_children(self, sheet, line_counter, parent_id, level=0, models = {}):
    """
    self: calling instance
    sheet : excel sheet to output to
    line_counter: actual line number to output to
    parent_id: id of the actual page of which we look for children
    level: int denoting the recursion level, starting at 0
    models : dictonary with models to access the records
    """
    # some fonts
    fontN = xlwt.Font()
    fontN.name = 'Helvetica'
    font0 = xlwt.Font()
    font0.name = 'Helvetica'
    font0.colour_index = 2
    font0.bold = True
    st_normal = xlwt.XFStyle()
    st_normal.font = fontN
    st_bold = xlwt.XFStyle()
    st_bold.font = font0  
    
    # make sure the models are loaded
    get_models(self, models)
    # assign them to variables for easy reference
    pages = models.get('pages')
    mlists = models.get('mlists')
    newsletters = models.get('newsletters')
    
    # first we output the "parent"
    parent = pages.browse(parent_id)
    c_index = 0
    view_name = parent.view_id.name
    mlist_name = parent.mass_mailing_object.name and parent.mass_mailing_object.name or ''
    for f in [parent.id, parent.sequence, parent.path, view_name, mlist_name]:
        sheet.write(line_counter, c_index, f, level == 0 and st_bold or st_normal)
        c_index += 1
    # output name on next line below path
    #
    sheet.write(line_counter, START_COL + level, parent.name, level == 0 and st_bold or st_normal)
    print('    ' * level, parent.name)
    if parent.children_ids:
        level += 1
        for child_id in parent.children_ids:
            line_counter += 1
            line_counter = output_children(self, sheet, line_counter, child_id.id, level, models)
    # addvance to the next line for the upper hierarchy
    line_counter += 1
    return line_counter
    

# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes
def run(self, **kw_args):
    odoo = self.get_odoo()
    
    # check whether there is already the output file, if yes, delete it
    if os.path.exists(file_path):
        os.unlink(file_path)
    # create ne workbook
    wb = xlwt.Workbook()    
    # create a new sheet
    sheet = wb.add_sheet('cms list')
    # write header
    c_index = 0
    for f in HEADER_LINE:
        sheet.write(0, c_index, f)
        c_index += 1
    
    # keep a list of handled id's
    seen_ids = {}
    line_counter = 0
    models = {}
    get_models(self, models)
    pages = models['pages']
    main_pages = pages.search([('path','=', '/')], order='sequence')
    level = 0
    for parent_id in main_pages:
        line_counter += 1
        line_counter = output_children(self, sheet, line_counter, parent_id, level, models)
    
    wb.save(file_path)    
    #for user in users:
        #if AFBS_MANAGER in [gid.id for gid in user.groups_id]:
            #print 'manager:', user.name
            #continue
        #print user.name, user.groups_id, 
        #user.groups_id = base_groups
        #print user.groups_id
    