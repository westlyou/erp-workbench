#!/bin/sh
# dodump_remote.sh rsyncs a remote site in /root/odoo_sites/SITENAME
# to /home/somesuer/odoo_sites/SITENAME, so we can rsync it from there
# the folder is /root/odoo_instances/$1/dump where $1 represents the site's name
# parameters:
# $1 : site name
# $2 : server url
# $3 : remote_data_path like /root/odoo_instances
# $4 : login name on remote server
# $5 : path to instances home on the remote server (/root/odoo_sites)
echo '----- dodump_remote ----'
echo sudo $5/scripts/site_syncer.py $1 $2 $3 $4 $5
sudo $5/scripts/site_syncer.py $1 $2 $3 $4 $5
