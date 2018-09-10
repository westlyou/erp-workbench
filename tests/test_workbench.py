import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scripts import create_site

print(sys.path)

"""
run it with:
bin/python -m unittest discover tests
"""

class TestManager(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_base_preset(self):
        """ get_base_preset should return a dictonary with info on the objects
            we have to handle
            this must return a dictionary
            with a description of objects that each erp site needs to have set
            It muss have a structure 'company'
        """
        return
        data = self.manager.get_yaml_file('base_preset')
        company = data.get('company')
        self.assertTrue(company)
        for n in ['model', 'model_help']:
            self.assertTrue(company[n], '%s is missing %s' % ('company', n))
        # all other elements need these fields also
        for k, v in list(data.items()):
            for n in ['model', 'model_help']:
                self.assertTrue(v[n], '%s is missing %s' % (k, n))


if __name__ == '__main__':
    unittest.main()
