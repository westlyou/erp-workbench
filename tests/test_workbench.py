import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scripts import create_site



"""
run it with:
bin/python -m unittest discover tests
"""

class TestManager(unittest.TestCase):

    def setUp(self):
        self.manager = Manager('presettest', 'admin', 'admin')

    def test_get_base_preset(self):
        """ get_base_preset should return a dictonary with info on the objects
            we have to handle
            this must return a dictionary
            with a description of objects that each erp site needs to have set
            It muss have a structure 'company'
        """
        data = self.manager.get_yaml_file('base_preset')
        company = data.get('company')
        self.assertTrue(company)
        for n in ['model', 'model_help']:
            self.assertTrue(company[n], '%s is missing %s' % ('company', n))
        # all other elements need these fields also
        for k, v in list(data.items()):
            for n in ['model', 'model_help']:
                self.assertTrue(v[n], '%s is missing %s' % (k, n))

    def test_set_test_mode(self):
        """some of the tests need not change anything on the running databas
        here setting a test_mode flag can help
        """
        self.manager.set_test_mode()
        registry = self.manager.handler_registry
        for handler in list(registry.values()):
            self.assertTrue(handler._test_mode)

    def shortDescriptiontest_get_handlers_from_base_preset(self):
        """ each config item needs a handler
            either that handler is explicitly defind with the keyword handler
            or a base handler is used
            all of these handlers must by calling handler.get_yaml_file(preset_name)
        """
        data = self.manager.get_yaml_file('base_preset')
        for _, v in list(data.items()):
            handler = v['handler']
            self.assertTrue(self.manager.get_handler_by_name(handler), 'Manager has no handler %s' % handler)

    def test_run_handlers(self):
        """
        We want to apply each handler from the base template and check
        whether it does create an object correctly.
        To do so, we ask each handler what model it deals with.
        With the name of the model, we get test data for this model
        from the folder with test data.
        """
        data = self.manager.get_yaml_file('base_preset')
        for _, v in list(data.items()):
            handler = v['handler']
            model = v['model']
            handler = self.manager.get_handler_for_model(model)[0]
            handler.run_handler()
   
    def test_run_all_base_handlers(self):
        """
        ckeck whether all base_handler are run, when we set the flag run_all
        """
        model = 'res.company'
        handler = self.manager.get_handler_for_model(model)[0]
        handler._check_and_run_basehandlers(run_all=True)

    def test_get_app_sequence(self):
        """ the apps should be presented to the user in a repeatable fasion
            This is achieved handling an a sequence of app names
            and within the app name a sequnce
        """
        sequence = self.manager.get_app_sequence()
        first_key = list(sequence.keys())[0]
        first_name = sequence[first_key].name # the keys of the index start at 1!!
        self.assertTrue(first_name == 'read_yaml_company', 'name of first index element is %s, should be read_yaml_company'% first_name)

    def test_get_handler_for_model(self):
        """get the handler that can deal with a model
        so we can set the data for it
        """
        model = 'res.company'
        result = self.manager.get_handler_for_model(model)
        self.assertTrue(result and result[0].model == model)

    def test_set_yaml_data_for_model(self):
        """we want to write out yaml data so we can
        read it in and creat objects
        """
        data = {'name' : 'the testers heaven'}
        model = 'res.company'
        self.manager.set_yaml_data_for_model(model, data)
        handler = self.manager.get_handler_for_model(model)[0]
        handler_data = handler.yaml_data
        self.assertEqual(data['name'], handler_data['name'])

    def test_get_yaml_object_by_key(self):
        """a yaml can have an a set of keys by whick it needs to be found
        For example this is used to get the base company that has id 1
        """
        model = 'res.company'
        data = {'keys' : "{'field' : 'id', 'type' : 'int', 'value' : 1, 'needs_exist' : True}"}
        handler = self.manager.get_handler_for_model(model)[0]
        handler.run_handler()
          
    def test_get_preset_data_folder(self):
        """ to be able to read/write yaml data for a site, we must know where 
        its yaml data ist stored.
        To get this information, we probaly need the help of odoo-workbench
        """
        site_name = 'presettest'
        self.manager.get_preset_data_folder(site_name)

    def test_login(self):
        """try to log into test database

        bin/s --add-site-local presettest
        bin/c -c presettest
        
        in a new bash shell:
        presettestw
        bin/build_odoo.py
        bin/odoo
        """
        self.manager.login('presettest')

if __name__ == '__main__':
    unittest.main()
