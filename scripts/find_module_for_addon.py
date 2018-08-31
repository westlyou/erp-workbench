#!bin/python
# -*- encoding: utf-8 -*-
import os
import sys
from os import walk

if len(sys.argv) != 2:
    print("need exactly one argument")
    sys.exit()

base_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.insert(0, base_path)

ilist = [eval(p)[1] for p in open('%s/.installed' % base_path, 'r').read().split('\n') if p]
site_path = '%s/%s' % (base_path, sys.argv[1])
if not os.path.exists(site_path):
    print("%s does not exist" % site_path)
    sys.exit()
    

f = []
for (dirpath, dirnames, filenames) in walk(site_path):
    for f in dirnames:
        if f in ilist:
            print('%s,%s,%s' % (f, os.path.split(dirpath)[-1], '%s/%s' % (dirpath, f)))



