# -*- encoding: utf-8 -*-
from scripts.bcolors import bcolors
MARKER = '# ---------------- marker ----------------'

SITE_EXISTED = """------------------------------------------------
To use the new settings (if any) execute
cd %(project_path)s
or by executing
%(site_name)sw
and then execute the following command:
bin/build_%(erp_version)s

when you later change the addon-path settings, you can execute:
bin/dosetup_%(erp_version)s

to rebuild the addon-path.

run:
bin/build_%(erp_version)s -f

to see all options
------------------------------------------------
"""
SITE_NEW = """------------------------------------------------
An alias %%(site_name)s has been created for you.
In a %snew%s shell you can execute
%%(site_name)sw
To create the new site execute the following commands:
cd %%(project_path)s
bin/build_%%(erp_version)s.py
bin/dosetup_%%(erp_version)s
------------------------------------------------
""" % (bcolors.WARNING, bcolors.ENDC)

SITE_NOT_EXISTING ="""%s------------------------------------------------
site with name %%s does not exist
------------------------------------------------%s
""" % (bcolors.WARNING, bcolors.ENDC)

VCS_MSG = """
%supdating %%s from %%s%s""" % (bcolors.WARNING, bcolors.ENDC)

VCS_MSG_DEVELOP = """
%sfound %%s in %%s
not updating!
%s
""" % (bcolors.OKBLUE, bcolors.ENDC)

VCS_OK = """
%supdated %%s from %%s%s
""" % (bcolors.OKGREEN, bcolors.ENDC)

VCS_ERROR = """
%s--------------------------------------------------------
updating %%s produced the following error
--------------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)

VCS_ERROR_END = """%s--------------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)

SITE_NOT_EDITED = """%s
--------------------------------------------------------
please edit the site description of %%s
in %%s
and replace 'xx.xx.xx.xx' with a valid ip address
--------------------------------------------------------
%s
""" % (bcolors.FAIL, bcolors.ENDC)
SITE_HAS_NO_REMOTE_INFO = """%s
--------------------------------------------------------
please edit the site description of %%s
in %%s
and add a remote block like 
        'remote_server' : {
            'remote_url'    : 'localhost', #, please adapt
            'remote_data_path'   : '/root/erp_workbench',
            'remote_user'   : 'root',
            'remote_sites_home'    : '/home/robert/erp_workbench',
            'redirect_emil_to' : '', # redirect all outgoing mail to this account
                                     # needs red_override_email_recipients installed
        },
--------------------------------------------------------
%s
""" % (bcolors.FAIL, bcolors.ENDC)

SITE_UNKNOW_IP = """%s
--------------------------------------------------------
please add the ip %%s found in the site description %%s
to config/servers.yaml
you can do so by executing:
bin/c support --add-server %%s@%%s
--------------------------------------------------------
%s
""" % (bcolors.FAIL, bcolors.ENDC)

SITE_CREATED_SERVER = """%s
--------------------------------------------------------
added a server with the %sip %%s for user %%s%s
%sPlease check its content by editing config/servers.yaml
--------------------------------------------------------
%s
""" % (bcolors.OKGREEN, bcolors.FAIL, bcolors.ENDC, bcolors.OKGREEN, bcolors.ENDC)

SITE_CREATED_SERVER_BAD_IP = """%s
--------------------------------------------------------
server info %%s
is not valid.
Must be of the form username@server_ip
--------------------------------------------------------
%s
""" % (bcolors.FAIL, bcolors.ENDC)

SITE_ADDED_NO_DOT = """%s
--------------------------------------------------------
site name %%s
is not valid.
No dot allowed
--------------------------------------------------------
%s
""" % (bcolors.WARNING, bcolors.ENDC)

SITE_DESCRIPTION_RELOADED = """%s
--------------------------------------------------------
An updated sites list was pulled from the repository.
site name(s) %%s reloaded.

You need to reexecute %%s
--------------------------------------------------------
%s
""" % (bcolors.WARNING, bcolors.ENDC)
# -------------------------------------
# sites_handler
# -------------------------------------

EXTRA_SCRIPTS_PATH_FAILED = """
%sIt was not possible to create the extra_scripts folder!
-------------------------------------------------------
The folder %%s
could not be created.
=======================================================
%%s
=======================================================
----------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)
EXTRA_SCRIPT_NOT_EXISTING = """
%sScript to execute not found!
------------------------------
The script %%s
could not be found.
----------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)
LOCALDATA_CREATED = """
A new set of remote servers was created for you!
----------------------------------------------------
it is in %%s
%sIts content must be edited before it can be used%s
At least line:
----------- UNEDITED ----------------
must be removed!
this can be done executing:
bin/c support --edit-server
----------------------------------------------------
""" % (bcolors.WARNING, bcolors.ENDC)

LOCALDATA_NOT_EDITED = """
The local data
%%s
%sis not edited yet%s. you must do so before
you can use bin/c
%sAt least line:
----------- UNEDITED ----------------
must be removed!%s
this can be done executing:
bin/c support --edit-server
""" % (bcolors.FAIL, bcolors.ENDC, bcolors.WARNING, bcolors.ENDC)

LOCALDATA_MOVED = """
%%s has been moved
----------------------------------------------------
it is now in %%s
%sPlease check its content and restart bin/c%s
----------------------------------------------------
""" % (bcolors.WARNING, bcolors.ENDC)

# SITE_TEMPLATE also exists in splitter as SITE_TEMPLATE
SITES_GLOBAL_TEMPLATE = """%s = {
    %s
}
"""
LOCALSITESLIST_CREATED = """
Two siteslists have been created for you
----------------------------------------------------
%%s
%%s
%sPlease check their content and restart bin/c%s
you can check and adapt them by executing:
bin/c -ls
and
bin/c support --edit-site demo_global
----------------------------------------------------
""" % (bcolors.WARNING, bcolors.ENDC)

LOCALSITESLIST_CLONED = """
----------------------------------------------------
The siteslists have been cloned from:
%%s
into %%s/sites_list
%sPlease check their content%s
----------------------------------------------------
""" % (bcolors.WARNING, bcolors.ENDC)
LOCALSITESLIST_BASEPATH_MISSING = """
Can not  create sites list
%s----------------------------------------------------
directory %%s
does not exist. Please create it.
----------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)
LOCALSITESLIST_MARKER_MISSING = """
%s
the marker
%s
could not be found in config/servers.yaml
please add it inside REMOTE_SERVERS, so it reads something like:
REMOTE_SERVERS = {
%s
    ...
}
do do so, you can execute:
bin/c support --edit-server
%s
""" % (bcolors.FAIL, MARKER, MARKER,bcolors.ENDC)


# -------------------------------------
# handling addons
# -------------------------------------
OWN_ADDONS_NO_DEVELOP = """
----------------------------------------------------
%sThe site description %%s
has no deleloper section. %s
Consider adding on in the form of:
'develop' : {
    'addons' : ['xx', 'yy'],
},
----------------------------------------------------
""" % (bcolors.WARNING, bcolors.ENDC)

# -------------------------------------
# geting git repro
# -------------------------------------
GIT_REPO_DIVERGED = """
----------------------------------------------------
%sThe repository at %%s has diverged
and must be merged manually
----------------------------------------------------
%s
""" % (bcolors.FAIL, bcolors.ENDC)

# =============================================================
# add site to bash_aliases
# =============================================================
DOCKER_CLEAN = """
alias docker-clean=' \\
  docker ps --no-trunc -aqf "status=exited" | xargs docker rm ; \\
  docker images --no-trunc -aqf "dangling=true" | xargs docker rmi ; \\
  docker volume ls -qf "dangling=true" | xargs docker volume rm'
"""
DOC_ET_ALL = """
alias  doc="cd %(user_home)s/Documents"
alias  down="cd %(user_home)s/Downloads"
alias  drop="cd %(user_home)s/Dropbox"
"""
WWB = """
# workbench
alias wwb="cd %s"
alias mh='(cd help; make html)'
"""
WWLI = """
# sites-list
alias wwli="cd %s"
"""
WWDA = """
# erp data
alias  wwda="cd %s"
"""
VIRTENV_D = """
#deactivate virtual env
alias d="deactivate"
"""
ALIAS = """
# %(lname)s
alias  %(sname)s="cd %(ppath)s/%(lname)s/%(lname)s"
alias  %(sname)sw="workon %(lname)s"
alias  %(sname)shome="cd %(ppath)s/%(lname)s/"
alias  %(sname)sa="cd_function %(ppath)s/%(lname)s/%(lname)s/%(sname)s_addons %(sname)s"
alias  %(sname)sc="cd %(dpath)s/%(lname)s/addons; do_checkit"
"""
ALIASC = """
alias  do_checkit="for x in *; do echo ----------; echo \$x; echo ----------; ( cd \$x; git status; ) ; done"
"""
ALIASOO = """
alias  wwbw="workon workbench"
"""
ALIAS_LINE = 'alias  %(sname)s="cd %(path)s"\n'
AMARKER = '##-----wb alias-marker %s-----##'
ABLOCK = """%(aliasmarker_start)s
# please do not change the lines between the two markers
# they are managed by the erp-workbench scripts
%(alias_header)s
%(alias_list)s
%(aliasmarker_end)s"""
ALIAS_LENGTH = 4

ALIAS_HEADER = """
cd_function() {
    if [ $2 ]; then
        if [ $3 ]; then
            if [[ -d %(pp)s/$2/addons/$3 ]]; then
                cd %(pp)s/$2/addons/$3
            elif [[ -d %(pp)s/$2/addons/ ]]; then
                cd %(pp)s/$2/addons
            else
                cd %(pp)s/addons
            fi
        else
            if [[ -d %(pp)s/$2/addons ]]; then
                cd %(pp)s/$2/addons
            else
                cd %(pp)s
            fi
        fi
    else
        # will never be reached ..
        cd $1
    fi
}
"""
# -------------------------------------
# odoo
# -------------------------------------
ERP_VERSION_BAD ="""%s------------------------------------------------
Site %%s has a badly defined odoo version %%s
it should be a string like '9.0', '10.0', '11.0' ..
------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)

ERP_NOT_RUNNING ="""%s------------------------------------------------
Site %%s seems not to run!
------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)

# -------------------------------------
# docker_handler
# -------------------------------------
DOCKER_DB_MISSING = """
%s--------------------------------------------
the database container db could not be found
please create it.
do do so, you can execute:
bin/c docker -dcdb
---------------------------------------------%s
""" % (bcolors.FAIL,bcolors.ENDC)

DOCKER_IMAGE_PULLED = """
%s--------------------------------------------
a new image %%s for container %%s was pulled
please stop and recreate all container using it
you can do so by executing:
bin/c docker -dr SITENAME
---------------------------------------------%s
""" % (bcolors.OKGREEN,bcolors.ENDC)

DOCKER_IMAGE_PUSHED = """
%s--------------------------------------------
image %%s for container %%s was pushed
---------------------------------------------%s
""" % (bcolors.OKGREEN,bcolors.ENDC)

DOCKER_IMAGE_PUSH_MISING_HUB_INFO = """
%s--------------------------------------------
mage for container %%s could not be pushed
since there is no docker hub info
---------------------------------------------%s
""" % (bcolors.FAIL,bcolors.ENDC)

DOCKER_IMAGE_NOT_FOUND = """
%s--------------------------------------------
image %%s coud not be found
---------------------------------------------%s
""" % (bcolors.OKGREEN,bcolors.ENDC)

DOCKER_IMAGE_PULL_FAILED = """
%s--------------------------------------------
a new image %%s for container %%s could not be pulled
---------------------------------------------%s
""" % (bcolors.FAIL,bcolors.ENDC)

DOCKER_IMAGE_CREATE = """
%s--------------------------------------------
a new image %%s for container %%s was created
please stop and recreate all container using it
you can do so by executing:
bin/c docker -dr SITENAME
---------------------------------------------%s
""" % (bcolors.OKGREEN,bcolors.ENDC)

DOCKER_IMAGE_CREATE_FAILED = """
%s--------------------------------------------
a new image %%s for container %%s could not be created
---------------------------------------------%s
""" % (bcolors.FAIL,bcolors.ENDC)

DOCKER_IMAGE_CREATE_ERROR = """
%s--------------------------------------------
a new image %%s for container %%s could not be created
ERROR: %%s
Please make sure, that there is a src directory within
the docker folder of the site data structure
It should contain the actual source of the odoo version
the site is using.
---------------------------------------------%s
""" % (bcolors.FAIL,bcolors.ENDC)

DOCKER_IMAGE_CREATE_MISING_HUB_INFO = """
%s--------------------------------------------
a new image for container %%s could not be created
since there is no docker hub info
---------------------------------------------%s
""" % (bcolors.FAIL,bcolors.ENDC)

DOCKER_IMAGE_CREATE_MISING_HUB_USER = """
%s--------------------------------------------
a new image for container %%s could not be created
since there is no docker user or no password defined
---------------------------------------------%s
""" % (bcolors.FAIL,bcolors.ENDC)

DOCKER_INVALID_PORT = """
%s--------------------------------------------
The sitedescription for the site %%s has an
invalid docker port '??'
to fix it, you can execute:
bin/c support --edit-site %%s
---------------------------------------------%s
""" % (bcolors.FAIL,bcolors.ENDC)

DOCKER_IMAGE_CREATE_PLEASE_WAIT = """
%s--------------------------------------------
About to create a new docker image. Please be patient
This process will take up to some minutes, and no output
will be provided until it is done.
---------------------------------------------%s
""" % (bcolors.WARNING, bcolors.ENDC)

DOCKER_IMAGE_CREATE_DONE = """
%s--------------------------------------------
Finished to create docker image.
Now it is the appropriate time to tag and upload it to
your docker hub account.
Todo so, make sure that you computer is logged into
your docker hub account and then 
please execute the following two commands:

docker tag %%s %%s
docker push %%s
---------------------------------------------%s
""" % (bcolors.OKGREEN, bcolors.ENDC)

# -------------------------------------
# missing modules
# -------------------------------------
MODULE_MISSING ="""%s------------------------------------------------
%%s could not be loaded.

To install it, please execute following commands:
wwb;bin/pip install -r install/requirements.txt
------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)

# -------------------------------------
# email stuff
# -------------------------------------
CUSTOMER_UNKNOWN ="""%s------------------------------------------------
froxlor customer %%(customer)s defined for site %%(site_name)s
does not exist in the froxlor db
------------------------------------------------%s
""" % (bcolors.FAIL, bcolors.ENDC)
