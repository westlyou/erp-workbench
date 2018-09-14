============================
Introduction and first steps
============================

ERP Workbench is a set of tools that are used to create and maintain local and remote
erp (odoo, flectra, ..) sites.

Objects that are maintained by erp-workbench are at three different locations:

    If you have installed it as proposed in the INSTALL.txt these locations are as follows:

    - ~/erp_workbench  ($WB in this documentation)
        that is where ERPW is installed and site-descriptions are maintained

    - ~/projects ($PROJECT in this documentation, or $SITE when the site description is meant)
        This is where for each local site a folder structure is maintained

    - remote servers (anywhere out there ..)
        This is where docker containers running the sites are hosted

Command categories:
-------------------
Commands are grouped in several categories:

    - create / update
    - docker
    - support
    - remote

Create objects:
***************
    bin/c *COMMAND*

    where *COMMAND* could be:

    Commands normally run locally:

    - **-ls**
        list all projects
    - **-c** *project_name* 
        | generate local project *project_name* in the project folder
        |   generate the needed folder structure
        |   download or upgrade all addons as mentioned in the *project_name*'s site-descriptions
        |   generate all aliases
    - **-lo** *project_name* 
        | list own modules mentioned in the *project_name*'s site-descriptions
    - **-I** *project_name* 
        | install all odoo modules (like CRM) as mentioned in the *project_name*'s site-descriptions
    - **-uo** [modules-list]|all *project_name* 
        | install/update own modules as found in the *project_name*'s site-descriptions
        | [modules-list] is a comma separated list of mdule names
        | if all is used as modules list, then all modules found in the sites descrition are installed

    Commands normally run remotelly:
    
    - **m**
        like -c but do not create project
        |   generate the needed folder structure
        |   download or upgrade all addons as mentioned in the *project_name*'s site-descriptions
        |   generate all aliases

    - **M** addons-list 
        download or upgrade addons-list addons thei must be mentioned in the sites descriptions

Docker handling
***************
    bin/d *COMMAND*

Support commands 
****************
    bin/s *COMMAND*
    bin/e [$SITE]

    Commands to add or remove site descriptions

    **--add--site** [--docker-port][--remote-server]
        add globale site to the 

Remote commands
***************
    bin/r *COMMAND*

    Commands that make only sense remotelly

    **--add-apache**
        build an apache entry for the site

    **--add-nginx**
        build an nginx entry for the site
