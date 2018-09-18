    # all options that are added to the parent parser
# the parent parser gets incloded in some other also
# and provides common options

from config import BASE_PATH, BASE_INFO, DOCKER_DEFAULTS
from utilities.parser_handler import ParserHandler

def add_options_docker(parser, result_dic):
    """add options to the create parser
    
    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parser_docker = ParserHandler(parser, result_dic)

    
    # -----------------------------------------------
    # manage docker
    # -----------------------------------------------
    #parser_support_s = parser_support.add_subparsers(title='docker commands', dest="docker_commands")
    parser_docker.add_argument(
        "-dc", "--create_container",
        action="store_true", dest="docker_create_container", default=False,
        help = 'create a docker container. Name must be provided',
        need_name = True,
        name_valid = True,
    )
    parser_docker.add_argument(
        "-dE", "--execute-script",
        action="store", dest="executescript",
        help="Run a script against a running odoo site. Name must be given",
        need_name = True,
        name_valid = True,      
    )
    parser_docker.add_argument(
        "-dEP", "--execute-script-parameter",
        action="store", dest="executescriptparameter",
        help="parameters to be passed to the executed script. It must be a comma separated string of key=value pairs. No spaces!")    
    parser_docker.add_argument(
        "-dSOS", "--set-odoo-settings-docker",
        action="store_true", dest="set_odoo_settings_docker", default=False,
        help="set odoo settings like the mail handlers. The script tries to define for what ip",
        need_name = True,
        name_valid = True,       
    )
    parser_docker.add_argument(
        "-dbi", "--build_image",
        action="store_true", dest="docker_build_image", default=False,
        help = 'create a docker image. Name must be provided',
        need_name = True,
        name_valid = True,        
    )
    parser_docker.add_argument(
        "-dbis", "--build_image_use_sites",
        action="store", dest="use_sites",
        help = 'use sites to collect libraries to build image',
        need_name = True
    )
    parser_docker.add_argument(
        "-dbiC", "--build_image_collect_sites",
        action="store_true", dest="use_collect_sites",
        help = 'collect all libraries from sites with same version'
    )
    #parser_docker.add_argument(
        #"-dsapw", "--docker-set-admin-pw",
        #action="store_true", dest="docker_set_admin_pw", default = False,
        #help = 'Set admin password from site description in a docker conatiner. option -n must be set and valid.',
    #)
    parser_docker.add_argument(
        "-dcdb", "--create_db_container",
        action="store_true", dest="docker_create_db_container", default=False,
        help = 'create a docker database container. It will be named db.  You must also set option -dcdbPG to set postgres version'
    )
    parser_docker.add_argument(
        "-dcdbPG", "--set-postgers-version",
        action="store", dest="set_postgers_version",
        help = 'define postgres version to be used. Something like 9.6 or 10.0'
    )
    #parser_docker.add_argument(
        #"-ds", "--start_container",
        #action="store_true", dest="docker_start_container", default=False,
        #help = 'start a docker container. Name must be provided',
        #need_name = True
    #)
    parser_docker.add_argument(
        "-dshow",
        action="store_true", dest="docker_show", default=False,
        help = 'show some info about a container. Name must be provided',
        need_name = True,
        name_valid = True,
    )
    parser_docker.add_argument(
        "-dshowa",
        action="store_true", dest="docker_show_all", default=False,
        help = 'show all info about a container. Name must be provided',
        need_name = True,
        name_valid = True,
    )
    #parser_docker.add_argument(
        #"-dS", "--stop_container",
        #action="store_true", dest="docker_stop_container", default=False,
        #help = 'stop a docker container. Name must be provided',
        #need_name = True
    #)
    #parser_docker.add_argument(
        #"-drs", "--restart_container",
        #action="store_true", dest="docker_restart_container", default=False,
        #help = 'restart a docker container. Name must be provided'
    #)
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
        "-dud", "--dataupdate_docker",
        action="store_true", dest="dataupdate_docker", default=False,
        help = 'update local data from remote server into local docker. Name must be provided.\nRespects -N and -nupdb options',
        need_name = True
    )
    parser_docker.add_argument(
        "-ddump", "--dump-local-docker",
        action="store_true", dest="dump_local_docker", default=False,
        help = 'dump database data into the servers dump folder. does use docker',
        need_name = True
    )
    parser_docker.add_argument(
        "-dio", "--dinstallown",
        action="store_true", dest="dinstallown", default=False,
        help = 'install all modules listed as addons. Name must be provided',
        need_name = True
    )
    parser_docker.add_argument(
        "-duo", "--dupdateown",
        action="store", dest="dupdateown", default='',
        help = 'update modules listed as addons, pass a comma separated list (no spaces) or all. Name must be provided',
        need_name = True
    )
    parser_docker.add_argument(
        "-dro", "--dremoveown",
        action="store", dest="dremoveown", default='',
        help = 'remove modules listed as addons, pass a comma separated list (no spaces) or all. Name must be provided',
        need_name = True
    )
    parser_docker.add_argument(
        "-dI", "--dinstallodoomodules",
        action="store_true", dest="dinstallodoomodules", default=False,
        help = 'install modules listed as odoo addons into docker. Name must be provided',
        need_name = True
    )
    #parser_docker.add_argument(
        #"-dassh", "--docker-add_ssh",
        #action="store_true", dest="docker_add_ssh", default=False,
        #help = 'add ssh to a docker container'
    #)    
