#!bin/python


import argparse
import os
import sys
from collections import OrderedDict
from pprint import pformat

import odoorpc
import yaml
from yaml_cache import YamlCache

from bcolors import bcolors
from presets_config import BASE_PATH

try:
    from presets.registry import handler_registry
except ImportError:
    from registry import handler_registry
try:
    from config import BASE_INFO
except ImportError:
    sys.path.insert(0, os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    from config import BASE_INFO


class Manager(object):
    """provide a management class for presets management

    Attributes:
        _handler_registry {dictionary} -- a container for all yaml handlers
        _odoo {odoo rpc instance} -- a rpc connection to a running odoo instance
        _reverse_registry {dictionary} -- a container for all yaml handlers keyed by (name, model)
        _cache {YamlCache instance} -- a cache for yaml data
        _site_name {string} -- name of the site we are handling data for
            is not selt when starting, can be learned from odoo
        _yaml_data_folder {string} -- path to the folder where all the yaml files are stored
            this is contructed usinge the name of the site 
    Returns:
        [type] -- [description]
    """

    _handler_registry = {}
    _odoo = None
    _reverse_registry = {}
    _cache = None
    _site_name = ''
    _yaml_data_folder = ''
    
    def __init__(self, site_name='', user='', password=''):
        """ load handler registry
        """
        self._handler_registry = handler_registry
        self.odoo = odoorpc.ODOO()
        if site_name:
            self.login(site_name, user, password)
        # provision all handler with access to odoo
        # and a backlink to the manager
        for handler in list(self._handler_registry.values()):
            handler.odoo = self.odoo
            handler.manager = self
        # cache to cache yaml data
        # give it a way to point back to ourself
        self._cache = YamlCache(self)
        
    @property
    def cache(self):
        """a cache for the reach yaml files

        Returns:
            YamlCache instance
        """
        return self._cache

    @property
    def handler_registry(self):
        """a registry of yaml handler

        Returns:
            dict -- a container with all yaml handlers
        """

        return self._handler_registry

    @property
    def base_path(self):
        """provide the base_path to where the datafiles are installed

        Returns:
            string -- path to the parentfolder of all datafiles
        """

        return BASE_PATH

    @property
    def base_yaml_path(self):
        """provide the base_path to where the datafiles are installed

        Returns:
            string -- path to the parentfolder of all yaml files
        """
        return '%s/yaml' % BASE_PATH  # os.path.split(__file__)[0]

    @property
    def reverse_registry(self):
        """a reverseregistry of yaml handler
        keyed by (name, model)

        Returns:
            dict -- a container with all yaml handlers
        """
        if not self._reverse_registry:
            for name, handler in list(self._handler_registry.items()):
                self._reverse_registry[(
                    handler.obj_name, handler.model)] = handler

        return self._reverse_registry
    
    @property
    def site_name(self):
        """the name of the yamlfile the handler reads/writes
        """
        if not self._site_name:
            if self.odoo:
                # db name and site_name are equal
                self._site_name = self.odoo.env.db
        return self._site_name

    @property
    def yaml_data_folder(self):
        if not self._yaml_data_folder:
            self._yaml_data_folder = self.get_preset_data_folder(
                self.site_name)
        return self._yaml_data_folder
    

    def get_yaml_file(self, preset_name):
        """ load a preset yaml file
            the folder where the yaml files are stored is
            defined by YAML_PATH
        Arguments:
            preset_name {string} -- name of the yaml file to load

        Returns:
            return a dictionary of which the keys are object/models/fields
            every erp instance needs
            such instances are:
            company:
                model: "res.company"
                name
                tagline
                ..
            incomming_mail:
                ....

        This method is only use while testing
        """
        yaml_file = '%s/yaml/%s.yaml' % (BASE_PATH, preset_name)
        if os.path.exists(yaml_file):
            with open(yaml_file) as f:
                yaml_data = yaml.load(f)
                return yaml_data
        else:
            print(bcolors.WARNING)
            print('*' * 80)
            print('%s does not exist', yaml_file)
            print(bcolors.ENDC)
        return None

    def get_handler_by_name(self, name):
        """access a handler by its name

        Arguments:
            name {string} -- name of the handler to return
        """
        if name in self.handler_registry:
            return self.handler_registry[name]
        else:
            print(bcolors.WARNING)
            print('*' * 80)
            print('handler %s does not exist', name)
            print(bcolors.ENDC)
        return None

    def get_preset_data_folder(self, site_name):
        """to be able to read/write yaml data for a site
        we must know where the data is situated.
        odoo-workbeench provites a folder for each site
        in its standard environment. So we must try to find out
        where this environment points to.

        Arguments:
            site_name {string} -- name of the site for which we handle the data
        """
        data_folder = '%s/%s/presets' % (
            BASE_INFO['odoo_server_data_path'], site_name)
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        return data_folder

    def login(self, database, user='admin', pw='admin'):
        """log into odoo

        Arguments:
            database {string} -- odoo db into which we should login

        Keyword Arguments:
            user {str} -- user (default: {'admin'})
            pw {str} -- password (default: {'admin'})
        """
        self.odoo.login(database, user, pw)

    def set_test_mode(self):
        """in test mode acctions are not really executed
        """
        for handler in list(self.handler_registry.values()):
            handler._test_mode = True

    def get_app_sequence(self):
        """ the apps should be presented to the user in a repeatable fasion
            This is achieved handling an a sequence of app names
            and within the app name a sequence

        Returns:

        """
        from presets_config import APP_SEQUENCE
        sec_dic = {}
        for handler in list(self.handler_registry.values()):
            app_group_index = APP_SEQUENCE.get(handler.app_group)
            # APP_SEQUENCE is something like
            # OrderedDict([('company', 1), ('mailhandler', 2), ('bank', 3)])
            if not app_group_index:
                raise ValueError('%s is not a valid app_group (%s)' %
                                 (handler.app_group, handler.name))
            # inner is the list of handlers belonging to an app_group
            inner = sec_dic.get(app_group_index, [])
            inner.append(
                tuple([int('%d%d' % (app_group_index, handler.app_index)), handler]))
            sec_dic[app_group_index] = inner
        # now sec_dic conains all handlers but it has no easy accessible sequence
        sequence_dic = OrderedDict()
        # now go trough sec_dic in order of its app_group_index entries
        # and add the values which are (index, handler) tupels in order of the inx to
        # the sequence_dic
        app_keys = list(sec_dic.keys())
        app_keys.sort()
        for app_key in app_keys:
            handlers = sec_dic[app_key]
            handlers.sort()
            for h in handlers:
                k, v = h
                # make key unique, if no goo sequence was provided
                while k in sequence_dic:
                    k += 1
                sequence_dic[k] = v
        # fine, we now have a struct that represents the sequence of handlers to load
        return sequence_dic

    def get_handler_for_model(self, model):
        """return list of handlers, that can deal with a model
        question: is it possible, that more than one handler deals with a model,
        or do we need to adapt a given handler similar to odoos _inherit?

        Arguments:
            model {string} -- hame of an odoo modle like 'res.partner'
        Returns:
            {list} -- list of handlers able to deal with 

        Todo:
            do we need to know what addon is related with the handler
            or does an addon define a set of handler that needs to be handled
        """
        result = []
        for handler in list(self.handler_registry.values()):
            if handler.model == model:
                result.append(handler)
        return result

    def set_yaml_data_for_model(self, model, data):
        """write the yaml file for the model
        this is done by checking if the yaml data already exists in the sites yaml folder
        if it does, the it is read and updated with the data
        if not, it is created.

        Arguments:
            model {string} -- the model for which we want set the yaml data
            data {dict} -- the data we want to update the yaml files with
        """
        handler = self.get_handler_for_model(model)[0]
        handler.yaml_data = data
        # now return the updated data
        return handler.yaml_data


def main(args):
    """this method is called when manager.py is run from the command line

    Arguments:
        args {namespace} -- arparse args
    """
    if args.add_handler:
        if not args.name:
            print('you must provide a handler name')
            return
        name = args.name
        # we want to create a handler say for
        # read_yaml_bankaccount
        # to do so we need classname for which we change the
        # snake case to camel case and add 'Class'
        # read_yaml_bankaccount -> ReadYamlBankaccountHandler
        class_name = '%sHandler' % ''.join(
            [word.capitalize() for word in args.name.split('_')])
        names_dic = {
            'klass': class_name,
            'yaml_name': name,
        }
        # now copy template out to the class module
        from templates.new_handler import HANDLER_TEMPLATE
        out_name = '%s/registry/%s.py' % (
            os.path.dirname(os.path.abspath(__file__)), name)
        open(out_name, 'w').write(HANDLER_TEMPLATE % names_dic)
        print(bcolors.OKGREEN)
        print('*' * 80)
        print('Happily created %s' % out_name)
        print(bcolors.ENDC)
    if args.show:
        from presets.templates.show_template import SHOW_TAMPLATE as st
        from presets.presets_config import BASE_PATH, APP_SEQUENCE, BASE_PRESETS
        data = {
            'base_path': BASE_PATH,
            'app_sequence': pformat(APP_SEQUENCE),
            'base_presets': pformat(BASE_PRESETS),
        }
        print (st % data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Preset manager handles presets for ERP sites',
    )
    parser.add_argument(
        '-a',
        action="store_true",
        dest='add_handler',
        help='add new handler')
    parser.add_argument(
        'name',
        action="store",
        # dest='name',
        nargs='?',
        default='',
        help='name of new handler')
    parser.add_argument(
        # '-s',
        '--show',
        action="store_true",
        dest='show',
        help='list preset managers settings')

    args = parser.parse_args()
    main(args)
