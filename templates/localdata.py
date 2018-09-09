# db_user is used to access the local postgres server
import getpass
DB_USER = getpass.getuser()
# db_password ist used to login db_userdb_user
DB_PASSWORD = 'odoo' # for docker
DB_PASSWORD_LOCAL = 'admin' # when used whitout docker
# apache_pathis used to create virtual sites
APACHE_PATH = '/etc/apache2'
# remote_user_dic is used to access the remote server to update the local db
# it is a dic with the ip of the remote server as key
# which ip to use is read from sytes.py

REMOTE_USER_DIC = {
# do not remove the marker!    
# ---------------- marker ----------------    
    '144.76.184.20' : { # frieda
        'remote_user' : 'root',
        ## the remote data path is used to overule the remot_data_path defined
        ## in the sites descrition
        'remote_data_path' : '/root/erp_workbench',
        ## remote_pw is used as credential for the remote user. normaly unset
        ## to use public keys.
        'remote_pw' : '',
    },
    # as non root user on elsbeth
    #'82.220.39.73' : { # elsbeth
    #    'remote_user' : 'odooprojects',
    #    'remote_data_path' : '/home/odooprojects/erp_workbench',
    #    # remote_pw is used as credential for the remote user. normaly unset
    #    # to use public keys.
    #    'remote_pw' : '',
    #},
    '82.220.39.73' : { # elsbeth
        'remote_user' : 'root',
        ## the remote data path is used to overule the remote_data_path defined
        ## in the sites descrition
        'remote_data_path' : '/root/erp_workbench',
        ## remote_pw is used as credential for the remote user. normaly unset
        ## to use public keys.
        'remote_pw' : '',
    },
    '46.4.89.241' : { # salome
        'remote_user' : 'root',
        # the remote data path is used to overule the remot_data_path defined
        ## the remote data path is used to overule the remote_data_path defined
        ## in the sites descrition
        'remote_data_path' : '/root/erp_workbench',
        ## remote_pw is used as credential for the remote user. normaly unset
        ## to use public keys.

        'remote_pw' : '',
    },
    'localhost' : {
        'remote_user' : DB_USER,
        'remote_data_path' : '/home/%s/erp_workbench' % DB_USER,
        # remote_pw is used as credential for the remote user. normaly unset
        # to use public keys.
        'remote_pw' : '',
        'local_user_email' : 'user_to_use@please set in local data',
    },
}
