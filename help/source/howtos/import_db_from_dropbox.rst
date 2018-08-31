Create db from dropbox
----------------------

.. create_db_form_dropbox:


Create purge and recreate local afbstest project
++++++++++++++++++++++++++++++++++++++++++++++++

Instructions to recreate afbstest::

    # first you have to refresh things:
    ooli; git pull
    ooin; git pull

    # purge all elements of an existing installation
    # this you only need to do if approriate
    bin/c --DELETELOCAL afbstest

    # after having purged things,  you have to recreate everything
    bin/c -c afbstest # this builds the afbs project structure
    afbstestw   # activate afbstests virtual env a
                # nd cd to the project folder
    bin/build_odoo.py   # download odoo and install it. 
                        # this will also create odoo's config file
    bin/odoo    # this will start odoo
    
    # then back to odoo_instances in a second bash shell
    d # this will deactivate an active virtual env
    ooin # cd into the odoo_instances folder
    bin/c -uo all afbstest  # install/update all addons 
                            # defined for afbstest
                            # now you have an empty database 
                            # with everything installed


(re)construct database from running site
++++++++++++++++++++++++++++++++++++++++

This howto assumes, that the two folders:

    - ~/Dropbox/afbstest/filestore
    - ~/Dropbox/afbstest/dump

exist, and have been provisioned with data of an actual sites.

Please adapt the following instructions accordingly, if your folderstructure is different.

steps to provision the afbssite database with data from a running system::

    # rsync the files to the correct folder
    rsync -av  --delete ~/Dropbox/hilar/afbstest/filestore/ afbstest/filestore/
    rsync -av  --delete ~/Dropbox/hilar/afbstest/dump/ afbstest/dump/
    
    # now you have to read in the data:
    # first make sure afbstest is running!
    ooin # to make sure we are in the rigth place
    bin/c -uu afbstest  -N  # this kills the running odoo, but remembers 
                            # where it has been running
                            # the -N option instructs the process to use existing data, 
                            # and not to reload it affresh
                            # the it drops the afbstest database
                            # and runs pg_restore -O -U afbstest/dump/afbstest.dmp
                            # after that, you have to restart odoo


Add new addon to site description
---------------------------------

When a new addon is added to a site description the following steps are involed:

1. add the addon to the addon part of the description
2. (re) generate the project
3. generate a new odoo config with the adapted addons-path
4. install the new addon into a running odoo

In the following example we add the addon 'l10n_ch_payment_fix_pos' to the site-description 
afbstest.
This is a somehow special case, as afbstest inherits its settings from afbs, and by default has
no own addons block in its site description. Therefore we must add it.

to add the new addon execute the following::

    ooin
    bin/e afbstest # this will start an editor with the afbstest site description
    # i this description add the following block
    # if unsure where to add it, loock at afbs.py in the same folder as afbstest.py
        'addons' : [
            {
                'type' : 'git',
                'url' : '%(gitlab.redcor.ch)s/l10n_ch/l10n_ch_payment_fix_pos.git',
                'name' : 'l10n_ch_payment_fix_pos',
                'group' : 'l10n_ch_payment_fix_pos',
                'branch' : '9.0',
            },
        ],

    # to download and install the addon in the addons hierarchy of afbstest
    # execute:
    bin/c -c afbstest

The above steps have added the addon to the local filesystem, but odoo nows yet nothing about it.
Therefore we must adapt odoos addon-path.

Steps to adapt odoos addon-path::

    afbstewstw # this activates a virtual env, and cd's to the project path
    bin/dosetup_odoo.py # this generates the new addons path
    bin/odoo # start odoo

Now odoo has access to the new module, so we can install it. To do so, the afbstest site must be running.

Steps to install the new addons with all its dependencies::

    ooin # change to odoo_instances
    bin/c -uo all afbstest # this install all new addons, and updates the existing ones
    # alternatively, we can also just install the newly added addon like so:
    bin/c -uo l10n_ch_payment_fix_pos afbstest

