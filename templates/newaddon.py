            {
                # ***********************************
                # please clean out lines not needed !
                # ***********************************
                # what type is the repository
                # possible values are 'git, 'local'
                'type' : '%(type)s',
                # what is the url to the repository
                'url' : 's(url)s',
                # branch is the repositories branch to be used. default 'master'
                'branch' : '%(branch)s',
                # what is the target (subdirectory) within the addons folder
                'target' : '%(target)s',
                # group what group should be created within the target directory.
                # see http://docs.anybox.fr/anybox.recipe.odoo/1.9.1/configuration.html#addons
                'group' : '%(group)s',
                # add_path is added to the addon path
                # it is needed in the case when group of modules are added under a group
                'add_path' : '%(addpath)s',
                # name is used as name of the addon to install
                'name' : '%(name)s',
                # names is a list of names, when more than one addon should be installed
                # from a common addon directory
                'names' : [%(names)s],
            },
