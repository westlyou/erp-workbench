# -*- coding: utf-8 -*-

"""
This modude provides a template for a new handler
"""

HANDLER_TEMPLATE = '''
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from registry.default_handler import BaseHandler
from presets_config import BASE_PATH
from bcolors import bcolors
 

class %(klass)s(BaseHandler):
    """ provide a handler for situation, where XXXXXX

    Attributes:
        _yaml_name {string} -- it is the name of the yaml file to load
         more than one handler can use the same file. It will only use
         those elements, for which the elements handler name is the handlers name.
         The elements handler name is set when the element is registered.
        _app_group {string} -- to what group of apps does the handler belong like company, project ..
        _app_sequence -- what sequence within the _app_group
    """
    _yaml_name = '%(yaml_name)s'
    _app_group = 'xxx' # please set
    _app_index = 0 # please set

    def run_handler(self):
        """run_handler does the handlers job and creates a new item
 
        Returns:
            {dict} -- yaml_data with three new elements added to it: 
                'parent_data': a dict with parent_data, with the result of calling the parent handler
                'values': a dict used to create the new object
                'new_object_id' : the id of the new object
        """
        # 
        yaml_data = self._run_handler_start()
        # parent_data = base_dict['parent_data'] # parent_data not needed here
        Model = self.Model
        if not self._test_mode:
            new_id = 0
            try:
                values = yaml_data['values']
                old_id = yaml_data.get('new_object_id')
                if old_id:
                    obj = Model.browse([old_id])
                    obj.write(values)
                else:
                    new_id = Model.create(values)
                    yaml_data['new_object_id'] = new_id
                self.yaml_data = yaml_data
                self._run_handler_end()
            except Exception, e:
                print(bcolors.FAIL)
                print('*' * 80)
                print(str(e))
                print('failed to create or update a record for% %s using %%s' %% (Model, values))
                print(bcolors.ENDC)
                yaml_data['new_object_id'] = None

        return yaml_data
                

"""HANDLER_LIST assigns classes external names
"""
HANDLER_LIST = [('%(klass)sHandler', '%(yaml_name)s')]
'''