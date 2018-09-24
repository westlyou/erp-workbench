Erp-Workbench install
---------------------

    The installation of erp-workbench hast the following major steps:

    1. setup virtualenv wrapper
        This is explained in install/virtualenv_wrapper.txt_
    2. create a virtual env using virtualenv-wrapper
        cd to the folder where erp-workbench is donloaded to
        ececute the following commands::

            mkvirtualenv -a . -p python3 workbench
            (cd bin; ln -s $(which python))
            (cd bin; ln -s $(which pip))
            bin/pip install -r install/requirements.txt
            (cd help; make html)
            (echo $'\n''alias  wb="workon workbench"' >> ~/.bash_aliases)

    After having executed the above commands and opened a new bash terminal
    (you created a new alias that is only active when freshly loaded)

    the command:
        wb

    will activate the workbench environment and cd into its installation folder

.. _install/virtualenv_wrapper.txt: install/install_virtalenv_wrapper.html