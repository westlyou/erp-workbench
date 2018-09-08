%(marker)s
# """
# some nice description of the project
# """
    "%(site_name)s": {
        'site_name': '%(site_name)s',
        'servername': '%(site_name)s',
        'odoo_admin_pw': '',
        'odoo_version': '%(odoo_version)s',
        'odoo_minor': '.0',
        'odoo_nightly': '', # what folder on nightly if not version like 'master'
        # servertype is odoo or flectra
        'server_type': 'odoo',
        'db_name': '%(site_name)s',
        # inherits tells from what other site we want to inherit values
        'inherit': '',
        # should we use demodata
        'without_demo': 'all',
        # pg_version to use with dumper
        # 'pg_version' : '--cluster 10/main',
        'site_settings': {
            # proto is either http:// or https://
            # it is used to construct the  web.base.url
            # if not set, the base url will be left untouched
            'proto': 'http://',
            'configs': {
                'website_config': {
                    'model': "website.config.settings",
                    'website_name': 'Your Sitename',
                    # needs recaptcha installed
                    # 'site_key' : 'xx',
                    # 'secret_key' : 'x',
                },
                # the following sample values assume, that the module support branding is installed
                'support_branding': {
                    'model': 'ir.config_parameter',
                    'config_parameter_company_name': 'Your company',
                    'config_parameter_company_url': 'https://yourwebsite.com',
                    'config_parameter_company_color': '#000',
                    'config_parameter_support_email': 'support@yourwebsite.com',
                    'config_parameter_release': 42,
                },
            },
            'server_config': {
                # override values to be set in the server config file
                # the defaul values that can be manipulated from this stanza are set
                # in templates/openerp_cfg_defaults.py
                #    'workers' : 4,
            },
            'site_settings': {
                # data to bes set on the remote server with
                # --set-site-data
                'company_data': {
                    # use any number of fields you want to set on the main company
                    # this is normaly done after after all modules are installed
                    # so you can also use fields like firstname/lastname that are
                    # only available after the addons have been installed
                    'name': 'acme & co',
                    'street': 'the street 007',
                    'zip': '12345',
                    'city': 'The City',
                    'phone': 'the phone number',
                },
                'users': {
                    # add users you want to be created
                    # for each user provide either an string with the email,
                    # or a dictionary with more data. In any case, the email must
                    # be provided
                    # the same rules as for the company apply
                    'testuser': 'test_user@%(base_url)s',
                    'otheruser': {
                        'email': 'otheruser%(base_url)s',
                        'city': 'otherusers city',
                        # ...
                    },
                },
                # what languaes to load, the first one will be the default language
                # unless the language is an empty string
                'languages': [],  # ['de_CH', 'fr_CH']
            },
            'local_settings': {
                # these are values that are set, when we run bin/c with the
                # -SL --set-local-data option
                # candiates to set are:
                # admin emai (pw is allready set to 'admin')
                # base url ..
                'base_url': 'http://localhost:8069',
                'admin_mail': '%(local_user_mail)s',
                'addons': {
                    'install': [],
                    # unistall is not yet implemented
                    'uninstall': []
                },
                'site_settings': {
                    'configs': {
                        'ir.config_parameter': {
                            'records': [
                                # list of (search-key-name, value), {'field' : value, 'field' : value ..}
                                [('key', 'support_branding.company_name'),
                                 {'value': 'redO2oo KLG'}],
                            ],
                        },
                    },
                },
            },
        },
        'email_settings': {
            'smtp_server': '',
            'email_server_incomming': '',
            'email_user_incomming': '',
            'email_pw_incomming': '',
            'email_userver_outgoing': '',
            'email_user_outgoing': '',
            'email_pw_outgoing': '',
        },
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
            'base_image': 'robertredcor/%(site_name)s:%(odoo_version)s-latest',
            'odoo_image_version': 'odoo:%(odoo_version)s',
            'container_name': '%(site_name)s',
            # 'db_container_name'    : 'db', # needs only to be set if it is not 'db'
            # trough what port can we access oddo (mapped to 8069)
            'odoo_port': '%(docker_port)s',
            # trough what port can we access odoos long polling port (mapped to 8072)
            'odoo_longpoll': '%(docker_long_poll_port)s',
            # within the the container the user odoo has a user and group id that
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
        # path to the letsencrypt structure
        'letsencrypt': {
            'path': '/etc/letsencrypt/live/'
        },
        # odoo_addons allow to install odoo base tools
        'odoo_addons': [
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
                ## see http://docs.anybox.fr/anybox.recipe.odoo/1.9.1/configuration.html#addons
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
                # should be in anly of the folders
                # pointed to by odoo.
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
