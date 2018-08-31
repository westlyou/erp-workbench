#!%(inner)s/bin/python
# -*- encoding: utf-8 -*-
import sys
import imp
sp = imp.load_source('dummy', 'bin/start_openerp')
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
