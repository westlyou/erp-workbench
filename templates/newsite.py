%(marker)s
# """
# some nice description of the project
# """
    "%(site_name)s": {
        'site_name': '%(site_name)s',
        'servername': '%(site_name)s',
        'erp_admin_pw': '',
        'erp_version': '%(erp_version)s',
        'erp_minor': '%(erp_minor)s',
        'erp_nightly': '%(erp_nightly)s', # what folder on nightly if not version like 'master'
        # servertype is odoo or flectra
        'erp_type': '%(erp_type)s',
        'db_name': '%(site_name)s',
        # inherits tells from what other site we want to inherit values
        'inherit': '',
        # should we use demodata
        'without_demo': 'all',
        # pg_version to use with dumper
        # 'pg_version' : '--cluster 10/main',
        'remote_server': {
            'remote_url': '%(remote_server)s',  # please adapt
            'remote_data_path': '/root/erp_workbench',
            'remote_user': 'root',
            # where is sites home on the remote server for non root users
            'remote_sites_home': '%(base_sites_home)s',
            'redirect_emil_to': '',  # redirect all outgoing mail to this account
            # needs red_override_email_recipients installed
        },
        'docker': {
            'base_image': '%(docker_hub_name)s/%(site_name)s:%(erp_version)s-latest',
            'erp_image_version': '%(erp_image_version)s:%(erp_version)s',
            'container_name': '%(site_name)s',
            # 'db_container_name'    : 'db', # needs only to be set if it is not 'db'
            # trough what port can we access oddo (mapped to 8069)
            'erp_port': '%(docker_port)s',
            # trough what port can we access the sites long polling port (mapped to 8072)
            'erp_longpoll': '%(docker_long_poll_port)s',
            # within the the container the erp user (odoo or flectra) has a user and group id that
            # is used to access the files in the log and filestore volumes
            'external_user_group_id': '104:107',
            # hub_name is the name to use to store our own images
            'hub_name': 'docker_hub',
            # ODOO_BASE_URL
            # If this variable is set, the `ir.config_parameter` `web.base.url`
            # will be automatically set to this domain when the container
            # starts. `web.base.url.freeze` will be set to `True`.
            'ODOO_BASE_URL': 'https://www.%(site_name)s.ch'
        },
        # docker_hub is used to store images we build ourself
        # by default we use dockers own docker_hub, but could
        # provide our own
        'docker_hub': {
            # 'docker_hub' : {
            #   'user' : 'robertredcor',
            #   'docker_hub_pw' : '',
            # }
        },
        'apache': {
            'vservername': 'www.%(site_name)s.ch',
            # 'vserveraliases': ['%(site_name)s.ch',],
        },
        # erp_addons allow to install base tools
        'erp_addons': [
            # 'website builder',
            # 'crm',
        ],
        'addons': [
            {
                """
                # ***********************************
                # please clean out lines not needed !
                # ***********************************
                ## what type is the repository
                #'type' : 'git',
                ## what is the url to the repository
                #'url' : 'ssh://git@gitlab.redcor.ch:10022/agenda2go/docmarolf_calendar.git',
                ## branch is the repositories branch to be used. default 'master'
                #'branch' : 'branch.xx',
                ## what is the target (subdirectory) within the addons folder
                #'target' : 'docmarolf_calendar',
                ## group what group should be created within the target directory.
                #'group' : 'somegroup',
                ## add_path is added to the addon path
                ## it is needed in the case when group of modules are added under a group
                #'add_path : 'somesubdir',
                ## name is used as name of the addon to install
                #'name' : 'some name',
                ## names is a list of names, when more than one addon should be installed
                ## from a common addon directory
                #'names' : ['list', 'of', 'addons'],
                """
                'type': 'git',
                'url': '',
                'name': '',
                'name': [],
                'target': '',
                'group': '',
                'add_path': '',
                'branch': '',
                'tag': '',
                'pip_list' : [], # what extra python libraries to load
                'apt_list' : [], # what extra apt modules to install into a docker

                # 'addon_name' : '' # this value needs only be set, 
                                    # when the name of the modul is not part of the git url
            },
            {
                # ***********************************
                # type local allows loading
                # a module while developing.
                # the module will not be touched so it
                # should be in anly of the addon folders
                # pointed to by othe site.
                # a good place would be the
                # SITENAME_addons folder created  in
                # every buildout folder created by
                # erp_workbench
                # ***********************************
                'type': 'local',
                'url': '',
                'name': 'my_library',
            },
        ],
        'tags': {
            # ***********************************
            # a dictonary pointing to tags to be
            # used for addons.
            # tags found here have lower precendence
            # the the ones found in the addon section
            # ***********************************
            # 'module_x' : 'vXXX',
        },
        'skip': {
            # the addons to skip when installing
            # the name is looked up in the addon stanza in the following sequence:
            # - name
            # - add_path
            # - group
            'addons': [],
            # skip when it is installed
            'updates': [],
        },
        # extra libraries needed to be installed by pip or apt
        # this is used in two places
        # 1. pip installs are executed when creating a site on the local computer
        #    and executing bin/dosetup [-f] in the sites buildout directory
        # 2. both pip and apt installs are executed when a docker image is created
        'extra_libs': {
            # 'pip' : [
            #   'xmlsec',
            #   'scrapy',
            #   'html2text',
            # ],
            # 'apt' : [
            #   'python-dev',
            #   'pkg-config',
            #   'libxml2-dev',
            #   'libxslt1-dev',
            #   'libxmlsec1-dev',
            #   'libffi-dev',
            # ]
        },
        'develop': {
            'addons': [],
        },
        # slave info: is this site slave of a master site from which it will be updated
        'slave_info': {
            # # master_site ist the name of the mastersite
            # # this must be a site in sites.py
            # "master_site" : '',
            # # master_domain is the domain from which the master is copied
            # "master_domain" : 'localhost',
        }
    },
