#!/usr/bin/python
# -*- encoding: utf-8 -*-
import subprocess
from subprocess import PIPE
import os
import sys

# we get the following parameters:
# $1 : site name
# $2 : server url
# $3 : path to the site home in the users directory (/home/anyuser/odoo_sites)
# $4 : login name on remote server
# $5 : path to instances home on the remote server (/root/odoo_sites)

site_name     = sys.argv[1]
server_url    = sys.argv[2]
usr_site_home = sys.argv[3]
user_name     = sys.argv[4]
site_home     = sys.argv[5]

# rsync the stuf
cmd_line = "rsync -av %s/%s/ %s/%s/" % (site_home, site_name, usr_site_home, site_name)
p = subprocess.Popen(cmd_line, stdout=PIPE, shell = True)
p.communicate()

# change ownership
cmd_line = "chown  %s:%s %s/%s" % (user_name, user_name, usr_site_home, site_name)
p = subprocess.Popen(cmd_line, stdout=PIPE, shell = True)
p.communicate()
# again but recursive
cmd_line = "chown  %s:%s %s/%s -R" % (user_name, user_name, usr_site_home, site_name)
p = subprocess.Popen(cmd_line, stdout=PIPE, shell = True)
p.communicate()
