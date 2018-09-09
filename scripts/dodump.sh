#!/bin/sh
# dodump.sh dumps a site's database into its folder
# the folder is /root/erp_workbench/$1/dump where $1 represents the site's name
# dodump creates a temporary docker container that dumps a servers database
# it is called by updatedb.sh and executed on the remote computer
# $1 : name of the server                     updatedb.$1
# $2 : path to the location of odo_instances  updatedb.$3
#      on the remote server
# $3 : verbose flag                           updatedb.$7
echo '----------- running dodump ----------------'
FILE=$2/dumper/rundumper.py
echo "FILE:$FILE"
echo $HOSTNAME
if [ -f "$FILE" ]
 then {
    echo 'calling python' $FILE $1 $3
    python $FILE $1 -d $3
}
else {
    echo 'kein rundumper'
    sudo docker run -v $2:/mnt/sites  --rm=true --link db:db  dbdumper -d $1
}
fi
