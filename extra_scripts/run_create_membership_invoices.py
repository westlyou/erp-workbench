# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes

from odoorpc import ODOO
from argparse import ArgumentParser
import copy
from datetime import date, timedelta
import os
import sys
sys.path.insert(0, '%s/extra_scripts' % os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
from create_membership_invoices import OdooHandler
def run(self, **kw_args):
    odoo = self.get_odoo()
    print('-------------------------->', odoo)
    print(self)
    handler = OdooHandler(opts=None, odoo=odoo)
    handler.list_invoices()