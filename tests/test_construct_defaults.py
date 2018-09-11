import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import construct_defaults
import getpass
import shutil

"""
run it with:
bin/python -m unittest discover tests
"""

class TestConstructDefault(unittest.TestCase):

    def setUp(self):
        BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
        ACT_USER = getpass.getuser()
        self.base_path = BASE_PATH
        self.act_user = ACT_USER
        self.user_home = os.path.expanduser('~')
        data_path = '%s/tests/test_data/' % BASE_PATH
        if not os.path.exists(data_path):
            os.makedirs(data_path, exist_ok=True)
        for root, dirs, files in os.walk(data_path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))        

    def test_check_and_update_base_defaults(self):
        """test overal functionality of check_and_update_base_defaults
        check_and_update_base_defaults reads a yaml file adapted by the user
        and creates a importable datastructure out of it
        The yaml file should only be parsed when it is newer than the importable module
        """

        result = {}
        # when a yaml file with config setting is newer than the coresponding
        # datafile we have to reload the datafile from the result
        vals = {
            'BASE_PATH' : self.base_path,
            'ACT_USER' : self.act_user,
            'USER_HOME' : self.user_home,  
        }
        must_reload = construct_defaults.check_and_update_base_defaults(
            vals,
            [(
                '%s/tests/yaml_files/config.yaml' % self.base_path,
                '%s/tests/test_data/base_config.py' % self.base_path,
                # defaults are the same
                '%s/tests/yaml_files/config.yaml' % self.base_path,
            )],
            result)
        self.assertTrue(must_reload)
        # we repeat the process but now reload must not be set
        must_reload = construct_defaults.check_and_update_base_defaults(
            vals,
            [(
                '%s/tests/yaml_files/config.yaml' % self.base_path,
                '%s/tests/test_data/base_config.py' % self.base_path,
            )],
            result)
        self.assertFalse(must_reload)

if __name__ == '__main__':
    unittest.main()
