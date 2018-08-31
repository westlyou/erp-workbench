============================
Introduction and first steps
============================

ERP Workbench is a set of tools that are used to create and maintain local and remote
ERP (odoo, flectra, ..) sites.

Objects that are maintained by ERPW are at three different locations:

    - ~/odoo_instances  
        that is where ERPW is installed and site-descriptions are maintained

    - ~/projects
        This is where for each local site a folder structure is maintained

    - remote servers
        This is where docker containers running the sites are hosted

Command categories:
-------------------

Create objects:
***************
    bin/c *COMMAND*

    where *COMMAND* could be:

    - **-ls**
        list all projects
    - **-c** *project_name* 
        | generate project *project_name*
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

Docker handling
***************
    bin/d *COMMAND*

