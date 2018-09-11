#!%(inner)s/bin/python
# -*- encoding: utf-8 -*-
import sys
import imp
# imp does not work in py3 anymore ..
sp = imp.load_source('dummy', 'bin/start_openerp')
# as replacement
# https://github.com/pyinvoke/invoke/issues/214
# https://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3
from importlib.machinery import SourceFileLoader
mymodule = SourceFileLoader('modname', '/path/to/file.py').load_module()
p = sp.sys.path
plist = p[0:len(p)]
sys.path[0:0] = plist
try:
    # v9
    from odoo import main
    main()
except ImportError:
    # v10
    import odoo
    odoo.cli.main()
