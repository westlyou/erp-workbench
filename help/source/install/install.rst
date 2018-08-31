INSTALL.txt
-----------

------------------------
for the ones in a hurry:
------------------------

    # prepare database access:

    the following is done as user zope, but use any username as you wish::

        # as user root add current user to group sudo, so he can execute sudo
        usermod -a -G sudo zope

        # back as user zope (or what ever ..)
        
        sudo -u postgres psql -e --command "CREATE USER $USER WITH SUPERUSER PASSWORD 'admin'
        createdb $(whoami)


    # then:

        - copy users private key to gitlab

    clone odoo workbench (aka odoo_instances)::

        git clone https://gitlab.redcor.ch/open-source/odoo_instances.git
        cd odoo_instances
        virtualenv python
        python/bin/pip install -U setuptools
        bin/pip install --upgrade pip
        bin/pip install -r install/requirements.txt
        bin/c -ls   # enter to all questions
        bin/e       # answer question re gitlab
                    # check if presented file is ok
        bin/ls      # should now present list of sites
        bin/c redhelp   # create redhelp site

By now you have created a project redhelp.
You can now switch to it and build it.
To do so *open a new bash shell*, as the freshly created aliases are not yet active.

build site redhelp::

    # open new bahs terminal
    redhelpw  <--- there is a w at the end
    bin/build_odoo
    bin/odoo

the command bin/c -c redhelp created the following aliases, that are accessible
as soon as you are in a new bash terminal:
redhelp  -> changes into the redhelp project folder
redhelpw -> activates the redhelp virtual environment and changes into the redhelp project folder
redhelpa -> changes into the redhelp addons folder
redhelpc -> changes into the redhelp addons folder and does a git status on all entries
d        -> deactivates the actual virtual environment

how to install virtalenv wrapper:
---------------------------------
the explanation is here:
install/CREATE_SITE.txt

------------------------
end  hurry:
------------------------
------------
PREPARATION:
------------
    create private/public key pair
    ------------------------------
    as normal user issue the following command
        ssh-keygen -t rsa
    just accept all prompts with enter


    the following modules must be installed (as user root):
    -------------------------------------------------------
        postgresql should be up and running
        sudo apt-get install postgresql postgresql-contrib

        install libraries:
            apt-get -y install build-essential libfreetype6-dev libjpeg8-dev liblcms2-dev libldap2-dev libsasl2-dev libssl-dev libffi-dev \
            libtiff5-dev libwebp-dev libxml2-dev libxslt1-dev node-less postgresql-server-dev* python-dev python3-dev \
            python-tk tcl8.6-dev tk8.6-dev zlib1g-dev postgresql-client python-virtualenv git vim npm nodejs-legacy libmysqlclient-dev \
            curl

    create a virtual env:
    ---------------------
        change to target directory:
            cd ~/odoo_instances # this script assumes this directory as base

        create virtual environment:
            virtualenv python
            python/bin/pip install -U setuptools
	    bin/pip install --upgrade pip

        set utf8:
        --------
            vim python/lib/python2.7/site.py
            search "ascii", 2 lines lower, change ascii to utf8


    as normal user:
    ---------------
        install lessc:
            curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
            sudo apt-get install -y nodejs

            sudo npm install -g npm  #(to update npm)
            sudo npm install -g less
            sudo npm install -g less-plugin-clean-css


    add yourself as postgres superuser to the database:
    ---------------------------------------------------
        sudo -u postgres psql -e --command "CREATE USER $USER WITH SUPERUSER PASSWORD 'admin'"


    Install Wkhtmltopdf
    -------------------
    sudo wget -P Downloads http://download.gna.org/wkhtmltopdf/0.12/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb
    cd Downloads
    sudo dpkg -i wkhtmltox-0.12.1_linux-trusty-amd64.deb


    create private/public key pair
    ------------------------------
    as normal user issue the following command
        ssh-keygen -t rsa

    copy the public key to .ssh/autorized_keys on the machine/homedir from
    which you will copy live data
----------------
END PREPARATION:
----------------

-----------------------
create ~/odoo_instances
-----------------------
    As normal user:

    check out repository:
        in your home directory execute the following command:
            git clone ssh://git@gitlab.redcor.ch:10022/open-source/odoo_instances.git
        this will create a folder odoo_instances and clone odoo_instances into it

    set up environment:
        cd odoo_instances
        virtualenv python

    install needed modules:
        bin/pip install -r install/requirements.txt

    -----------------------------------------------
    start bin/c for the first time
    this will create some config files which you have
    to edit, to be able to run bin/c successfully
    -----------------------------------------------
    bin/c   # this will result in a message with hints what to do next

    edit local config data:
    ----------------------
        to be able to use the scripts in bin/ there needs to exist a file
        localdata.py with the following settings. There is a file localdata.py.in
        which you can copy and adapt.
            cp localdata.py.in localdata.py

        localdata.py has this content which should be adapted:
            # db_user is the user used to access the local postgres server
            db_user = 'robert'
            # db_password ist used to login db_user
            db_password = 'odoo'
            # apache_path is used to create virtual sites
            apache_path = '/etc/apache2'
            # remote_user_dic is used to access the remote server to update the local db
            # it is a dic with the ip of the remote server as key
            # which ip to use is read from sites.py
            remote_user_dic {
                '144.76.184.20' : {
                    'user' : 'root',
                    'remote_data_path' : '/root/odoo_instances'
                    # remote_pw is used as credential for the remote user. normaly unset
                    # to use public keys.
                    remote_pw : '',
                }
            }

        see sample localdata.py at the end of this text.

    start for the first time:
    -------------------------
        when you start bin/c.sh or bin/u.sh for the first time you are asked
        to provide the path to where the local projects should be created:
        Accepting the provided default is just fine.
        !!attention!! the folder needs to exist.

---------------------------
END create ~/odoo_instances
---------------------------

--------------
handling sites
--------------
    defining sites:
    ---------------
        the sites are described in three dictionaries (all of them in odoo_sites)
        - sites.py
            here the remote sites are described
        - sites_local.py:
            here you can have local sites described that are not on the
            remote server.
            there is a template file local_sites.py.in which you can copy.
        - sites_pw.py:
            here are the passwords for odoo and the mail accounts
            this file is not under version control and not distributed

        to manage the sites there are a number bash scripts in bin/:
            - bin/c
                this script is used to create local sites
                if available these local sites use the data copied from
                the remote live servers.
                bin/c -h to show its help
            - bin/d
                this script handles docker instances
                it is a shortcut for:bin/c docker
            - bin/e
                this script is to edit site description
                and server descriptions
            - bin/d
                this script handles docker instances
                it is a shortcut for:bin/c docker
            - bin/r
                this script handles remote instances
                it is a shortcut for:bin/c remote
            - bin/s
                this script handles support instances
                it is a shortcut for:bin/c support
            - bin/lc
                this script handles local copies of sites

        help:
        -----
            bin/c.sh -h
            bin/u.sh -h


    creating local sites
    --------------------
    bin/c.sh is used to create local sites. To be able to do so, the site needs
    an entry either in sites.py or sites_local.py.
    You can list the possible sites with:
        bin/c.sh -l
        the output is something like this:
            key2gont
            odoodev (local)
            redcorkmu
            rederpdemo

    Sites defined in sites_local.py are marked with (local).

    To create a site you have to follow three steps:
        - create the site:
            bin/c.sh -n SITENAME -c
        - change to the sites home and prepare the buildout
            (assuming you entered ~/projects as projects home)
            cd ~/projects/SITENAME/SITENAME
            bin/dosetup.py
            (you get error complaining this is not a working copy,
            if ~/projects is not managed by subversion. ignore them)
        - run the buildout:
            bin/buildout

    copy remote data to local_sites
    -------------------------------
    To be able to run a local site with life data you have to set up yourself
    as a postgres superuser:
        add yourself as postgres superuser to the database:
            sudo -u postgres psql -e --command "CREATE USER $USER WITH SUPERUSER PASSWORD 'admin'"


   to copy remote data run:
        ~/odoo_instances$ bin/u.sh -n SITENAME

------------------
END handling sites
------------------

-------------------------------
godies
-------------------------------
The setupscript bin/dosetup.py you have to run in each local site
adds some aliases to your ~/.bash_aliases file. they start with the
first 4 characters to the site name:
so rederpdemo produces:
    rede
    redehome

try it out ..

some usefull postgres commands:
-------------------------------
    list postgres user and change password
    --------------------------------------
    become root
        su
    become user postgres
        su postgres
    start psql
        psql
    list users
        \du
    change password of user robert to be admin
        ALTER USER robert WITH PASSWORD 'admin'

if you ever want to change change the password of an odoo user:
    su
    su postgres
    psql
    \connect DBNAME         # connect to db DBNAME
    # list odoo users
    # password will only be set until user is logged in successfully the first time
    select login, password, password_crypt from res_users;
    # change password of odoo user admin
    update res_users set password='admin' where login='admin';

subversion:
-----------
    add the following line to ~/.subversion/config
    global-ignores = *.o *.lo *.la *.al .libs *.so *.so.[0-9]* *.a *.pyc *.pyo *.rej *~ #*# .#* .*.swp .DS_Store *.egg-info

--------------------
sample localdata.py:
--------------------
    this localdata.py works for accessing files on frieda (144.76.184.20)
    as local user nirmala, and as remote user odooprojects

    # db_user is the used to access the local postgres server
    DB_USER = 'nirmala'
    # db_password ist used to login db_userdb_user
    DB_PASSWORD = 'odoo'
    # apache_pathis used to create virtual sites    if you ever want to change change the password of an odoo user:
            su
            su postgres
            psql
            \connect DBNAME         # connect to db DBNAME
            # list odoo users
            # password will only be set until user is logged in successfully the first time
            select login, password, password_crypt from res_users;
            # change password of odoo user admin
            update res_users set password='admin' where login='admin';

    APACHE_PATH = '/etc/apache2'
    # remote_user_dic is used to access the remote server to update the local db
    # it is a dic with the ip of the remote server as key
    # which ip to use is read from sytes.py
    REMOTE_USER_DIC = {
        '144.76.184.20' : {
            'remote_user' : 'odooprojects',
            'remote_data_path' : '/home/odooprojects/odoo_instances',
            # remote_pw is used as credential for the remote user. normaly unset
            # to use public keys.
            'remote_pw' : '',
        },
    }


setup /etc/sudoerr:
-------------------
on the remote server we have to have a user odooprojects to act as a proxy for these user, that are not
allowed to access the remote server as user root.
in the users homdirectory must exist a folder: /home/odooprojects/odoo_instances
The user has to be added to sudoerrs as follows:

#includedir /etc/sudoers.d
odooprojects ALL = NOPASSWD: /usr/bin/docker
odooprojects ALL = NOPASSWD: /root/odoo_instances/scripts/site_syncer.py




master password:
----------------
check ur odoo8 config file named as: odoo-server.conf. it basically inside of your etc folder.

find and open it.

admin_passwd = admin

here admin is your master password. try this.

EDIT:  If you have changed the master password from the user interface, it is stored in a resource file called .openerp_serverrc in the home directory of the user running the server/service.



echo "--------------------------------------------------"
echo "########## Install Asterisk Dependencies #########"
echo "--------------------------------------------------"
echo -e "---- Installing Dependencies... ----"
sudo apt install -y wget gcc gcc-c++ libncurses-dev libxml2-dev  libsqlite3-dev libsrtp0-dev \
    uuid-dev libssl-dev bzip2 libjansson-dev

# from http://www.mikeslab.net/?p=330
sudo apt-get update; sudo apt-get upgrade -y; sudo apt-get dist-upgrade -y; sudo apt-get install \
    -y build-essential git-core pkg-config subversion libjansson-dev sqlite autoconf automake libtool \
    libxml2-dev libncurses5-dev unixodbc unixodbc-dev libasound2-dev libogg-dev libvorbis-dev libneon27-dev \
    libsrtp0-dev libspandsp-dev uuid uuid-dev sqlite3 libsqlite3-dev libgnutls-dev libtool-bin python-dev texinfo;
    #sudo shutdown -r now

echo "--------------------------------------------------"
echo "########## Install PJSIP #########"
echo "--------------------------------------------------"
mkdir /root/aserisk
cd /root/asterisk
git clone https://github.com/asterisk/pjproject pjproject
cd pjproject
./configure --prefix=/usr --enable-shared --disable-sound --disable-resample --disable-video --disable-opencore-amr CFLAGS='-O2 -DNDEBUG -DPJ_HAS_IPV6=1'
make
make dep
make install
ldconfig
# check whether modules are loaded with
ldconfig -p | grep pj


echo "--------------------------------------------------"
echo "############## Install Asterisk ##################"
echo "--------------------------------------------------"
sudo cd /usr/src
sudo wget wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-13-current.tar.gz
sudo tar zxvf asterisk*
sudo cd ./asterisk*
sudo ./configure  --with-pjproject-bundled

echo "--------------------------------------------------"
echo "############## Disable Resource RES-SRTP ##################"
echo "--------------------------------------------------"
sudo make menuselect
sudo make && sudo make install

echo "-------------------------------------------------------------------------"
echo "############## Install Configuration Files and Service ##################"
echo "-------------------------------------------------------------------------"
sudo make samples
sudo make config

echo "------------------------------------------------------"
echo "############## Install Certificates ##################"
echo "------------------------------------------------------"
sudo mkdir /etc/asterisk/keys
sudo cd contrib/scripts
sudo ./ast_tls_cert -C $SERVER_NAME -O "Asterisk Fernuni" -d /etc/asterisk/keys


# to clean the config files
sed -e 's/;.*$//' -e '/^$/d' rtp.conf.ori > rtp.conf
