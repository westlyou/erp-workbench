#!/bin/sh
# updatedb.sh executes the script dodump_remote on a remote server
# it runs site_syncer on the remote server. this script runs as root
# and rsyncs the sites files to a place from where we can copy it
# parameters:
# $1 : site name
# $2 : server url
# $3 : remote_data_path like /root/odoo_instances
# $4 : login name on remote server
# $5 : path to instances home on the remote server (/root/odoo_sites)
    #!/bin/sh
    ## dodump.sh dumps a site's database into its folder
    ## the folder is /root/odoo_instances/$1/dump where $1 represents the site's name
    ## dodump creates a temporary docker container that dumps a servers database
    ## it is called by updatedb.sh and executed on the remote computer
    ## $1 : name of the server                     updatedb.$1
    ## $2 : path to the location of odo_instances  updatedb.$3
    ##      on the remote server
    ## $3 : verbose flag                           updatedb.$7
    #echo '----------- running dodump ----------------'
    #FILE=$2/dumper/rundumper.py
    #echo "FILE:$FILE"
    #echo $HOSTNAME
    #if [ -f "$FILE" ]
     #then {
        #echo 'calling python' $FILE $1 $3
        #python $FILE $1 -d $3
    #}
    #else {
        #echo 'kein rundumper'
        #sudo docker run -v $2:/mnt/sites  --rm=true --link db:db  dbdumper -d $1
    #}
    #fi

echo '----- updatedb_remote calling dodump_remote ----'
echo $(pwd)
echo ssh $4@$2 'bash -s' < scripts/dodump_remote.sh $1 $2 $3 $4 $5
ssh $4@$2 'bash -s' < scripts/dodump_remote.sh $1 $2 $3 $4 $5
