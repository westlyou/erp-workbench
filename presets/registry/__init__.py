from __future__ import absolute_import, division, print_function
import importlib
import os
import sys
BASE_PATH = __path__[0]
print(__path__, __file__)
files = os.listdir(BASE_PATH)
# sys.path.insert(0, '.')
# sys.path.insert(0, '../')

REGISTRY = {}
class bcolors:
    """provide error colors
    """

    FAIL = '\033[91m'
    ENDC = '\033[0m'

# iterate over all files in the folder and try to import
# a handler from them
# each file  should define a class with a handler
# the name of the handler is derived from fromm its name
# this name can be overridden by an object HANDLER_LIST
# which is a list of tuples:[('ClassName', 'handler_name), ...]
# each class must have a metho register(registry)
# this method gets a registry, into which the object installs itself

for file_name in files:
    try:
        n, e = file_name.split('.')
    except:
        continue
    if n != '__init__' and e == 'py':
        try:
            # construct path to import
            # BASE_PATH migth start with a '.' like in './presets/registry'
            mod_name = '.'.join([p for p in BASE_PATH.split('/') if p != '.'] + [n])
            mod = importlib.import_module('registry.' + n)
            if hasattr(mod, 'HANDLER_LIST'):
                handler_list = mod.HANDLER_LIST
            else:
                handler_list = [(n, n)]
            for klass_name, handler_name in handler_list:
                klass = getattr(mod, klass_name)
                if klass:
                    obj = klass()
                    obj.register(REGISTRY, handler_name)
        except Exception as e:
            p = os.path.abspath(file_name)
            print(bcolors.FAIL, '*' * 80)
            print('could not load file:')
            print(p)
            print(str(e))
            print('.' + mod_name)
            print('*' * 80, bcolors.ENDC)

handler_registry = REGISTRY