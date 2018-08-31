from __future__ import absolute_import
import sys
import os
from config import SITES_HOME
os.environ['SITES_HOME']=SITES_HOME

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
#from . import tests
#from . import manager
