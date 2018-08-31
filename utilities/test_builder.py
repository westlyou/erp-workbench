#!bin/python
# -*- coding: utf-8 -*-
import os, fnmatch
import sys
import ast
from ast import ClassDef
from argparse import ArgumentParser
from glob import glob

# Folders: what folders do we scan for modules
FOLDERS = ['models', 'controllers', 'wizard']
SKIP_FILES = ['__init__.py']
SKIP_CLASSES = []
TEST_HEADER = """
# -*- encoding: utf-8 -*-
\"\"\"
start the tests with:
bin/odoo --test-enable -i %(app_name)s --stop-after-init
\"\"\"
from odoo.tests.common import TransactionCase, post_install
#from psycopg2 import IntegrityError
from %(common_test_module)s import TestHrCommon

"""
INI_HEADER = 'from . import %(common_test_module)s'
COMMON_TEST_MODULE_NAME = 'hr_common'
COMMON_MODULE = """
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# copied verbatim from odoo with small enhancements

from odoo.tests import common

class TestHrCommon(common.TransactionCase):

    def setUp(self):
        super(TestHrCommon, self).setUp()

        self.Users = self.env['res.users']

        self.group_hr_manager_id = self.ref('hr.group_hr_manager')
        self.group_hr_user_id = self.ref('hr.group_hr_user')
        self.group_user_id = self.ref('base.group_user')

        # Will be used in various test cases of test_hr_flow
        self.demo_user_id = self.ref('base.user_demo')
        self.main_company_id = self.ref('base.main_company')
        self.main_partner_id = self.ref('base.main_partner')
        self.rd_department_id = self.ref('hr.dep_rd')

        # Creating three users and assigning each a group related to Human Resource Management
        self.res_users_hr_manager = self.Users.create({
            'company_id': self.main_company_id,
            'name': 'HR manager',
            'login': 'hrm',
            'email': 'hrm@example.com',
            'groups_id': [(6, 0, [self.group_hr_manager_id])]
        })

        self.res_users_hr_officer = self.Users.create({
            'company_id': self.main_company_id,
            'name': 'HR Officer',
            'login': 'hro',
            'email': 'hro@example.com',
            'groups_id': [(6, 0, [self.group_hr_user_id])]
        })

        self.res_users_employee = self.Users.create({
            'company_id': self.main_company_id,
            'name': 'Employee',
            'login': 'emp',
            'email': 'emp@example.com',
            'groups_id': [(6, 0, [self.group_user_id])]
        })

        # Will be used to test the flow of jobs(i.e. opening the job position for "Developer" for
        # recruitment and closing it after recruitment done)
        self.job_developer = self.env(user=self.res_users_hr_officer.id).ref('hr.job_developer')
        self.employee_niv = self.env(user=self.res_users_hr_officer.id).ref('hr.employee_niv')

        self.partner_client = self.env.ref("base.res_partner_1")

"""
SMOKETEST = """
class %(class_name)s(TestHrCommon):
    \"""
    %(class_name)s is here to check ......
    \"""
    @post_install(True)
    def test_first(self):
        "just check if setUp is executed"
        self.assertTrue(1 == 1, 'Somethings wrong in the state of Danemark')
"""

# redhelp/addons/fsm_tools/red_fnq_handler/models/models.py
class bcolors:
    """
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestCreator(object):
    def load_suite(self, path):
        """ use pythons ast parser 
        
        Arguments:
            path {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """

        data = open(path).read()
        body = ast.parse(data).body
        # collect names of classes
        result = [e.name for e in body if isinstance(e, ClassDef)]
        return result

    def make_test_module(self, path, classes, app_name):
        """ 
        path is the path to a test module
        If the test module is not existing, it is created and added 
        to the __init__ file
        If it exists, it is checked whether all classes exist
        
        Arguments:
            path {string} -- path to the test module
            classes {list} -- list of classes for which testsclasses should exist
            app_name {string} -- name of the app_name we are creating tests for
        """
        # first check whether tests block exists
        test_folder, module_f = os.path.split(path)
        ini_file = '%s/__init__.py' % test_folder
        common_file = '%s/%s.py' % (test_folder, COMMON_TEST_MODULE_NAME)
        if not os.path.exists(test_folder):
            os.makedirs(test_folder)
            #_, app_name = os.path.split(os.getcwd())
            open(ini_file, 'w').write(INI_HEADER % {'common_test_module' : COMMON_TEST_MODULE_NAME, 'app_name': app_name})

        # does the file with common tests exist?
        if not os.path.exists(common_file):
            open(common_file, 'w').write(COMMON_MODULE)

        # check whether the testmodule is imported
        module, _ = os.path.splitext(module_f)
        lines = open(ini_file, 'r').read().split('\n')
        first_line = lines.pop(0)
        if not module in first_line:
            first_line += (', %s' % module)
            open(ini_file, 'w').write('\n'.join([first_line] + lines))
        # generate names for the testclasses
        test_classes = set(['Test%s' % c for c in classes])
        # now we check whether the module exist
        new = None
        if os.path.exists(path):
            # fine, check whether thest classes for all classes exist
            # we assume that __init__.py loads the file
            existing_tests = set(self.load_suite(path))
            missing = test_classes - existing_tests 
            if missing:
                test_file_string = open(path, 'r').read()
                # we assume that all imports are in place
        else:
            new = True # could be that no class is in the module, but we import it, so we must create it in all cases
            test_file_string = TEST_HEADER % {'common_test_module' : COMMON_TEST_MODULE_NAME, 'app_name' : app_name}
            missing = test_classes

        # now add the missing tests
        for test_class in missing:
            test_file_string += (SMOKETEST % {'class_name' : test_class, 'common_test_module' : COMMON_TEST_MODULE_NAME})
        # only write out the test module if we changed anything
        if missing or new:
            test_file_string = open(path, 'w').write(test_file_string)
            



    def handle_odoo_module(self, path, module_name):
        """List all classes belonging to a module
        
        Arguments:
            path {sting} -- path to the module
        """
        # check if folder exists and chdir into it
        if not os.path.exists(path) or not os.path.isdir(path):
            print('%s is not an existing folder' % path)
            return

        os.chdir(path)
        pattern = "*.py" 
        for root in FOLDERS:
            for dir_name, subdirList, fileList in os.walk(root, topdown=False):
                print(('Found directory: %s' % dir_name))
                for fname in fileList:
                    if fnmatch.fnmatch(fname, pattern) and not fname in SKIP_FILES:
                        print(('\t%s' % fname))
                        classes = self.load_suite('%s/%s' % (dir_name, fname))
                        module, _ = os.path.splitext(fname)
                        self.make_test_module('tests/test_%s_%s.py' % (dir_name, module), classes, module_name)

#handle_odoo_module('redhelp/addons/fsm_tools/red_fnq_handler')

def main(opts):
    handler = TestCreator()
    app_path = opts.app_path
    if not app_path or not os.path.isdir(app_path):
        print(bcolors.FAIL)
        print("you must use option -a with a valid path")
        print(bcolors.ENDC)
        sys.exit()
    app_list = opts.app_list
    if not app_list:
        app_path, app_name = os.path.split(app_path)
        app_list = [app_name]
    elif '*' in app_list:
        module_names = glob('%s/%s' % (app_path, app_list))
        app_list = [os.path.split(mn)[-1] for mn in module_names]
    else:
        app_list = app_list.split(',')
    for app_name in app_list:
        # construct the tests
        act_path = '%s/%s' % (app_path, app_name)
        print('handling: %s' % act_path)
        handler.handle_odoo_module(act_path, app_name)


if __name__ == '__main__':
    usage = "insert_media_in_cms.py -h for help on usage"
    parser = ArgumentParser(usage=usage)
    dp = '/'.join(os.path.split('%s' % (  __file__))[:-1])
    parser.add_argument("-al", "--app-list",
                        action="store", dest="app_list",
                        help="""
                            list of modules to be handled. they are found in the ap-path. 
                            You can use an start (like red*) to use several modules""")

    parser.add_argument("-a", "--app-path",
                        action="store", dest="app_path",
                        help="Path to the app folder")

    opts = parser.parse_args()
    main(opts)
