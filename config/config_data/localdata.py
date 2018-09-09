# db_user is used to access the local postgres server
import getpass
from config import BASE_PATH, DB_PASSWORD
DB_USER = getpass.getuser()
# db_password ist used to login db_userdb_user
DB_PASSWORD = 'odoo' # for docker
DB_PASSWORD_LOCAL = 'admin' # when used whitout docker
# apache_pathis used to create virtual sites
APACHE_PATH = '/etc/apache2'
NGINX_PATH = '/etc/nginx/'
# remote_user_dic is used to access the remote server to update the local db
# it is a dic with the ip of the remote server as key
# which ip to use is read from sytes.py

REMOTE_USER_DIC = {
    'localhost' : {
        'remote_user' : DB_USER,
        'remote_data_path' : BASE_PATH, 
        # remote_pw is used as credential for the remote user. normaly unset
        # to use public keys.
        'remote_pw' : '',
        'local_user_email' : 'user_to_use@please set in local data',
    },
}

