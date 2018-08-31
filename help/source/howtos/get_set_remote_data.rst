Get or Set Data from/to remote Site
-----------------------------------

This howto explains, how to get a sites data from a remote server.

Alltough this is normally a one way process as we only want to get the data
from a life server to the local developement environment, it is also possible 
to "send" the local data to the life server.

Sending data to the remote life server migth be advisable when a new site is deployes, 
after a massive local reconstruction or after an upgrade to a newer odoo version.


The Commadns / Options to use are the following::

    # -u        : update local data from the remote server taken from the site description
    # SOURCE    : the site to be used as source
    # -N        : use only local data for SOURCE
    #             if not set, fetch data from the life server
    # -nupdb    : do not update the local postgres database
    #             if not set, the local postgres database is droped
    #             and recreated from the dumpfile in SOURCE/dump/SOURCE.dmp
    #             if set, the data is just copied from the remote site

    # copy the remote data of the site afbschweiz 
    # to the local box and recreate the local database
    bin/c -u afbschweiz

    # just copy the remote data to the local computer
    bin/c -u -nupdb afbschweiz

    # just recreate the local database
    bin/c -u -N afbschweiz

    # just do nothing :)
    bin/c -u -N -nupdb afbschweiz
