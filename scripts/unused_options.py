def parse_args():
    argparse.ArgumentParser.set_default_subparser = set_default_subparser
    usage = "create_system.py is a tool to create and maintain local odoo developement environment\n" \
    "**************************\n" \
    "updating the local environment:\n" \
    "update_local_db.py udates the local postgres database. \nEither in a local docker container or on localhost\n\n" + \
    "First the remote data is read by running a temporary docker container on the remote site\n" \
    "that dumps the remote database into the sites dump directory\n" \
    "then this directory together with the sites data directory is copied to local host using rsync\n\n" \
    "**************************\n" \
    "the following files are read:\n" \
    "sites_list/sites_global: This folder contains a set of site descriptions\n" \
    "sites_list/sites_local:  This folder contains local site descriptions not managed by git\n" \
    "localdata.py: It contains the name and password of the local postgres user. not managed by git\n" \
    "**************************\n" \
    "\n-h for help on usage"
    parent_parser = argparse.ArgumentParser(usage=usage, add_help=False)
    parser_rpc = ArgumentParser(add_help=False)
    parser = ArgumentParser(add_help=False)# ArgumentParser(usage=usage)
    parser.add_argument('--help', action=_HelpAction, help='help for help if you need some help')  # add custom help
    parser_s = parser.add_subparsers(title='subcommands', dest="subparser_name")
    #parser_site   = parser_s.add_parser('s', help='the option -s --site-description has the following subcommands', parents=[parent_parser])

    # -----------------------------------------------
    # manage rpc stuff
    # -----------------------------------------------
    #parser_remote_s = parser_remote.add_subparsers(title='remote commands', dest="rpc_commands")
    parser_rpc.add_argument("-SL", "--set-local-data",
                            action="store_true", dest="set_local_data", default=False,
                            help="set local data from the site description. Together with -F it can also be used remotely")
    parser_rpc.add_argument("-SOS", "--set-odoo-settings",
                            action="store_true", dest="set_odoo_settings", default=False,
                            help="set odoo settings like the mail handlers. The script tries to define for what ip")
    parser_rpc.add_argument("-SOSL", "--set-odoo-settings-local",
                            action="store_true", dest="set_odoo_settings_local", default=False,
                            help="set odoo settings like the mail handlers. The script tries to define for what ip")
    parser_rpc.add_argument("-FL", "--force-local-data",
                            action="store_true", dest="force_local_data", default=False,
                            help="force setting local data from the site description, even when we are on a remote site")
    parser_rpc.add_argument("-E", "--execute-script",
                            action="store", dest="executescript",
                            help="Run a script against a running odoo site. Name must be given")
    parser_rpc.add_argument("-EP", "--execute-script-parameter",
                            action="store", dest="executescriptparameter",
                            help="parameters to be passed to the executed script. It must be a comma separated string of key=value pairs. No spaces!")
    #parser_rpc.add_argument("-dbp", "--dbport",
                    #action="store", dest="dbport", default=5432,
                    #help="define db port default 5432")
    # -----------------------------------------------
    # manage sites create and update sites
    # -----------------------------------------------
    #http://stackoverflow.com/questions/10448200/how-to-parse-multiple-sub-commands-using-python-argparse
    #parser_site_s = parser_site.add_subparsers(title='manage sites', dest="site_creation_commands")
    parser_manage = parser_s.add_parser(
        'create',
        help='create is used to manage local and remote sites',
        parents=[parser_rpc, parent_parser],
        prog='PROG',
        usage='%(prog)s [options]')
    parser_manage.add_argument(
        "-cdb", "--create-db-demo",
        action="store_true", dest="create_db_demo", default=False,
        help = 'create new database with demo data. Name must be provided',
    )
    parser_manage.add_argument(
        "-capw", "--copy-admin-pw",
        action="store", dest="copy_admin_pw",
        help = 'Copy admin pw from source site. option -n must be set and valid. It is the TARGET site.',
    )
    parser_manage.add_argument(
        "-sapw", "--set-admin-pw",
        action="store_true", dest="set_admin_pw", default = False,
        help = 'Set admin password from site description. option -n must be set and valid.',
    )
    parser_manage.add_argument(
        "-uiss", "--update-install-serversettings",
        action="store_true", dest="update_install_serversetting", default=False,
        help = 'update serversettings like base url or recaptcha keys'
    )
    parser_manage.add_argument(
        "--add-addon",
        action="store", dest="add_addon",
        help = 'add addon to server-description. pass a comma separated list of addon-infos' \
        'of the form url:name;name2;nameX'
    )
    parser_manage.add_argument(
        "-lm", "--listmodules",
        action="store_true", dest="listmodules", default=False,
        help = 'list installable odoo module sets like CRM ..'
    )
    # temporarily handle preset
    parser_manage.add_argument(
        "-PR", "--use_preset",
        action="store", dest="use_preset",
        help = """
        Use preset. This is a temporary solution till preset works
        """
    )
    # -----------------------------------------------
    # support commands
    # -----------------------------------------------
    #parser_manage_s = parser_manage.add_subparsers(title='manage sites', dest="site_manage_commands")
    parser_support= parser_s.add_parser('support', help='the option -sites --support has the following subcommands', parents=[parent_parser])
    # -----------------------------------------------
    # manage docker
    # -----------------------------------------------
    #parser_support_s = parser_support.add_subparsers(title='docker commands', dest="docker_commands")
    parser_docker = parser_s.add_parser(
        'docker',
        help='the option --docker has the following subcommands',
        parents=[parent_parser])
    parser_docker.add_argument(
        "-dassh", "--docker-add_ssh",
        action="store_true", dest="docker_add_ssh", default=False,
        help = 'add ssh to a docker container'
    )
    parser_docker.add_argument(
        "-duiss",
        action="store_true", dest="update_install_serversetting", default=False,
        help = 'update serversettings like base url or recaptcha keys'
    )
    parser_docker.add_argument(
        "-dsssh", "--docker-start_ssh",
        action="store_true", dest="docker_start_ssh", default=False,
        help = 'start ssh in a running docker container'
    )
    parser_docker.add_argument(
        "-dc", "--create_container",
        action="store_true", dest="docker_create_container", default=False,
        help = 'create a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dcu", "--create_update_container",
        action="store_true", dest="docker_create_update_container", default=False,
        help = 'create a docker container that runs the etc/runodoo.sh script at startup. Name must be provided'
    )
    parser_docker.add_argument(
        "-dE", "--execute-script",
        action="store", dest="executescript",
        help="Run a script against a running odoo site. Name must be given")
    parser_docker.add_argument(
        "-dEP", "--execute-script-parameter",
        action="store", dest="executescriptparameter",
        help="parameters to be passed to the executed script. It must be a comma separated string of key=value pairs. No spaces!")    
    parser_docker.add_argument(
        "-dSL", "--set-local-data-docker",
        action="store_true", dest="set_local_data_docker", default=False,
        help="force setting local data from the site description, even when we are on a remote site")
    parser_docker.add_argument(
        "-dSOS", "--set-odoo-settings-docker",
        action="store_true", dest="set_odoo_settings_docker", default=False,
        help="set odoo settings like the mail handlers. The script tries to define for what ip")
    parser_docker.add_argument(
        "-dbi", "--build_image",
        action="store_true", dest="docker_build_image", default=False,
        help = 'create a docker image. Name must be provided'
    )
    parser_docker.add_argument(
        "-dbis", "--build_image_use_sites",
        action="store", dest="use_sites",
        help = 'use sites to collect libraries to build image'
    )
    parser_docker.add_argument(
        "-dbiC", "--build_image_collect_sites",
        action="store_true", dest="use_collect_sites",
        help = 'collect all libraries from sites with same version'
    )
    parser_docker.add_argument(
        "-dpi", "--push_image",
        action="store_true", dest="docker_push_image", default=False,
        help = 'push a docker image. Name of site must be provided'
    )
    parser_docker.add_argument(
        "-dcapw", "--docker-copy-admin-pw",
        action="store", dest="docker_copy_admin_pw",
        help = 'Copy admin pw from source site in docker conatiners. option -n must be set and valid. It is the TARGET site.',
    )
    parser_docker.add_argument(
        "-dsapw", "--docker-set-admin-pw",
        action="store_true", dest="docker_set_admin_pw", default = False,
        help = 'Set admin password from site description in a docker conatiner. option -n must be set and valid.',
    )
    parser_docker.add_argument(
        "-dr", "--recreate-container",
        action="store_true", dest="docker_recreate_container", default=False,
        help = 'rename and recreate docker container. Name must be provided,'
    )
    parser_docker.add_argument(
        "-dp", "--docker-pull-image",
        action="store_true", dest="docker_pull_image", default=False,
        help = 'pull actual image used by a docker container. Name must be provided,'
    )
    parser_docker.add_argument(
        "-dcdb", "--create_db_container",
        action="store_true", dest="docker_create_db_container", default=False,
        help = 'create a docker databse container. It will be named db.  You must also set option -dcdbPG to set postgres version'
    )
    parser_docker.add_argument(
        "-dcdbPG", "--set-postgers-version",
        action="store", dest="set_postgers_version",
        help = 'define postgres version to be used. Something like 9.6 or 10.0'
    )
    parser_docker.add_argument(
        "-ds", "--start_container",
        action="store_true", dest="docker_start_container", default=False,
        help = 'start a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dshow",
        action="store_true", dest="docker_show", default=False,
        help = 'show some info about a container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dshowa",
        action="store_true", dest="docker_show_all", default=False,
        help = 'show all info about a container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dS", "--stop_container",
        action="store_true", dest="docker_stop_container", default=False,
        help = 'stop a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-drs", "--restart_container",
        action="store_true", dest="docker_restart_container", default=False,
        help = 'restart a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-ddbname", "--dockerdbname",
        action="store", dest="dockerdbname", # no default, otherwise we can not get it from the site description
        help="user to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerdb_container_name'])

    parser_docker.add_argument(
        "-ddbuser", "--dockerdbuser",
        action="store", dest="dockerdbuser", # no default, otherwise we can not get it from the site description
        help="user to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerdbuser'])

    parser_docker.add_argument(
        "-ddbpw",
        action="store", dest="dockerdbpw", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerdbpw'])

    parser_docker.add_argument(
        "-drpcuser",
        action="store", dest="drpcuser", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerrpcuser'])

    parser_docker.add_argument(
        "-drpcuserpw",
        action="store", dest="drpcuserpw", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites odoo stanza, default %s" % DOCKER_DEFAULTS['dockerrpcuserpw'])

    parser_docker.add_argument(
        "-ddpo", "--dockerdbport",
        action="store", dest="dockerdbport", default='',
        help="port on which to access database in the db container\nnormally taken from config")

    #parser_docker.add_argument(
        #"-dtd", "--transferdocker",
        #action="store_true", dest="transferdocker", default=False,
        #help = 'transfer data from master to slave using docker'
    #)
    parser_docker.add_argument(
        "-dud", "--dataupdate_docker",
        action="store_true", dest="dataupdate_docker", default=False,
        help = 'update local data from remote server into local docker. Name must be provided.\nRespects -N and -nupdb options'
    )
    parser_docker.add_argument(
        "-ddump", "--dump-local-docker",
        action="store_true", dest="dump_local_docker", default=False,
        help = 'dump database data into the servers dump folder. does use docker'
    )
    parser_docker.add_argument(
        "-dio", "--dinstallown",
        action="store_true", dest="dinstallown", default=False,
        help = 'install all modules listed as addons. Name must be provided'
    )
    parser_docker.add_argument(
        "-duo", "--dupdateown",
        action="store", dest="dupdateown", default='',
        help = 'update modules listed as addons, pass a comma separated list (no spaces) or all. Name must be provided'
    )
    parser_docker.add_argument(
        "-dro", "--dremoveown",
        action="store", dest="dremoveown", default='',
        help = 'remove modules listed as addons, pass a comma separated list (no spaces) or all. Name must be provided'
    )

    # !!! local_docker is added to parent_parser, not parser_docker
    parent_parser.add_argument(
        "-L", "--local-docker",
        action="store_true", dest="local_docker", default=False,
        help = 'allways use a docker running locally as source when updating local data'
    )
    parser_docker.add_argument(
        "-shell", "--shell",
        action="store", dest="shell", default=False,
        help = 'open a shell in a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-dip", "--use-ip-docker",
        action="store", dest="use_ip_docker",
        help = 'docker: use the ip provided instead of the one found in the site description'
    )

    # -----------------------------------------------
    # manage remote server (can be localhost)
    # -----------------------------------------------
    #parser_docker_s = parser_docker.add_subparsers(title='remote commands', dest="remote_commands")
    parser_remote = parser_s.add_parser(
        'remote',
        help='the command remote is used to manage the remote server.',
        parents=[parent_parser])
    parser_remote.add_argument(
        "--add-apache",
        action="store_true", dest="add_apache", default=False,
        help = 'add apache.conf to the apache configuration. Name must be provided'
    )
    parser_remote.add_argument(
        "--add-nginx",
        action="store_true", dest="add_nginx", default=False,
        help = 'add configuration to the list of nginx configurations. Name must be provided'
    )
    parser_remote.add_argument(
        "-cert", "--create-certificate",
        action="store", dest="create_certificate",
        help = 'create or update lets encrypt ssl certificate. Name must be provided'
    )
    # -----------------------------------------------
    # manage mails
    # -----------------------------------------------
    parser_mail = parser_s.add_parser(
        'mail',
        help='the command mail is used to manage mails.',
        parents=[parent_parser])

    parser_mail.add_argument(
        "-mm", "--manage_mail",
        action="store_true", dest="manage_mail", default=False,
        help = 'manage mail seting. Name must be provided'
    )
    parser_mail.add_argument(
        "-myh", "--mysql_host",
        action="store", dest="mysql_host", default='localhost',
        help = 'host on which mysql server with mail settings. Default localhost'
    )
    parser_mail.add_argument(
        "-myP", "--mysql_port",
        action="store", dest="mysql_port", default=3306,
        help = 'mysql port. Default 3306'
    )
    parser_mail.add_argument(
        "-myu", "--mysql_user",
        action="store", dest="mysql_user", default='froxlor',
        help = 'mysql user. Default froxlor'
    )
    parser_mail.add_argument(
        "-myp", "--mysql_password",
        action="store", dest="mysql_password",
        help = 'mysql_password'
    )
    parser_mail.add_argument(
        "-myd", "--mysql_db",
        action="store", dest="mysql_db", default='froxlor',
        help = 'mysql database with emails. Default froxlor'
    )
    parser.set_default_subparser('create')
    args, unknownargs = parser.parse_known_args()
    return args
    command_line = ' '.join(sys.argv)
    
    opts = OptsWrapper(args)
    opts.command_line = command_line # so we can reexecute
    if not opts.name and unknownargs:
        unknownargs = [a for a in unknownargs if a and a[0] != '-']
        if unknownargs:
            opts._o.__dict__['name'] = unknownargs[0]
