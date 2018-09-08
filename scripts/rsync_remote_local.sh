#!/bin/sh
# updatedb.sh executes the script dodump on a remote server
# dodump creates a temporary docker container that dumps a servers database
# into this servers data folder within erp_workbench
# parameters:
# $1 : site name
# $2 : server url
# $3 : remote_data_path like /root/erp_workbench
# $4 : login name on remote server
# $5 : local odoo_server_data_path
# $6 : target site name
# echo ssh $4@$2 'bash -s' < scripts/dodump.sh $1
# ssh $4@$2 'bash -s' < scripts/dodump.sh $1 '/root/erp_workbench'
echo rsync -avzC --delete $4@$2:/$3/$1/filestore/$1 $5/$6/filestore/$6
rsync -avzC --delete $4@$2:/$3/$1/filestore/$1 $5/$6/filestore/$6
echo rsync -avzC --delete $4@$2:/$3/$1/dump/$1.dmp $5/$6/dump/$6.dmp
rsync -avzC --delete $4@$2:/$3/$1/dump/$1.dmp $5/$6/dump/$6.dmp
