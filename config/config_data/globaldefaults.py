DOCKER_DEFAULTS = {
    # the name of the container in which the database is created
    'dockerdb_container_name' : 'db',
    # dockerdbuser is used to access the database  in the database container
    'dockerdbuser'      : 'odoo',
    # dockerdbpw is the dockerdbuser's password
    'dockerdbpw'        : 'odoo',
    # dockerrpcuser is the user with which we want to login to the odoo site running in the container
    'dockerrpcuser'     : 'admin',
    # dockerrpcuserpw dockerrpcuser's password
    # this is in most cases NOT 'admin'
    # you can overrule it with -ddbpw
    'dockerrpcuserpw'   : 'admin',
    'odoo_version' : '12.0',
}
