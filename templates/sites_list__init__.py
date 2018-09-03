import importlib
import os
import sys
os.chdir(__path__[0])
files = os.listdir('.')
sys.path.insert(0, '.')
SITES_G = {}
importlib.invalidate_caches()
for file_name in files:
    try:
        n, e = file_name.split('.')
    except:
        continue
    if n != '__init__' and e == 'py':
        fun = importlib.import_module(n)
        SITES_G.update(getattr(fun, n))
