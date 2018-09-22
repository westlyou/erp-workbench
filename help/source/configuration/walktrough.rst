-------------------------
Configuring erp-workbench
-------------------------

To configure erp-workbench to your needs, you adapt a number
of yaml files.
You find them in $WB/config

These config files are checked when ever you perform an erp
task if they are still accurate (by checking their file date).
If a change is detected the changed yaml file(s) is loaded and
converted into a python dictionary in $WB/config/config_data.

There are several groups of configuration options.
These are:

    - config
        Here we do basic configuration
    - projects
        Here we configure how to handle erp-workbench projects
    - docker
        Here we configure wo to handle docker
    - servers
        Here we configure how to handle remote servers

For each configuration group there is yaml.in file with the default
values for this configuration group. 
When you execute your first erp-workbench command, they will be copied to 
files without the .in extension.
So config.yaml.in will be copied to config.yaml etc.

You will get a warning to check the yaml files.

reset to factory defaults
-------------------------
To reset all your configuration to their default values, just
delete all yaml files in $WB/config.
They will be recreated the next time you execute an erp-workbench
command.
You will get a warning to check the yaml files.


config.yaml
-----------

In this configuration group we define where erp-workbench finds its data on
the local host and also from where to download its project files.

project.yaml
------------
Here we define what are the default values to use when creating a new project.

docker.yaml
-----------
Her we define how to create docker containers, what images to use where to get the from
Again, these are only the default values and must be set per erp site.

servers.yaml
------------
Here we define what servers we use and what are the configuration details
like where the $SITE-folders are located or how to access them.
You can create new entries into this file by executing::

    bin/s add-server $SERVERNAME

