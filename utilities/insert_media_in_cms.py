#!bin/python
# -*- coding: utf-8 -*-
import base64
import mimetypes
from argparse import ArgumentParser

import odoorpc
import os

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


def _full_path(fname, inputdir):
    path = inputdir.split("/")
    path.append(fname)
    path = "/".join(path)
    return path


def _read_file(fname, inputdir):
    full_path = _full_path(fname, inputdir)
    r = ''
    try:
        size = os.path.getsize(full_path)
        r = open(full_path, 'rb').read().encode('base64')
    except (IOError, OSError):
        print("Cant read File: %s" % full_path)
    return r, size


def _vprint(text, verbose):
    if verbose:
        print(text)


class ImageHandler(object):
    def __init__(self):
        self.opts = opts
        odoo = odoorpc.ODOO(opts.host, port=opts.port)
        odoo.login(opts.dbname, opts.rpcuser, opts.rpcpw)
        self.odoo = odoo

        self.required_opts = {
            "--parent-page": self.opts.parent_page,
            "--input-dir": self.opts.inputdir or self.opts.outputdir,
        }

    def get_parent_id(self, name):
        # search for an id based on a name
        pages = self.odoo.env["cms.page"]
        counter = 0
        result = self.odoo.env["cms.page"].search([('name', '=', name)])
        if result:
            return result[0]

    def get_img(self, fname, mime_type):
        pass
    
    def insert_img(self, fname, mime_type):
        parent_id = self.get_parent_id(self.opts.parent_page)
        f, size = _read_file(fname, self.opts.inputdir)

        self.odoo.env["cms.media"].create({
            'datas': f,
            'datas_fname': fname,
            'description': False,
            # u'force_category_id': category_id,
            'image': f,
            'lang_id': False,
            'name': fname,
            'page_id': parent_id,
            'published_date': False,
            # u'res_id': u'',
            'res_model': 'cms.page',
            'type': 'binary',
            'url': False,
            'website_published': True,
            'mimetype': mime_type,
            # u'file_size': size
        })

        _vprint("created: " + fname + " \n\tparent: " + str(parent_id) + " \n\tsize: " + str(size) + " \n\ttype: " + mime_type + "\n", self.opts.verbose)

    def process_page(self):
        parent_id = self.get_parent_id(self.opts.parent_page)
        medias = self.odoo.env["cms.media"]
        odir = self.opts.outputdir
        if not odir.startswith('/'):
            odir = '%s/%s' % (os.getcwd(), odir)
        odir = os.path.normpath(odir)
        if not os.path.exists(odir):
            os.makedirs(odir)
        
        for m in medias.browse(medias.search([('page_id', '=', parent_id)])):
            if m.image:
                print(m.datas_fname)
                open('%s/%s' % (odir, m.datas_fname), 'wb').write(base64.b64decode(m.image))
        
    def process_dir(self):
        for filename in os.listdir(self.opts.inputdir):
            # guess_type returns a tuple so we take only the first.
            mime_type = mimetypes.guess_type(filename)[0]
            # mime_type is something like this: image/jpg. but we want all images and not only jpg.
            # so we split and take only the image.
            if mime_type and mime_type.split("/")[0] == "image":
                _vprint("read: " + filename, self.opts.verbose)
                self.insert_img(filename, mime_type)

    def check_required_opts(self):
        # check if the required options are set
        missing_opts = []
        for opt_name in self.required_opts:
            if not self.required_opts[opt_name]:
                missing_opts.append(opt_name)
        return missing_opts


def main():
    handler = ImageHandler()
    missing_opts = handler.check_required_opts()
    if not len(missing_opts):
        if handler.opts.outputdir:
            handler.process_page()
        else:
            handler.process_dir()
    else:
        parser.error("Please specify the following options: " + ", ".join(missing_opts))


if __name__ == '__main__':
    usage = "insert_media_in_cms.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument("-H", "--host",
                        action="store", dest="host", default='localhost',
                        help="define host default localhost")

    parser.add_argument("-pp", "--parent-page",
                        action="store", dest="parent_page",  # default="website_images standard",
                        help="define parent of the media page")

    parser.add_argument("-d", "--dbname",
                        action="store", dest="dbname", default='afbsdemo',
                        help="define host default ''")

    parser.add_argument("-U", "--rpcuser",
                        action="store", dest="rpcuser", default='admin',
                        help="define user to log into odoo default admin")

    parser.add_argument("-i", "--input-dir",
                        action="store", dest="inputdir",
                        help="define folder where images are found")

    parser.add_argument("-o", "--output-dir",
                        action="store", dest="outputdir",
                        help="define folder where images to be written")

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
