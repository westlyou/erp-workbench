#!/usr/bin/python
# -*- encoding: utf-8 -*-

# for flectra we merge FILES_TO_COPY_FLECTRA into FILES_TO_COPY

FILES_TO_COPY = {
    # F = File
    # O = File, allways overwrite
    # X = File set executable bit, allways overwrite
    # L = Link
    # D = Folder
    # R = copy and rename (sourcename, targetname)
    # T = Touch
    # U = Update, these files can have updatable content in the form of %(XXX)s
    # '$FILE$' link to the source
    'project' : {
        #'alias.py'          : 'F',
        'base_recipe.cfg'   : 'O',
        'bin'               : {
            # we want to link to the original dosetup.py so we can update it
            #'dosetup.py' : ('L','$FILE$'),
            'dosetup.py' : ('U', 'X'),
            # python and pip are created whe running dosetup
            # we just want to link to them to be able to access them more easyily
            'pip' : ('L', '../python/bin/pip'),
            'python' : ('L', '../python/bin/python'),
            # we want to link to the original update_local_db.py so we can update it
            #'update_local_db.py' : ('L','$FILE$'),
            #'update_local_db.py' : 'X',
            'odoorunner.py' : ('U','X'),
            '__init__.py' : 'T',
        },
        'etc' : {
            'runodoo.sh' : ('O', 'X'),
        },
        'bootstrap.py'      : 'O',
        'buildout.cfg'      : 'O',
        'install'           : {
            'requirements.txt' : 'U',
        },
        'login_info.cfg.in' : 'O',
        'scripts'           : {
            'dodump.sh' : 'F',
            '__init__.py' : 'F',
            'README.txt' : 'F',
            'updatedb.sh' : 'F',
            # we want to link to the original update_local_db.py so we can update it
            #'update_local_db.py'  : ('L','$FILE$'),
            'update_local_db.py'  : 'F',
        },
        'Dockerfile' : 'F',
    },
    'project_home' : {
        'documents' : 'D',
        'README.txt' : 'T',
        #'Python.gitignore' : ('R', '.gitignore')
    },
    'simple_copy' : {
        'base_recipe.cfg'   : ('U', 'X'),
        'login_info.cfg.in' : 'O',
        #'Python.gitignore' : ('R', '.gitignore'),
        'bin'               : {
            'dosetup.py' : ('U', 'X'),
            'update_local_db.py' : 'X',
            'odoorunner.py' : 'X',
            '__init__.py' : 'T',
        },
    }

}
FILES_TO_COPY_FOLDER = {
    # F = File
    # O = File, allways overwrite
    # X = File set executable bit, allways overwrite
    # L = Link
    # D = Folder
    # R = copy and rename (sourcename, targetname)
    # T = Touch
    # U = Update, these files can have updatable content in the form of %(XXX)s
    # '$FILE$' link to the source
    'etc' : {
        'runodoo.sh' : ('U', 'X'),
    },
}

# FILES_TO_COPY_ODOO is used in the case, that we run odoo using workon
FILES_TO_COPY_ODOO = {
    'project' : {
        'bin' : {
            # we want to link to the original dosetup.py so we can update it
            #'dosetup.py' : ('L','$FILE$'),
            'dosetup_odoo.py' : ('U','X'),
            'build_odoo.py' : ('U', 'X'),
            'create_db.py' : ('U', 'X'),
            'odoo' : ('U', 'X'),
            'erp_runner.py' : ('U', 'X'),
            '__init__.py' : 'T',
        },
        'install'           : {
            'requirements.txt' : 'U',
        },
        'login_info.cfg.in' : 'O',
    },
}

FILES_TO_COPY_FLECTRA = {
    'project' : {
        'bin' : {
            # we want to link to the original dosetup.py so we can update it
            #'dosetup.py' : ('L','$FILE$'),
            'flectra' : ('U', 'X'),
            'dosetup_flectra.py' : ('U','X'),
            'build_flectra.sh' : ('U', 'X'),
            'flectra-bin' : ('L', '../flectra/flectra-bin'),
            '__init__.py' : 'T',
        },
        'install'           : {
            'requirements.txt' : 'U',
        },
        'login_info.cfg.in' : 'O',
    },
}
