# -*- coding: utf-8 -*-
import os
try:
    import yaml 
    from fcache import FileCache
except ImportError:
    raise
    from bcolors import bcolors
    print(bcolors.FAIL)
    print('*' * 80)
    print('there was an error importing yaml or fcache, please run:bin/pip install -r install/requirements.txt')
    print(bcolors.ENDC)

class YamlCache(object):
    """Maintain a cache of yyaml files.
    These yaml files will be automaticall updated whe they are changed anywhere 
    when constructing an odoo object
    
    Returns:
        [type] -- [description]
    """

    _dump_path = ''

    def __init__(self, manager):
        """Constructor"""
        self._cache = {}
        self._manager = manager

    def __contains__(self, key):
        """
        Returns True or False depending on whether or not the key is in the 
        _cache
        """
        return key in self._cache
    
    @property
    def manager(self):
        """
        point back to the callin manager
        """
        return self._manager
    
    def get(self, yaml_name):
        # did we read the file before?
        yaml_file_path_for_site = '%s/%s.yaml' % (self.manager.yaml_data_folder, yaml_name)
        if self._cache.has_key(yaml_file_path_for_site):# preset_path):
            return self._cache[yaml_file_path_for_site]
        else:
            # preset_path_origin = preset_path
            # _yaml_data_folder is where the sites yaml files are
            preset_path = os.path.abspath(
                '%s/%s.yaml' % (self.manager.base_yaml_path, yaml_name))            
            if not os.path.exists(preset_path):
                print(bcolors.FAIL)
                print('*' * 80)
                print('%s does not exist' % preset_path)
                print(bcolors.ENDC)
                raise ValueError('yaml file not found:' + preset_path)

            # if the file does not exist or is older 
            # and has a size (could be left existing but empty)
            yaml_file_path_for_site = '%s/%s.yaml' % (self.manager.yaml_data_folder, yaml_name)
            if not os.path.exists(yaml_file_path_for_site) or \
               (os.path.exists(yaml_file_path_for_site) and not os.path.getsize(yaml_file_path_for_site)) or \
               (
                   os.path.exists(yaml_file_path_for_site)
                and
                    (os.path.getctime(preset_path) > os.path.getctime(yaml_file_path_for_site))
                ):
                # we have to create it
                with open(preset_path) as f:
                    yaml_data = yaml.load(f)
                cache = FileCache(yaml_name, flag='c', app_cache_dir = self.manager.yaml_data_folder)
                cache.update(yaml_data)
                with open(yaml_file_path_for_site, 'w') as f:
                    yaml.dump(yaml_data, f, default_flow_style=False)
            else:
                cache = FileCache(yaml_name, flag='c', app_cache_dir = self.manager.yaml_data_folder)
            ## now the "real" file exists and we can (re)read it
            ##def __init__(self, appname, flag='c', mode=0o666, keyencoding='utf-8',
                         ##serialize=True, app_cache_dir=None):            
            #with open(yaml_file_path_for_site) as f:
                #yaml_data = yaml.load(f)
            #cache.update(yaml_data)
            ## register the data with the manager, so we need not to reload it
            
            self._cache[yaml_file_path_for_site] = cache
            return self._cache[yaml_file_path_for_site]
    
    def dumper(self, key):
        """
        get the data from the cache using key and dump it to the file system
        key is also the path to the filesystem
        
        """
        if self._cache[key].dirty:
            with open(key, 'w') as yaml_file:
                yaml.dump(yaml_data_raw, self._cache[key]['value'], default_flow_style=False)
            self._cache[key]._dirty = {'_dirty' : False}
        
       
    def update(self, key, value):
        """
        Update the _cache dictionary and optionally remove the oldest item
        """
        self._cache[key] = {
            'date_accessed': datetime.datetime.now(),
            'value': value,
            '_dirty' : False,
            'dump' : self.dumper(key)
        }


    @property
    def size(self):
        """
        Return the size of the _cache
        """
        return len(self._cache)
    
    
    @property
    def c(self):
        """
        Return the size of the _cache
        """
        return self._cache
    
    
    