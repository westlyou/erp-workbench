
# -*- coding: utf-8 -*-

from registry.default_handler import BaseHandler
from presets_config import BASE_PATH
from bcolors import bcolors

"""
downloads/odoo-10.0.post20180708/odoo/addons/account/models/account.py
{u'bank_acc_number': u'12345',
 u'bank_id': 2,
 u'company_id': 1,
 u'currency_id': False,
 u'display_on_footer': True,
 u'inbound_payment_method_ids': [[6, False, [1]]],
 u'outbound_payment_method_ids': [[6, False, [2]]],
 u'type': u'bank'}

  if vals.get('type') in ('bank', 'cash'):
 wir müssen einen default kredit debit account haben
 default_account = vals.get('default_debit_account_id') or vals.get('default_credit_account_id')

"""
 

class ReadYamlBankaccountHandler(BaseHandler):
    """ provide a handler for situation, where XXXXXX

    Attributes:
        _yaml_name {string} -- it is the name of the yaml file to load
         more than one handler can use the same file. It will only use
         those elements, for which the elements handler name is the handlers name.
         The elements handler name is set when the element is registered.
    """
    _yaml_name = 'base_preset'
    _app_group = 'bank'
    _app_index = 2

    def run_handler(self):
        """run_handler does the handlers job

        Returns:
            {dict} -- a dictonary with two entries:
                'yaml_data' : a list of yaml dicts updated with new_ids of the created
                    objects and a values dict with the values to create the object
                'parent_data': a dict with parent_data, with the result of calling the parent handler
                'model' : the odoo model this handler deals with
        """
        # collect the data from the yaml file and install all 
        # parent bank accounts
        yaml_data = self._run_handler_start()
        model = yaml_data['model']
        Model = self.Model
        if not self._test_mode:
            # we have the accounts in values
            # each account has a field bank_id
            # this bank _id we find in the parent data
            # under the 'banks' key
            values = yaml_data.get('values', {})
            accounts = list(values.get('accounts', {}).values())
            banks = values['parent_data']['values']['banks']
            for account in accounts:
                bank_id = account.get('bank_id')
                if bank_id:
                    obj_id_bank = banks.get(bank_id, {}).get('new_object_id')
                if obj_id_bank:
                    # we have a pointer to the bank, and now can construct a 
                    # bank journal 
                    vals = {
                        'bank_id' : obj_id_bank,
                        'type' : 'bank',
                        'acc_number' : account.get('acc_number', '')
                    }
                    
                    new_id = 0
                    # we know, that acount numbers must be unique per bank and company (or only company ??)
                    exists = Model.search([('acc_number', '=', vals['acc_number'])])
                    if exists:
                        account['new_object_id'] = exists[0]
                    else:
                        try:
                            new_id = Model.create(vals)
                            account['new_object_id'] = new_id
                            self._run_handler_end(safe = True)
                        except Exception as e:
                            print(bcolors.FAIL)
                            print('*' * 80)
                            print('failed to create a record for %s using %s' % (model, vals))
                            print( str(e))
                            print(bcolors.ENDC)
                            account['new_object_id'] = None
    
        return yaml_data
                

"""HANDLER_LIST assigns classes external names
"""
HANDLER_LIST = [('ReadYamlBankaccountHandler', 'read_yaml_bankaccount')]
