
# -*- coding: utf-8 -*-


import datetime
import os

import xlrd
from bcolors import bcolors
from presets_config import BASE_PATH
from registry.default_handler import BaseHandler

HEADER_DIC = {
    'Gruppe' : 0,
    'BCNr' : 1,
    'Filial-ID' : 2,
    'BCNr neu' : 3,
    'SIC-Nr' : 4,
    'Hauptsitz' : 5,
    'BC-Art' : 6,
    'gültig ab' : 7,
    'SIC' : 8,
    'euroSIC' : 9,
    'Sprache' : 10,
    'Kurzbez.' : 11,
    'Bank/Institut' : 12,
    'Domizil' : 13,
    'Postadresse' : 14,
    'PLZ' : 15,
    'Ort' : 16,
    'Telefon' : 17,
    'Fax' : 18,
    'Vorwahl' : 19,
    'Landcode' : 20,
    'Postkonto' : 21,
    'SWIFT' : 22,
}
class ReadYamlBankHandler(BaseHandler):
    """ provide a handler for situation, where XXXXXX

    Attributes:
        _yaml_name {string} -- it is the name of the yaml file to load
         more than one handler can use the same file. It will only use
         those elements, for which the elements handler name is the handlers name.
         The elements handler name is set when the element is registered.
    """
    _yaml_name = 'base_preset'
    _app_group = 'bank'
    _app_index = 1

    def get_actual_bank_list_from_excel(self):
        """the list of swiss banks is maintained by six
        and can be downloaded as excel sheet

        this method should check for an actual version 
        as it is implemented now, we just read an existing one
        """
        excel_path = '%s/divers/%s' % (self.manager.base_path, 'bcbankenstamm_d.xls')
        if os.path.exists(excel_path):
            wb = xlrd.open_workbook(excel_path)
        else:
            print (bcolors.FAIL + '*' * 80)
            print ('File not found' % excel_path)
            print ('*' * 80 + bcolors.ENDC)
            return
            
        # we need to skip the to rows
        skip = 1
        # get sheet from workbook
        first_sheet = wb.sheet_by_index(0)
        banks_dic = {}
        hd = HEADER_DIC
        for l_index in range(first_sheet.nrows):
            if l_index < skip:
                continue
            # using ('Filial-ID', 'BCNr neu' or 'BCNr') is a key
            # line -> [u'01', u'100  ', u'0000', u'     ', u'001008', u'100  ', u'1', u'20170911', u'1', u'3', u'1', u'SNB            ', u'Schweizerische Nationalbank                                 ', u'B\xf6rsenstrasse 15                   ', u'Postfach 2800                      ', u'8022      ', u'Z\xfcrich                             ', u'058 631 00 00     ', u'                  ', u'     ', u'  ', u'30-5-5      ', u'SNBZCHZZXXX   ']

            line = [(str(l).strip() + '') for l in first_sheet.row_values(l_index)]
            bdic_index = (line[hd['Filial-ID']], (line [hd['BCNr neu']].strip() or line[hd['BCNr']].strip()))
            banks_dic[
                bdic_index
            ] = line
            # remove '*' in front of postconto
            v = line[hd['Postkonto']]
            v = v.replace('*', '')
            banks_dic[bdic_index][hd['Postkonto']] = v

        return banks_dic

    def run_handler(self):
        """run_handler does the handlers job

        Returns:
            {dict} -- a dictonary with two entries:
                'yaml_data' : a list of yaml dicts updated with new_ids of the created
                    objects and a values dict with the values to create the object
                'parent_data': a dict with parent_data, with the result of calling the parent handler
                'model' : the odoo model this handler deals with
        """
        # banks_dic is using ('Filial-ID', 'BCNr neu' or 'BCNr') is a key
        # items  -> [u'01', u'100  ', u'0000', u'     ', u'001008', u'100  ', u'1', u'20170911', u'1', u'3', u'1', u'SNB            ', u'Schweizerische Nationalbank                                 ', u'B\xf6rsenstrasse 15                   ', u'Postfach 2800                      ', u'8022      ', u'Z\xfcrich                             ', u'058 631 00 00     ', u'                  ', u'     ', u'  ', u'30-5-5      ', u'SNBZCHZZXXX   ']
        banks_dic = self.get_actual_bank_list_from_excel()
        # 
        yaml_data = self._run_handler_start()
        # parent_data = base_dict['parent_data'] # parent_data not needed here
        Model = self.Model
        hd = HEADER_DIC
        # we need to create n bank objects
        if not self._test_mode:
            for yaml_bank in list(yaml_data.get('values', {}).get('banks', {}).values()):
                swift = [yaml_bank.get('swift', ''), 'SWIFT', '', 'bic']
                bcnr = [yaml_bank.get('bcnr', ''), 'BCNr neu', 'BCNr', 'clearing']
                postac = [yaml_bank.get('postac', ''), 'Postkonto', '', 'ccp']
                city = [yaml_bank.get('city', ''), 'Ort', '', 'city']
                zip_  = [yaml_bank.get('zip', ''), 'PLZ' , '', 'zip']
                street = [yaml_bank.get('street', ''), 'Domizil', '', 'street']
                # now we loop trough the values, and look for the best fitting entry in the bancs dic
                fitting = {}
                # start collecting banks that could fit
                for what in [swift, bcnr, postac, city, zip_, street]:
                    use_this = fitting or banks_dic
                    if what[0]:
                        fitting = {
                            b_item[0] : b_item[1] 
                            for b_item in list(banks_dic.items()) 
                            if (str(what[0]) + '') == (
                                # if what[2] has a value we must OR two posible fields
                                what[2] and (b_item[1][hd[what[2]]] or b_item[1][hd[what[1]]])
                                or
                                b_item[1][hd[what[1]]]
                            )
                        }
                if fitting:
                    found_existing = False
                    for b_item in list(fitting.items()):
                        # we search an existing bank, which normaly sould yield
                        search_list = []
                        for what in [swift, bcnr, postac, city, zip_, street]:
                            v = b_item[1][hd[what[1]]]
                            if v:
                                # the excel has a * in front of the post account
                                if what[3] == 'ccp':
                                    v = v.replace('*', '')
                                search_list.append((what[3], '=', v))
                        found_existing = Model.search(search_list)
                        if found_existing:
                            if isinstance(found_existing, list):
                                found_existing = found_existing[0]
                            break
                if found_existing:
                    yaml_bank['new_object_id'] = found_existing
                else:
                    new_vals = {'name' : yaml_bank['name']}
                    for what in [swift, bcnr, postac, city, zip_, street]:
                        v = what[0]
                        if v:
                            new_vals[what[3]] = v
                    new_id = 0
                    try:
                        new_id = Model.create(new_vals)
                        yaml_bank['new_object_id'] = new_id
                        self._run_handler_end()
                    except Exception as e:
                        self._run_handler_end()
                        print(bcolors.FAIL)
                        print('*' * 80)
                        print('failed to create a record for %s using %s' * (Model, new_vals))
                        print(str(e))
                        print(bcolors.ENDC)
                        yaml_bank['new_object_id'] = None

        return yaml_data
                

"""HANDLER_LIST assigns classes external names
"""
HANDLER_LIST = [('ReadYamlBankHandler', 'read_yaml_bank')]
