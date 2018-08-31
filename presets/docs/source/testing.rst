=======================
Test the Preset-Manager
=======================

To test the preset manager, you have to have a running erp site
called presettest, created using the redo2oo erp management tools

To create this testsite follow these steps
------------------------------------------

    Create local site::

        ooin 
        bin/s --add-site-local presettest
        bin/c -c presettest

    in a new bash window build and run the new site::

        presettestw # activates virtual env, and cd's into the project directory
        bin/build_odoo.py 
        bin/odoo

    to delete the db and recreate it::

        presettestw
        dropdb presettest
        bin/odoo