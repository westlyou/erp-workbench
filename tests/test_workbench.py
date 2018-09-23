import os
import sys
import unittest
from argparse import Namespace
from importlib import reload

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

    def x_test_create_create(self):
        """ run the create -c command 
        """
        self.handler.site_names = [list(self.handler.sites.keys())[0]]
        result = self.handler.create_or_update_site()

    def x_test_create_create_main(self):
        """ run the create -c command 
        using the scripts.create_site main method
        """
        from scripts.create_site import main
        args = self.args
        args.create = True
        args.name = list(self.handler.sites.keys())[0]
        main(args, args.subparser_name)

    def x_test_create_ls(self):
        """ run the create -ls command 
        """
        from scripts.utilities import list_sites
        list_sites(self.handler.sites, quiet = True)

    def x_test_create_ls_main(self):
        """ run the create -ls command 
        """
        from scripts.create_site import main
        args = self.args
        args.list_sites = True
        main(args, args.subparser_name)

    def x_test_create_parse_args(self):
        """ run the create parse_args command 
        """
        from scripts.create_site import parse_args
        parse_args()

class TestSupportNewSites(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self._get_sites()
        from config.handlers import SupportHandler
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'support'
        args.skip_name = True
        args.quiet = True
        self.args = args
        self.handler = SupportHandler(args, {})
        
    def _get_sites(self):
        old_exit = sys.exit
        # monkey patch sys.exit not 
        def exit(arg=0):
            print('monkey patched sys exit executed')
        sys.exit = exit
        try:
            # if the sites_list does not exist yet
            # the following import will create it
            # but call exit afterwards, which we have monkeypatched
            from config import sites_list
            self.sites_list_path = os.path.dirname(sites_list.__file__)
            self.SITES_G = sites_list.SITES_G
            self.SITES_L = sites_list.SITES_L
        except:
            # 
            try:
                from config import BASE_INFO
                sys.path.append(os.path.dirname(BASE_INFO.get('sitesinfo_path')))
                import sites_list
                self.sites_list_path = os.path.dirname(sites_list.__file__)
                self.SITES_G = sites_list.SITES_G
                self.SITES_L = sites_list.SITES_L
            except:
                raise
        finally:
            sys.exit = old_exit
        
    def tearDown(self):
        super().tearDown()
        # remove sites we added
        for n, existing in [('sites_global',self.SITES_G)  , ('sites_local', self.SITES_L)]:
            keys = list(existing.keys())
            temp_path = os.path.normpath('%s/%s' % (self.sites_list_path, n))
            files = os.listdir(temp_path)
            for file_name in files:
                try:
                    n, e = file_name.split('.')
                except:
                    continue
                if n != '__init__' and e == 'py':
                    if n not in keys:
                        os.unlink('%s/%s' % (temp_path, file_name))

    def x_test_support_add_drop_site(self):
        """ run the create -c command 
        """
        import sites_list
        new_name = 'new_site'
        self.handler.site_names = [new_name]
        self.handler.name = new_name
        self.args.add_site = True
        result = self.handler.add_site_to_sitelist()
        reload(sites_list.sites_global)
        from sites_list.sites_global import SITES_G
        self.assertTrue(new_name in SITES_G.keys())
        # now delete the site again
        result = self.handler.drop_site()
        reload(sites_list.sites_global)
        from sites_list.sites_global import SITES_G
        self.assertFalse(new_name in SITES_G.keys())


class TestSupport(unittest.TestCase):

    def setUp(self):
        from config.handlers import SupportHandler
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'support'
        args.skip_name = True
        args.quiet = True
        self.args = args
        self.handler = SupportHandler(args, {})
   
    def test_editor(self):
        print(self.handler.editor)

if __name__ == '__main__':
    unittest.main()
