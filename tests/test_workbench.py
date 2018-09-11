import os
import sys
import unittest
from argparse import Namespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
run it with:
bin/python -m unittest discover tests
"""

class Testreate(unittest.TestCase):

    def setUp(self):
        from config.config_data.handlers import SiteCreator
        args = Namespace()
        args.name = ''
        args.subparser_name = 'ccreate'
        self.handler = SiteCreator(args, {})

    def test_create_ls(self):
        """ run the create -ls command 
        """
        print(self.handler)


if __name__ == '__main__':
    unittest.main()
