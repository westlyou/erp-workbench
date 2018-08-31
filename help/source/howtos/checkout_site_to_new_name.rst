Checkout site to new Name
-------------------------

When getting a remote site, we can copy the sites data to a new folder

The Commadns / Options to use are the following::

    # -dump     : dump the data from the actually running local site
    # SOURCE    : the site to be used as source
    # -NTS      : option to indicate that we want to copy SOURCE to a new TARGET
    # TARGET    : the target site of the copy operation
    # -N        : use only local data for SOURCE
    #             if not set, fetch data from the life server
    # -F        : force copying the existing data, when a site other than SOURCE is running
    #             if not set, either SOURCE must be running, then the data is dumped from the
    #             running site before copying, or if no site is running
    #             the existing data is copied to the TARGET structure
    bin/c -dump SOURCE -NTS TARGET -N -F


Copying from a remote that differs from the life site to a new local target::

    # this has to be done in two steps:

    # step 1:
    # first, copy data from remote to local
    # -u        : update local postgres db from remote site
    # -ip       : use source server's IP
    # -nupdb    : do not restore the fetched data into the local postgres database
    #             if this flag is not set, the local postgress db is droped and
    #             recreated with the copied data
    bin/c -u afbschweiz -ip mozart -nupdb
    # or using option -uu
    # -uu same as -u but kill all open db connection to db afbschweiz
    bin/c -uu afbschweiz -ip mozart -nupdb

    # step 2
    # in the second step we copy the local SOURCE to TARGET
    # -N        : norefresh. Use only local data to copy from SOURCE to TARGET
    #             without this flag the SOURCE would first be fetched from the
    #             sources life site. this would CONTRADICT the option -ip
    #             that was used in the first step!
    # -NTS      : use new target afbstest
    bin/c -dump afbschweiz -N -NTS afbstest

Copying afbschweiz to afbstest would be like this::

    bin/c -u afbschweiz -NTS afbstest

You can use the *-N* modifier to prevent downloading the data from the source::

    # Copying afbschweiz to afbstest, using only local data
    bin/c -u afbschweiz -NTS afbstest -N

Use *-uu* to *kill* all active db connections to SITE on the local host:

    # Copying afbschweiz to afbstest, using only local data
    # killing all active db connections
    bin/c -u afbschweiz -NTS afbstest -N

Use the *-ipt* option to define to what *target server* the data should be copied::

    # Copying afbstest to server LISA
    # -dump     : dump afbstes, if astest is not runnin, just use existing files
    # -N        : do not refresh local data from live server
    bin/c -dump afbstest -ipt lisa -N


Use the freshly copied data on the remote machine and read it into a docker container::

    this needs several steps:
    - update odoo workbench
    - update SITE (here afbstest)
    - restart the container
    - read the dumped data

    ooin 
    git pull
    bin/c -m afbstest
    docker restart afbstest
    bin/d -dud -N afbstest  -v 

    # if the freshly copied data needs an upgrde, or some fiddeling with odoo
    # you can start an update docker container like so 

    # remove old container
    docker stop afbstest
    docker rm afbstest 
    # run update container. It will stop as soon as its odoo -u all --stop-after-init hasfinished running
    bin/d -dcu afbstest

    # create a new afbstest container
    bin/d -dc afbstest