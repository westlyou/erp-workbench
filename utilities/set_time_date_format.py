#!bin/python
# -*- coding: utf-8 -*-
import mimetypes
from argparse import ArgumentParser

import odoorpc
import os

class FormatHandler(object):
    def __init__(self):
        self.opts = opts
        odoo = odoorpc.ODOO(opts.host, port=opts.port)
        odoo.login(opts.dbname, opts.rpcuser, opts.rpcpw)
        self.odoo = odoo

        self.required_opts = {
            "--date-format": self.opts.date_format,
            "--time-format": self.opts.time_format,
            "--iso-code": self.opts.iso_code,
        }

    def check_required_opts(self):
        # check if the required options are set
        missing_opts = []
        for opt_name in list(self.required_opts.keys()):
            if not self.required_opts[opt_name]:
                missing_opts.append(opt_name)
        return missing_opts

    def setFormats(self):
        lmodule  = self.odoo.env["res.lang"]
        languages= lmodule.search([('name', '>', '')])
        iso = self.opts.iso_code
        data = {
            'time_format' : self.opts.time_format,
            'date_format' : self.opts.date_format,
        }
        for lang in languages:
            if iso == 'all' or lang.iso_code == iso:
                l = lmodule.browse(lang)
                l.write(vals=data)



def main():
    handler = FormatHandler()
    missing_opts = handler.check_required_opts()
    if not len(missing_opts):
        handler.setFormats()
    else:
        parser.error("Please specify the following options: " + ", ".join(missing_opts))


if __name__ == '__main__':
    usage = "insert_media_in_cms.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument("-H", "--host",
                        action="store", dest="host", default='localhost',
                        help="define host default localhost")

    parser.add_argument("-l", "--language",
                        action="store", dest="language",  default="all",
                        help="what language to set values for, default all")

    parser.add_argument("-d", "--dbname",
                        action="store", dest="dbname", default='afbsdemo',
                        help="define host default ''")

    parser.add_argument("-U", "--rpcuser",
                        action="store", dest="rpcuser", default='admin',
                        help="define user to log into odoo default admin")

    parser.add_argument("-tf", "--time-format",
                        action="store", dest="time_format", default='%H:%M',
                        help="time format. Default '%H:%M'")

    parser.add_argument("-df", "--date-format",
                        action="store", dest="date_format", default='%d.%m.%Y',
                        help="time format. Default '%d.%m.%Y'")

    parser.add_argument("-i", "--iso-code",
                        action="store", dest="iso_code", default='all',
                        help="iso code of the language to set, Default=all")

    parser.add_argument("-P", "--rpcpw",
                        action="store", dest="rpcpw", default='admin',
                        help="define password for odoo user default 'admin'")

    parser.add_argument("-PO", "--port",
                        action="store", dest="port", default=8069,
                        help="define rpc port default 8069")

    parser.add_argument("-v", "--verbose",
                        action="store_true", dest="verbose", default='false',
                        help="be a bit verbose")

    opts = parser.parse_args()
    main()
