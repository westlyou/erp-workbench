Delete a local workkbench project
---------------------------------

You can remome all locally installed elements of a workbench project.
This will erase the followin elements:

    - $HOME/projects/$SITENAME
    - $OODA/$SITENAME # this $OODA is normaly the erp-workbench folder (erp_workbench)
    - drop database $SITENAME
    - remove virtualenv $SITENAME

Delete local workbench data::

    bin/c --DELETELOCAL SITENAME

    # for example to remove redhelp 
    bin/c --DELETELOCAL redhelp
