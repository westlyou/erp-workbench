-------------------------------------
A quick walk trough the erp-workbench
-------------------------------------

erp-workbench lets you create erp-sites locally and remotely with ease. It tries to blur the distinction of a site running locally or in a remote docker context.

I this walktrough you learn: 

- Explanation of terms used
- to define what type of erp you handle
- change editor to use
- How to define a remote server
- How to define a new erp site
- Add existing modules to this new site
- Create a local erp project running this site
- Create a docker container running this site
- Backing up data from to the container from to the lacal site

Explanation of terms used
-------------------------
There are a number of terms used in erp-workbensch you should understand the meaning of:

- $WB

This is the erp-workbench's home folder. Often ~/erp-workbench


- Site / Site-Description

An erp-workbench site is defined within a site description file.
There are global sites, of which the site descriptions are shared using git repositories, and
local sites, that are only used on the actual pc.

- $Site

The name of the site

- Project 

A project is a local structure, where a site is constructed and can be run locally.

- $PROJECT

This is a projects home folder. Often ~/projects/$SITE/$SITE

- Remote Server

A remote server is a server accessible trough the internet, where site is deployed to a docker container.


Defining what erp type you handle by default:
---------------------------------------------

For the time being (sept. 2018) there are two types of erp system er-workbench is capable of handling:

    - odoo
    - flectra

Flectra is an odoo fork that has many things with odoo in common.

Selecting the default erp system only defines, what setting will be used when creating a new site. 
By defaul odoo sites will be generated. To change this, do as follows:

in $WB/config/config.yaml change the line::


