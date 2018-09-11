import os
import sys
import unittest
from argparse import Namespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
run it with:
bin/python -m unittest discover tests
"""
class MyNamespace(Namespace):
    # we need a namespace that just ignores unknow options
    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        return None

class TestCreate(unittest.TestCase):

    def setUp(self):
        from config.config_data.handlers import SiteCreator
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'create'
        args.skip_name = True
        args.quiet = True
        self.args = args
        self.handler = SiteCreator(args, {})

    def test_create_create(self):
        """ run the create -c command 
        """
        self.handler.site_names = [list(self.handler.sites.keys())[0]]
        result = self.handler.create_or_update_site()

    def test_create_create_main(self):
        """ run the create -c command 
        using the scripts.create_site main method
        """
        from scripts.create_site import main
        args = self.args
        args.create = True
        args.name = list(self.handler.sites.keys())[0]
        main(args, args.subparser_name)

    def test_create_ls(self):
        """ run the create -ls command 
        """
        from scripts.utilities import list_sites
        list_sites(self.handler.sites, quiet = True)

    def test_create_ls_main(self):
        """ run the create -ls command 
        """
        from scripts.create_site import main
        args = self.args
        args.list_sites = True
        main(args, args.subparser_name)

if __name__ == '__main__':
    unittest.main()
