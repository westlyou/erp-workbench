%(marker)s

    '%(use_ip)s' : { # ADDED bin/c support --add-server
        # if you want to have non root access to site dat you have to set the values
        # like so:
        #    'remote_user' : 'odooprojects',
        #    'remote_data_path' : '/home/odooprojects/odoo_instances',
        # then we have to allow access by adding the following two lines
        # to the sudoerrs file using visudo
        # odooprojects ALL = NOPASSWD: /usr/bin/docker
        # odooprojects ALL = NOPASSWD: /root/odoo_instances/scripts/site_syncer.py
        'remote_user' : '%(remote_user)s',
        'remote_data_path' : '%(remote_data_path)s',
        # remote_pw is used as credential for the remote user. normaly unset
        # to use public keys.
        'remote_pw' : '',
    },
