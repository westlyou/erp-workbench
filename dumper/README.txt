# README.txt
# ----------
# dbdumper is part of the odoo maker suite found at
# http://gitlab.redcor.ch/open-source/odoo_instances
# it can be downloaded from: http://gitlab.redcor.ch:10080/open-source/odoo_instances.git

create dbdumper image:
----------------------
    to be able to do transfer data from/to a database within docker, we need a dbdumer image
    this can be created as follows:

        cd dumper
        # make sure that the ubuntu version used in the dockerfile
        # employs the same postgres version, as the one running in the container named 'db'
        docker build  -t dumper . # this creates the image

        afterwards you have to tag the image with:
        docker tag dumper(or image id) robertredcor/dumper

        maybe it is

        test it:
            dbdumper assumes a directory layout as described under "use dbdumper image:"
            assuming that your odoo instances are in the folder /root/odoo_instances/root/odoo_instances
            you can run the following command:
                docker run -v /root/odoo_instances:/mnt/sites --rm=true --link db:db -it dbdumper -h

use dbdumper image:
-------------------
    dbdumper expects the following directory layout
    BASEDIR can be any folder:
        BASEDIR/dumper
            with dumper.py
            ...
        BASEDIR/SITENAME
            addons
                additional addons (not used by dbdumper)
            dump
                to this folder the database will be dumped to / read from
            etc
                here is odoo's config file (not used by dbdumper)
            filestore
                here are the external files stored (not used by dbdumper)(not used by dbdumper)
            log
                here is odoos log file stored (not used by dbdumper)
            ssl
                (not used by dbdumper)

create odoo docker container using folder structure:
----------------------------------------------------
    to create a docker container "afbstest" using the above lined out folder sturcture
    BASEDIR is /root/odoo_instances/ in this example:
    docker run -p 127.0.0.1:8071:8069 \
        -v /root/odoo_instances/afbstest/etc:/etc/odoo \
        -v /root/odoo_instances/afbstest/addons:/mnt/extra-addons \
        -v /root/odoo_instances/afbstest/dump:/mnt/dump \
        -v /root/odoo_instances/afbstest/filestore:/var/lib/odoo/filestore \
        -v /root/odoo_instances/afbstest/log:/var/log/odoo \
        --name afbstest -d --link db:db -t odoo:9.0
