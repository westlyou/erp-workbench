# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import datetime
import os

import yaml

from bcolors import bcolors
from presets_config import BASE_PATH, BASE_PRESETS

"""default_handler provides yaml_handler for modules that do not define their own

This module provides the BaseHandler class from which all handlers derive.
.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

# where are the yaml files stored

SKIP_NAMES = [
    'model',
    'keys',
    'handler',
    'depends',
]
# name of the handler to use, if none is defined
BASE_YAML_HANDLER = 'base_yaml_handler'


class NotImlementedException(Exception):
    """exception to signal that a method is not yet implemented
    """
    pass


class BaseHandler(object):
    """Provide a base class with all methods a handler need defined but not implemented

    Attributes:
        _odoo {instance} -- an odoorpc instance of a running odoo used to manage objects on
                          it is added with the set_odoo property
        _manager {instance} -- a backlink to the manager
        _model {string} -- the name of the model, this handler deals with
        _Model {instance} -- the odoo model object, this handler deals with
        _obj_name {string} -- the name of the object found in the yaml_file (the main key like company:)
        _yaml_name {string} -- name of the yaml file
            if not explicitely set by the implementation, use self.name
        _yaml_data {dict} -- data loaded from the yaml file
        _registry {dict} -- a pointer to the registry. so a handler can call an other handler
        _last_run {datetime} -- will be set, when the handler is executed
        _test_mode {bool} -- if set, changes in the database are not executed
        _skip_names {list} -- list of name to skip when constructing the dict to create an erp object
        _app_group {string} -- to what group of apps does the handler belong like company, project ..
        _app_index -- what sequence within the _app_group
        _is_done {boolean} -- handler has been exected
    """
    _odoo = None
    _is_done = False
    _manager = None
    _Model = None
    _model = ''
    _obj_name = ''
    _yaml_data = {}
    _yaml_name = ''
    _last_run = None
    _test_mode = False
    _skip_names = SKIP_NAMES
    _registry = {}
    _app_group = ''
    _app_index = 0

    def _get_yaml_data(self, raw=False):
        """load the yaml data from the yaml file

        Arguments:
            raw {bool} -- if True return data as read from the yaml file          
                else return data filterd for this handler

        Raises:
            ValueError -- when the base yaml does not exist

        Returns:
            [type] -- [description]
        """
        #yaml_file_path_for_site = self.yaml_file_path_for_handler
        
        # did we read the file before?
        yaml_data = self.manager.cache.get(self.yaml_name)
        if raw:
            return yaml_data

        for obj_name, data_set in yaml_data.items():
            if data_set.get('handler', '') == self.name:
                yaml_data = data_set
                # we want to be able to ask for the obj_name both
                # the handler, and also the yaml_data .., redudncy ??
                yaml_data['obj_name'] = yaml_data.get('obj_name', obj_name)
                self._obj_name = yaml_data['obj_name']
                self._yaml_data = yaml_data
                return self._yaml_data

        self._yaml_data = {}
        return self._yaml_data
    
    @property
    def app_group(self):
        return self._app_group

    @property
    def app_index(self):
        return self._app_index

    @property
    def base_presets(self):
        """base presets is a list of presets every handler assumes that
        all of them have been executed and the related objects have ben 
        created 

        Returns:
            [list] -- list of preset names like ['company', 'mailhandler', 'bank']
        """
        return BASE_PRESETS

    @property
    def is_done(self):
        return self._is_done

    @property
    def odoo(self):
        """odoo is the odoorpc.ODOO instance on which we manage objects
            it can be None
        """
        return self._odoo

    @odoo.setter
    def odoo(self, odoo):
        """set the odoo to a valid odoorpc.ODOO instance    

        Arguments:
            odoo {instance} -- a running odoorpc.ODOO instance
        """
        self._odoo = odoo

    @property
    def manager(self):
        """this is a backlink to the manager, that is handling the registry
            to which this handler belongs
        """
        return self._manager

    @manager.setter
    def manager(self, manager):
        """set manager 

        Arguments:
            manager {instance} -- the calling manager instance
        """
        self._manager = manager

    @property
    def model(self):
        """return the model, this handler is dealing with
        this must be read from the yaml_data, which must be loaded in appropriate
        """
        try:
            # here we have to loop trough all elements of the handlers yaml dat
            # because the same yaml file could be used for several handlers
            # base_yaml_handler my have no own data, it is probably not used on its own
            data = self.yaml_data
            if data:
                return self.yaml_data['model']
        except:
            print (self._yaml_data)
            raise
        if not self._model:
            try:
                self._model = self.yaml_data['model']
            except:
                print(bcolors.FAIL)
                print('*' * 80)
                print('handler %s has no model defined' % self.name)
                print(bcolors.ENDC)
                raise
        return self._model

    @property
    def Model(self):
        """model is the odoo model, this handler deals with
        """
        if not self._Model:
            try:
                self._Model = self._odoo.env[self.model]
            except:
                print(bcolors.FAIL)
                print('*' * 80)
                print('%s does not exist, do you need to install an addon?' %
                      self.model)
                print('*' * 80)
                print(bcolors.ENDC)
                raise
        return self._Model

    @property
    def obj_name(self):
        """the name of the yamlfile the handler reads/writes
        """
        if not self._obj_name:
            self._get_yaml_data()
        return self._obj_name

    @property
    def site_name(self):
        """the name of the yamlfile the handler reads/writes
        """
        return self._manager.site_name

    @property
    def yaml_name(self):
        """the name of the yamlfile the handler reads/writes
        """
        return self._yaml_name

    @property
    def yaml_data(self):
        """the data this handler deals with
        """
        if not self._yaml_data:
            self._get_yaml_data()
        return self._yaml_data

    @yaml_data.setter
    def yaml_data(self, data, update=False):
        """create or update yaml files in the sites yaml folder

        Arguments:
            yaml_path {string} -- path to the file, if it does not exis it will be created
            data {dictionary} -- dictonary with data to be used
            update {boolean} -- if set overwrite data , if not only create
        Return:
            #updated yaml_data
        """
        # get the raw yaml data
        yaml_data_raw = self._get_yaml_data(True)
        # out of the raw data we have to get the dataset
        # the actual handler deals with
        for data_set in yaml_data_raw.values():
            if data_set.get('handler', BASE_YAML_HANDLER) == self.name:
                yaml_data = data_set
                break
        # now we have the actual yaml data
        # upgrade it with the new data
        yaml_data.update(data)
        yaml_data_raw.sync()
        #yaml_path = '%s/%s.yaml' % (self.manager.yaml_data_folder, self.yaml_name)
        #with open(yaml_path, 'w') as yaml_file:
            #yaml.dump(yaml_data_raw, yaml_file, default_flow_style=False)
        ## now refresh the data
        #self._get_yaml_data()
        # return yaml_data
    
    #def yaml_file_path_for_handler(self):
        #"""
        #construct a path to the yamlfile this handler is using
        #"""
        
        #return '%s/%s.yaml' % (self.manager.yaml_data_folder, self._yaml_name)

    def dump(self):
        """
        dump the content of the yaml this handler is using to the filesystem
        """
        self.manager.cache.c[self.yaml_file_path_for_site].dump()

    def register(self, registry, name):
        """register a handler 

        Arguments:
            registry {dict} -- the registry is a dict passed by reference,
                               into which each handler adds itself on its name
            name {string} -- name of the handler
        """
        self.name = name
        if not self._yaml_name:
            self._yaml_name = name
        registry[name] = self
        # some handlers need to call other handlers
        # so we keep a pointer to the registry
        self._registry = registry

    def check_and_run_parent(self, dependent_data, caller_name):
        """make sure objects we are dependent from are installed

        Arguments:
            dependent_data {dict} -- yaml data of a potetially dependent object
                if it has ann field 'depends', we will call this handler
            caller_name {string} -- handler that is calling
        Returns:
            {yaml-dict} -- a dictionary similar to the one that was read by the parent handler,
                updated with the objects the parent handler created 
        """

        depends = dependent_data.get('depends')
        if depends:
            parent = self._registry.get(depends, {})
            if not parent:
                print(bcolors.FAIL)
                print('*' * 80)
                print('%s is dependant of %s but this handler is not known' %
                      (caller_name, depends))
                print(bcolors.ENDC)
            if not parent.is_done:
                parent.run_handler()
            return parent.yaml_data
        return {}

    def get_object_by_keys(self, Model, yaml_data={}):
        """an objects yaml can define keys by which a handler can find the
        correct object in odoos database.
        This is also used to avoid conflicts with odoo when creating new elements or to avoid 
        creating new elements when existing ones are available.
        
        Arguments:
            Model {odoo model instance} -- an odoo model able to handle the objects in question
        
        Keyword Arguments:
            yaml_data {dict} -- if provided, thae it to get at the objecs, othewis use self.yaml_data  (default: {{}})
        
        Returns:
            object id or none -- id of the found object
        """

        yaml_data = yaml_data or self.yaml_data
        # 'keys': {'field': 'id', 'needs_exist': True, 'type': 'int', 'value': 1},
        keys = yaml_data.get('keys')
        result = []
        if keys:
            result = Model.search([(keys['field'], '=', keys['value'])])
        return result and result[0]

    def _check_and_run_basehandlers(self, run_all=False):
        """if we are not a base_handler, make sure 
        all basehandler are run
        every handler but the base handlers assumes
        that the base handlers have been run.

        Arguments:
            run_all {boolean} -- if set, run all base handler. mainly for testing

        base_presets is a list of tuples like [('company', 'res.company'), ..]
        self._manager.reverse_registry is a dict  like {('company', 'res.company'): handler, ..}
        """
        # get an ordered list of handlers to run as base handlers
        to_run = [self._manager.reverse_registry[bp]
                  for bp in self.base_presets]
        # we only want to run handler we are expecting to have been executed befor us
        # the ones after us we do not bother about, as we are not dependent on them
        # this we do by bisecting the to_run list with ourself
        # however this is only done if we are part of the base_preset
        # for all other handlers we all base_handlers must have been run
        if not run_all:
            my_preset = self._manager.reverse_registry[tuple(
                [self.obj_name, self.model])]
            if my_preset in to_run:
                to_run = to_run[:to_run.index(my_preset)]
        for bp in to_run:
            if not bp.is_done and not bp == self:  # avoid recursion
                bp.run_handler()

    def _run_handler_start(self, *args, **kwargs):
        """helper method starts the creation of an object
        in any case it will run the base handlers.
        At the start, it sets a timestamp

        Returns:
            {dict} -- yaml_data
        """
        if not self._yaml_data:
            self._get_yaml_data()
        self._last_run = datetime.datetime.now()
        # first make sure the base handlers have been run
        # how do we make sure, that we do not call us recursively?
        self._check_and_run_basehandlers()
        # we create the objects defined in the yaml file
        yaml_data = self.yaml_data
        # make sure objects we are dependent from are installed
        # parent_data is not used in this handler
        parent_data = self.check_and_run_parent(yaml_data, self.name)
        values = {}  # dict that will be used to create an object
        yaml_data['parent_data'] = parent_data
        for k, v in yaml_data.items():
            if k.endswith('_help') or k in self._skip_names:
                continue
            values[k] = v
        yaml_data['values'] = values
        return yaml_data

    def _run_handler_end(self, *args, **kwargs):
        """helper method that finishes up the creation of an object
        """
        # flag handler as beeing executed
        if kwargs.get('save'):
            self.dump()
        self._is_done = True

    def run_handler(self):
        """run_handler does the handlers job
            it is an "abstract" method that must be implemented in the derived handler
            it must set the self._last_run variable
            so a dependent handler can check wheter this handler has been executed
            or needs to be called

            at the beginning it needs to call:
                yaml_data = self._run_handler()
            and at the end:
                self._run_handler_end()
        """

        raise NotImlementedException


class BaseYamlHandler(BaseHandler):
    """ provide a handler for situations, where no special handling is needed

    Attributes:
        _yaml_name {string} -- it is the name of the yaml file to load
         more than one handler can use the same file. It will only use
         those elements, for which the elements handler name is the handlers name.
         The elements handler name is set when the element is registered.
        _app_group {string} -- to what group of apps does the handler belong like company, project ..
        _app_index -- what sequence within the _app_group
    """
    _yaml_name = 'base_preset'
    _app_group = 'company'
    _app_index = 100  # should allways be overriden with a "real" index

    def run_handler(self):
        """run_handler does the handlers job and creates a new item

        Returns:
            {dict} -- yaml_data with three new elements added to it: 
                'parent_data': a dict with parent_data, with the result of calling the parent handler
                'values': a dict used to create the new object
                'new_object_id' : the id of the new object
        """
        #
        yaml_data = self._run_handler_start()
        # parent_data = base_dict['parent_data'] # parent_data not needed here
        Model = self.Model
        if not self._test_mode:
            new_id = 0
            try:
                values = yaml_data['values']
                old_id = yaml_data.get('new_object_id')
                old_id = old_id or self.get_object_by_keys(Model, yaml_data)
                if old_id:
                    obj = Model.browse([old_id])
                    obj.write(values)
                    # if an error accours new_object_id is not set
                    # is that correct
                    yaml_data['new_object_id'] = old_id
                else:
                    new_id = Model.create(values)
                    yaml_data['new_object_id'] = new_id
                self.yaml_data = yaml_data
                self._run_handler_end()
            except Exception, e:
                print(bcolors.FAIL)
                print('*' * 80)
                print(str(e))
                print('failed to create or update a record for %s using %s' %
                      (Model, values))
                print(bcolors.ENDC)
                yaml_data['new_object_id'] = None

        return yaml_data


class CompanyHandler(BaseYamlHandler):
    """ a handler for company objects and fields
    nothin but the index
    """
    _app_index = 1


class WebsiteHandler(BaseYamlHandler):
    """ a handler for company objects and fields
    nothin but the index
    """
    _app_index = 2


class OutgoingmailHandler(BaseYamlHandler):
    """ a handler for company objects and fields
    nothin but the index
    """
    _app_group = 'mailhandler'
    _app_index = 1


class IncommingmailHandler(BaseYamlHandler):
    """ a handler for company objects and fields
    nothin but the index
    """
    _app_group = 'mailhandler'
    _app_index = 2


"""HANDLER_LIST assigns classes external names
"""
HANDLER_LIST = [
    #('BaseYamlHandler', BASE_YAML_HANDLER),
    ('CompanyHandler', 'read_yaml_company'),
    ('WebsiteHandler', 'read_yaml_website'),
    ('OutgoingmailHandler', 'read_yaml_outgoingmail'),
    ('IncommingmailHandler', 'read_yaml_incommingmail'),
]
