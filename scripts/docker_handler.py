#!bin/python
# -*- encoding: utf-8 -*-

#https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04
from docker import Client
from config import SITES, BASE_INFO, GLOBALDEFAULTS, ODOO_VERSIONS, APT_COMMAND, PIP_COMMAND #,DOCKER_FILES
#from config.handlers import InitHandler, DBUpdater
from create_handler import InitHandler
from update_local_db import DBUpdater
import os
import re
import sys
import shutil
from utilities import get_remote_server_info, bcolors
from scripts.messages import *
import docker
import datetime
from datetime import date

class DockerHandler(InitHandler, DBUpdater):
    master = '' # possible master site from which to copy
    def __init__(self, opts, sites=SITES, url='unix://var/run/docker.sock', use_tunnel=False):
        """
        """
        self.docker_db_admin_pw = GLOBALDEFAULTS['dockerdbpw']
        self.docker_db_admin = GLOBALDEFAULTS['dockerdbuser']
        super(DockerHandler, self).__init__(opts, sites)
        try:
            from docker import Client
        except ImportError:
            print '*' * 80
            print 'could not import docker'
            print 'please run bin/pip install -r install/requirements.txt'
            return
        cli = self.default_values.get('docker_client')
        self.url = url
        if not cli:
            from docker import Client
            cli = Client(base_url=self.url)
            self.default_values['docker_client'] = cli

        if not self.site:
            return # when we are creating the db container
        # ----------------------
        # get the db container
        # ----------------------
        # the name of the database container is by default db
        docker_info = self.site['docker']
        self.docker_db_admin_pw = docker_info.get('db_admin_pw', GLOBALDEFAULTS['dockerdbpw'])
        if not self.opts.dockerdbname:
            db_container_name = docker_info.get('db_container_name', GLOBALDEFAULTS['dockerdb_container_name'])
        self.db_container_name = db_container_name
        
        # update the docker registry so we get info about the db_container_name 
        self.update_container_info()

        # get the dbcontainer
        db_container_list = cli.containers(filters = {'name' : db_container_name})
        if db_container_list:
            db_container = db_container_list[0]
        else:
            return # either db container was missing or some other problem
        # the ip address to access the db container
        self.docker_db_ip = db_container[u'NetworkSettings'][u'Networks']['bridge']['IPAddress']
        # the db container allows access to the postgres server running within
        # trough a port that has been defined when the container has been created
        self.postgres_port = BASE_INFO.get('docker_postgres_port')
        # todo should we check whether the postgres port is accessible??
        
        # ----------------------
        # get the sites container
        # ----------------------
        container_name = docker_info['container_name']
        self.docker_rpc_port = docker_info['odoo_port']
        long_polling_port = docker_info.get('odoo_longpoll')
        if not long_polling_port:
            long_polling_port = int(self.docker_rpc_port) + 10000
        self.docker_long_polling_port = long_polling_port
        self.registry = self.default_values['docker_registry'].get(container_name)
        try:
            self.docker_rpc_host = self.registry['NetworkSettings']['IPAddress']
        except:
            self.docker_rpc_host = 'localhost'
        
        # --------------------------------------------------
        # get the credential to log into the db container
        # --------------------------------------------------
        # by default the odoo docker user db is 'odoo'
        self.docker_db_admin = docker_info.get('db_admin', 'odoo')
        if self.opts.dockerdbuser:
            self.docker_db_admin = self.opts.dockerdbuser or GLOBALDEFAULTS['dockerdbuser']        
        # by default the odoo docker db user's pw is 'odoo'
        #self.docker_db_admin_pw = GLOBALDEFAULTS['dockerdbpw']
        if self.opts.dockerdbpw:
            self.docker_db_admin_pw = self.opts.dockerdbpw or GLOBALDEFAULTS['dockerdbpw']  
          
        # --------------------------------------------------
        # get the credential to log into the sites container
        # --------------------------------------------------
        docker_rpc_user = self.opts.drpcuser
        if not docker_rpc_user:
            docker_rpc_user = GLOBALDEFAULTS['dockerrpcuser']
        self.docker_rpc_user = docker_rpc_user
        
        docker_rpc_user_pw = self.opts.drpcuserpw
        if not docker_rpc_user_pw:
            # no password was provided by an option
            # we try whether we can learn it from the site itself
            docker_rpc_user_pw = self.site.get('odoo_admin_pw')
            if not docker_rpc_user_pw:
                docker_rpc_user_pw = GLOBALDEFAULTS['dockerrpcuserpw']
        self.docker_rpc_user_pw = docker_rpc_user_pw
        
        #dbhost = self.db_host 
        #info = {
            #'rpchost' : 'localhost',
            #'port' : ports[0].get("HostPort", '8069'),
            #'rpcuser' : 'admin',
            #'rpcpw' : self.sites[self.site_name]['odoo_admin_pw'],
            #'dbuser' : 'odoo', # should be configurable
            #'dbpw' : 'odoo', # should be configurable
            #'dbhost' : dbhost,
            #'docker_postgres_port' : self.default_values.get('docker_postgres_port'),
        #}
        # install_own_modules(self, list_only=False, quiet=False)

    def update_docker_info(self, name, required=False, start=True):
        """
        update_docker_info checks if a docker exists and is started.
        If it does not exist and required is false, the container is created and started.
        If it does not exist and required is True, an error is thrown.
        If it does exist and is stoped and start is True, it is started.
        If it does exist and is stoped and start is False, nothing happens.

        In all cases, status info read from the docker engine is saved into the registry
        maintained in self.default_values['docker_registry']
        """
        registry = self.default_values.get('docker_registry', {})
        cli = self.default_values.get('docker_client')
        # check whether a container with the requested name exists.
        # similar to docker ps -a, we need to also consider the stoped containers
        exists  = cli.containers(filters={'name' : name}, all=1)
        if exists:
            # collect info on the container
            # this is equivalent to docker inspect name
            try:
                info = cli.inspect_container(name)
            except docker.errors.NotFound:
                info = []
            if info:
                if info['State']['Status'] != 'running':
                    if start:
                        cli.restart(name)
                        info = cli.containers(filters={'name' : name})
                        if not info:
                            raise ValueError('could not restart container %s', name)
                        info = info[0]
                    elif required:
                        raise ValueError('container %s is stoped, no restart is requested', name)
                registry[name] = info
            else:
                if required:
                    if name == 'db':
                        print DOCKER_DB_MISSING
                        return
                    raise ValueError('required container:%s does not exist' % name)
        else:
            if required:
                if name == 'db':
                    print DOCKER_DB_MISSING
                    return
                raise ValueError('required container:%s does not exist' % name)
        self.default_values['docker_registry'] = registry

    def update_container_info(self):
        """
        update_container_info tries to start all docker containers a site is associated with:
        The server where these dockers reside, depends on the options selected.
        It could be either localhost, or the remote host.
        Either two or three containers are handeled on each site:
        - db: this is the container containing the database.
              it is only checkd for existence and started when stopped.
        - $DOCKERNAME: This is the docker that containes the actual site
              The value of $DOCKERNAME is read from the site info using the key 'docker'
        If the site is a slave, and a transfer from the master to the slave is requested:
        - $MASTER_DOCKERNAME: this is the container name of the master site as found in sites.py.
        """
        name = self.site_name
        site_info = self.sites[name]
        server_type  = site_info.get('server_type')
        docker = site_info.get('docker')
        if not docker or not docker.get('container_name'):
            print 'the site description for %s has no docker description or no container_name' % opts.name
            return
        # collect info on database container which allways is named 'db'
        self.update_docker_info(self.db_container_name, required=True) 
        self.update_docker_info(docker['container_name'])
        # check whether we are a slave
        if self.opts.transferdocker and site_info.get('slave_info'):
            master_site = site_info.get('slave_info').get('master_site')
            if master_site:
                self.update_docker_info(master_site)

    # -------------------------------
    # check_and_create_container
    # checks if a docker container for the actual site exists
    # if not it is created and started
    # if it exists but not started it is started
    # --------------------------------
    def _create_container(self, docker_template, info_dic):
        """this is a helper method that does the actual creation of the container
        
        Arguments:
            template {string} -- template used to run docker create
            info_dic {dict} -- dictionary with info about values to use with the container

        Achtung:
            can not handle flectra update container
        """
        docker_info = {
            'odoo_port' : info_dic['odoo_port'],
            'odoo_longpoll' : info_dic['odoo_longpoll'],
            'site_name' : info_dic['site_name'],
            'container_name' : info_dic['container_name'],
            'remote_data_path' : info_dic['remote_data_path'],
            'odoo_image_version' : info_dic['odoo_image_version'],
            'odoo_server_data_path' : info_dic['odoo_server_data_path'],
        }
        docker_template = docker_template % docker_info
        mp = self.default_values.get('docker_path_map')
        if mp and self.user != 'root':
            try:
                t, s = mp
                docker_template = docker_template.replace(s, t)
            except:
                pass
        self.run_commands([docker_template], self.user, pw='')

    def check_and_create_container(self, container_name='', rename_container = False, pull_image = False, update_container=False):
        """create a new docker container or manage an existing one
        
        Keyword Arguments:
            container_name {str} -- name of the container, mandatory (default: {''})
            rename_container {bool} -- rename the container by adding a time-stamp to its name (default: {False})
            pull_image {bool} -- pull an actual image from dockerhup (default: {False})
            update_container {bool} -- create a container, that runs etc/runodoo.sh as entrypoint. --stop-after-init (default: {False})
        
        Raises:
            ValueError -- [description]
        """

        name = self.site_name or container_name
        site = self.site
        if name == 'db':
            self.update_docker_info('db')
            site = {
                'docker' : {
                    'container_name' : 'db',
                    'odoo_port' : 'db',
                    'odoo_longpoll' : 'db',
                    'odoo_image_version' : 'db',
                }
            }
            odoo_port = ''
            long_polling_port = ''
        else:
            site = self.site
        
        if not site:
            raise ValueError('%s is not a known site' % name)
        docker_info = site['docker']
        if not container_name:
            # get info on the docker container to use
            #'docker' : {
                #'odoo_image_version': 'odoo:9.0',
                #'container_name'    : 'afbs',
                #'odoo_port'         : '8070',
            #},        
            container_name = docker_info['container_name']
            odoo_port = docker_info['odoo_port']
            if odoo_port == '??':
                print DOCKER_INVALID_PORT % (name, name)
                return()
            long_polling_port = docker_info.get('odoo_longpoll')
            if long_polling_port == '??':
                print DOCKER_INVALID_PORT % (name, name)
                return()
            if not long_polling_port:
                long_polling_port = int(odoo_port) + 10000
            
        if pull_image:
            image = docker_info['odoo_image_version']
            if image:
                self.pull_image(image)
            return
        if rename_container:
            self.stop_container(container_name)
            n = str(datetime.datetime.now()).replace(':', '_').replace('.', '_').replace(' ', '_').replace('-', '_')
            self.rename_container(container_name, '%s.%s' % (container_name, n))
        # if we are running as user root, we make sure that the 
        # folders that are accessed from within odoo belong to the respective 
        # we do that before we start the container, so it has immediat access
        if os.geteuid() == 0:
            # cd to the site folder, preserve old folder
            act_pwd = os.getcwd()
            t_folder = os.path.normpath('%s/%s' % (BASE_INFO['odoo_server_data_path'], name))
            try:
                os.chdir(t_folder)
                user_and_group =  docker_info.get('external_user_group_id', '104:107')
                cmdlines = [
                    ['/bin/chown', user_and_group, 'log'],
                    ['/bin/chown', user_and_group, 'filestore', '-R'],
                ]
                for c in cmdlines:
                    os.system(' '.join(c))
                #self.run_commands(cmdlines, self.user, pw='')
                os.chdir(act_pwd)
            except OSError:
                pass # no such folder
        # the docker registry was created by update_docker_info
        # if this registry does not contain a description for container_name
        # we have to create it
        info_dic = {
            'odoo_port' : odoo_port,
            'odoo_longpoll' : long_polling_port,
            'site_name' : name,
            'container_name' : container_name,
            'remote_data_path' : self.site and self.site.get('remote_server', {}).get('remote_data_path', '') or '',
            'odoo_image_version' : docker_info['odoo_image_version'],
            'odoo_server_data_path' : BASE_INFO['odoo_server_data_path'],           
        }
        if update_container:
            # create a container that runs etc/odoorunner.sh as entrypoint
            from templates.docker_templates import docker_template_update
            self._create_container(docker_template_update, info_dic)    
        elif rename_container or self.default_values.get('docker_registry') \
            and not self.default_values['docker_registry'].get(container_name) or (container_name == 'db'):
            if container_name != 'db':
                from templates.docker_templates import docker_template, flectra_docker_template
                if site.get('server_type', 'odoo') == 'flectra':
                    docker_template = flectra_docker_template
                self._create_container(docker_template, info_dic)
            else:
                # we need a postgres version
                pg_version = self.opts.set_postgers_version
                if not pg_version:
                    print bcolors.FAIL
                    print '*' * 80
                    print 'you must define a postgres version with option -dcdbPG'
                    print '*' * 80
                    print bcolors.ENDC
                    sys.exit()
                
                # here we need to decide , whether we run flectra or odoo
                if site.get('server_type') == 'flectra':
                    from templates.docker_templates import flectra_docker_template
                else:
                    from templates.docker_templates import docker_db_template
                BASE_INFO['postgres_version'] = pg_version
                docker_template = docker_db_template % BASE_INFO
                try:
                    self.run_commands([docker_template], user=self.user, pw='')
                except:
                    pass # did exist allready ??
            if self.opts.verbose:
                print docker_template
        else:
            if self.opts.verbose:
                print 'container %s allready running' % name

    def pull_image(self, imagename):
        """
        docker login
        docker tag e6861e4e5151 robertredcor/afbs:9.0
        docker push robertredcor/afbs
        """
        try:
            self.default_values['docker_client'].pull(imagename)
            print DOCKER_IMAGE_PULLED % (imagename, self.site_name)
        except docker.errors.NotFound:
            print DOCKER_IMAGE_PULL_FAILED % (imagename, self.site_name)

    def push_image(self):
        """
        docker login
        docker tag e6861e4e5151 robertredcor/afbs:9.0
        docker push robertredcor/afbs
        """
        client = self.default_values['docker_client']
        name = self.site_name
        site = self.site
        if not site:
            raise ValueError('%s is not a known site' % name)
        docker_info = site['docker']
        image = docker_info['odoo_image_version']
        if image:
            images = [i['RepoTags'] for i in client.images()]
            found = False
            for tags in images:
                for tag in tags:
                    if tag == image:
                        found = True
                        break
                if found:
                    break
        if not found:
            print DOCKER_IMAGE_NOT_FOUND % image
        self.dockerhub_login()
        result = client.push(image, stream=True)
        for line in result:
            print line
        

    def dockerhub_login(self):
        client = self.default_values['docker_client']
        site = self.site
        docker_info = site['docker']
        hname =  docker_info.get('hub_name', 'docker_hub')
        if hname != 'docker_hub':
            raise ValueError('only docker_hub is suported when login in')
        hub_info = site['docker_hub'].get(hname)
        if not hub_info:
            print DOCKER_IMAGE_PUSH_MISING_HUB_INFO % self.site_name
        user = hub_info.get('user')
        pw = hub_info.get('docker_hub_pw')
        try:
            client.login(username=user, password=pw)
        except:
            raise ValueError('could  not log in to docker hub, user or pw wrong')
                
    def collect_extra_libs(self):
        """
        collect apt modules and pip libraries needed to construct image with expected capabilities
        we collect them from the actual site, and all sites named with the option -sites
        """
        extra_libs = self.site.get('extra_libs', {})        
        if self.opts.use_collect_sites:
            version = self.version
            more_sites = []
            for k, v in self.sites.items():
                if v.get('odoo_version') == version:
                    more_sites.append(k)
        else:
            more_sites = (self.opts.use_sites or '').split(',')
        # libraries we need to install using apt
        apt_list = extra_libs.get(APT_COMMAND, [])       
        # libraries we need to install using pip
        pip_list = extra_libs.get(PIP_COMMAND, [])  
        for addon in self.site.get('addons', []):
            pip_list += addon.get('pip_list', [])
            apt_list += addon.get('apt_list', [])
        for s in more_sites:
            if not s:
                continue
            site = self.sites.get(s)
            if not site:
                print(SITE_NOT_EXISTING % s)
                continue
            apt_list += site.get('extra_libs', {}).get(APT_COMMAND, [])
            pip_list += site.get('extra_libs', {}).get(PIP_COMMAND, [])
            for addon in self.site.get('addons', []):
                pip_list += addon.get('pip_list', [])
                apt_list += addon.get('apt_list', [])
            
        if apt_list:
            apt_list = list(set(apt_list))
        if pip_list:
            pip_list = list(set(pip_list))
        if self.opts.verbose:
            print bcolors.WARNING
            print '*' * 80
            print 'apt_list:%s' % apt_list
            print 'pip_list:%s' % pip_list
            print bcolors.ENDC
        return apt_list, pip_list
         
    def build_image(self):
        """
        build image that has all python modules installed mentioned in the site description
        the base odo image is also read from the site description
        
        a docker image will only be buildt when the site description has a docker_hub block.
        """
        from templates.docker_templates import docker_base_file_template, docker_run_apt_template, docker_run_no_apt_template, \
             docker_odoo_setup_requirements, docker_odoo_setup_version, docker_odoo_setup_script
        def apt_lines(block):
            if not block:
                return []
            result = ['&& apt-get install -y --no-install-recommends']
            pref = ' ' * 4
            for line in block:
                result.append(pref + line.strip())
            return result
        docker_info = self.site.get('docker', {})
        # do we have a dockerhub user?
        hub_name  = docker_info.get('hub_name', '')
        if not hub_name:
            print DOCKER_IMAGE_CREATE_MISING_HUB_INFO % self.site_name
            return
        dockerhub_user = self.site.get('docker_hub', {}).get(hub_name, {}).get('user')
        dockerhub_user_pw = self.site.get('docker_hub', {}).get(hub_name, {}).get('docker_hub_pw')
        if not dockerhub_user or not dockerhub_user_pw:
            print DOCKER_IMAGE_CREATE_MISING_HUB_USER % self.site_name
            return
        
        # copy files from the official odoo docker file to the sites data directory
        # while doing so adapt the dockerfile to pull all needed elements
        odoo_version = self.site['odoo_version']
        if not odoo_version in ODOO_VERSIONS.keys():
            print ODOO_VERSION_BAD % (self.site_name, self.site['odoo_version'])
            return
        docker_source_path = '%s/docker/docker/%s/' % (self.default_values['odoo_server_data_path'], odoo_version)
        # get path to where we want to write the docker file
        docker_target_path = '%s/docker/' % self.default_values['data_dir']
        if not os.path.exists(docker_target_path):
            os.mkdir(docker_target_path)
        # there are some files we can copy unaltered
        #for fname in DOCKER_FILES[odoo_version]:
            #shutil.copy('%s%s' % (docker_source_path, fname), docker_target_path)
        # construct dockerfile from template
        apt_list, pip_list = self.collect_extra_libs()
        #line_matcher = re.compile(r'\s+&& pip install.+')
        with open('%sDockerfile' % docker_target_path, 'w' ) as result:
            pref = ' ' * 8
            data_dic = {
               'odoo_image_version'  : docker_info.get('base_image', 'camptocamp/odoo-project:%s-latest' % odoo_version),
               'apt_list' : '\n'.join(['%s%s \\' % (pref, a) for a in apt_list]),
            }
            if pip_list:
                data_dic['pip_install'] = '&& pip install'
                data_dic['pip_list'] = (' '.join(['%s' % p for p in pip_list])) + ' \\'
            else:
                data_dic['pip_install'] = ''
                data_dic['pip_list'] = '\\'
                
            # depending whether there are python-libraries and or apt modules to install
            # we have to constuct a docker run block
            if apt_list:
                data_dic['run_block'] = docker_run_apt_template % data_dic
            elif pip_list:
                data_dic['run_block'] = docker_run_no_apt_template % data_dic
            else:
                data_dic['run_block'] = ''
            docker_file = (docker_base_file_template % data_dic).replace('\\ \\', '\\') 
            result.write(docker_file)
        # construct folder layout as expected by the base image
        # see https://github.com/camptocamp/docker-odoo-project/tree/master/example
        for f in ['external-src', 'local-src', 'data', 'features', 'songs']:
            try:
                td = '%s%s' % (docker_target_path, f)
                if not os.path.exists(td):
                    os.mkdir(td )
            except OSError: 
                pass
        for f in [
            ('VERSION', docker_odoo_setup_version % str(date.today())),
            ('migration.yml', ''),
            ('requirements.txt', docker_odoo_setup_requirements),
            ('setup.py', docker_odoo_setup_script),]:
            # do not overwrite anything ..
            fp = '%s%s' % (docker_target_path, f[0])
            if not os.path.exists(fp):
                open(fp, 'w').write(f[1])
            else:
                print '%s\n%s\n%snot overwitten %s' % (bcolors.WARNING, '-'*80, fp, bcolors.ENDC)
        # check out odoo source
        act = os.getcwd()
        os.chdir(docker_target_path)
        cmd_lines = [
            'git init .',
            'git submodule init',
            'git submodule add -b %s https://github.com/odoo/odoo.git src' % odoo_version
        ]
        self.run_commands(cmd_lines=cmd_lines)
        #for line in open( '%sDockerfile' % docker_source_path, 'r' ):
            #if line_matcher.match(line):
                #pip_line = line
                #pref = ' ' * 8
                ## write out all librarieds needed for the new python libraries to be
                ## installed by pip
                #for line in apt_lines(apt_list):
                    #result.write( pref + line + " \\\n")
                ## finally add the pip line embellished with our own list
                #result.write( pref + pip_line.strip() + ' '  + ' '.join([p.strip() for p in pip_list]) + '\n')
            #else:
                #result.write( line ) 
        print DOCKER_IMAGE_CREATE_PLEASE_WAIT
        tag = docker_info['odoo_image_version']
        try:
            result = self.default_values['docker_client'].build(
                docker_target_path, 
                tag = tag, 
                dockerfile = '%sDockerfile' % docker_target_path)
            for line in result:
                line = eval(line)
                if isinstance(line, dict):
                    if line.get('errorDetail'):
                        print DOCKER_IMAGE_CREATE_ERROR % (self.site_name, self.site_name, line.get('errorDetail'))
                        return
                    status = line.get('status')
                    if status:
                        print line['status'].strip()
                        continue
                    sl = line.get('stream')
                    if not sl:
                        print DOCKER_IMAGE_CREATE_ERROR % (
                            self.site_name, 
                            self.site_name, 
                            'no stream element found processing Dockerfile')
                    print line['stream'].strip()
        except docker.errors.NotFound:
            print DOCKER_IMAGE_CREATE_FAILED % (self.site_name, self.site_name)
        else:
            # the last line is something like:
            # {"stream":"Successfully built 97cea8884220\n"}
            print DOCKER_IMAGE_CREATE_DONE % (line['stream'].strip().split(' ')[-1], tag, tag)                

    def rename_container(self, name, new_name):
        """
        """
        try:
            self.default_values['docker_client'].stop(name)
            self.default_values['docker_client'].rename(name, new_name)
            print 'rename %s to %s' % (name, new_name)
        except:
            print 'container %s nicht gefunden' % name

    def stop_container(self, name=''):
        """
        """
        if not name:
            name = self.site_name
        try:
            print 'stoping container %s' % name
            self.default_values['docker_client'].stop(name)
            print 'stopped %s' % name
        except docker.errors.NotFound:
            print 'container %s nicht gefunden' % name
            
        

    def start_container(self, name=''):
        """
        """
        if not name:
            name = self.site_name
        print 'starting container %s' % name
        self.default_values['docker_client'].start(name)
        print 'started %s' % name

    def restart_container(self, name=''):
        """
        """
        if not name:
            name = self.site_name
        print 'restarting container %s' % name
        self.default_values['docker_client'].restart(name)
        print 'restarted %s' % name

    def doTransfer(self):
        """
        """
        super(dockerHandler, self).doTransfer()

    def checkImage(self, image_name):
        """
        """
        # todo should also check remotely
        return self.default_values['docker_client'].images(image_name)

    def createDumperImage(self):
        """
        """
        act = os.getcwd()
        p = '%s/dumper' % self.sites_home
        os.chdir(p)
        self.run_commands([['docker build  -t dbdumper .']], self.user, pw='')
        os.chdir(act)

    def doUpdate(self, db_update=True, norefresh=None, names=[], set_local=True):
        """
        set_local is not used yet
        """
        # self.update_container_info()
        # we need to learn what ip address the local docker db is using
        # if the container does not yet exists, we create them (master and slave)
        self.check_and_create_container()
        server_dic = get_remote_server_info(self.opts)
        # we have to decide, whether this is a local or remote
        remote_data_path = server_dic['remote_data_path']
        dumper_image = BASE_INFO.get('docker_dumper_image')
        if not dumper_image:
            print bcolors.FAIL + \
                  'the %s image is not available. please create it first. ' \
                  'insturctions on how to do it , you find in %s/dumper' % (
                      dumper_image,
                      self.default_values['sites_home'] + bcolors.ENDC)
        if not self.checkImage(dumper_image):
            self.createDumperImage()
            if not self.checkImage(dumper_image):
                print bcolors.FAIL + \
                      'the %s image is not available. please create it first. ' \
                      'insturctions on how to do it , you find in %s/dumper' % (
                          dumper_image,
                          self.default_values['sites_home'] + bcolors.ENDC)
                return

        #mp = self.default_values.get('docker_path_map')
        #if mp and ACT_USER != 'root':
            #t, s = mp
            #remote_data_path = remote_data_path.replace(s, t)
        self.stop_container(self.site_name)
        self._doUpdate(db_update, norefresh, self.site_name, self.opts.verbose and ' -v' or '')

        # if we know admins password, we set it
        # for non docker pw is usualy admin, so we do not use it
        #adminpw = self.sites[self.site_name].get('odoo_admin_pw')
        #if adminpw:
            #cmd_lines_docker += [['%s/psql' % where, '-U', user, '-d', site_name,  '-c', "update res_users set password='%s' where login='admin';" % adminpw]]

        self.start_container(self.site_name)


    def docker_install_own_modules(self, list_only=False, quiet=False):
        """
        """
        if list_only:
            return install_own_modules(self.opts, self.default_values, list_only, quiet)
        # get_module_obj
        docker_info = self.default_values['docker_registry'].get(self.site_name)
        db_info = self.default_values['docker_registry'].get(self.site_name)
        if not db_info:
            print bcolors.FAIL + 'no docker container %s running' % self.site_name + bcolors.ENDC
            if self.opts.docker_start_container:
                print bcolors.WARNING + 'it will be created' + bcolors.ENDC
                self.check_and_create_container()
                self.update_container_info()
            else:
                return
        return self.install_own_modules( list_only, quiet)


    # shell
    # -----
    # shell runs and eneters a shell
    # in a docker container
    def run_shell(self):
        container_name = self.opts.shell
        print 'docker exec -it %s bash' % container_name
        os.system('docker exec -it %s bash' % container_name)
        return

    def execute_in_shell(self, cmd_lines):
        """
        execute_in_shell enters a container by its shell
        and executes a command
        Args:
            cmd_lines (list): This is a list of [commands] to be executed
                         within the shell
                         
        Returns:
            tuple: (return_code, "error message")
        """
        import json
        class StreamLineBuildGenerator(object):
            def __init__(self, json_data):
                self.__dict__ = json.loads(json_data)

        # make sure container is up and running
        self.check_and_create_container()
        # this places info about the running container into the default_values
        docker_info = self.default_values['docker_registry'].get(self.site_name)
        if not docker_info:
            print bcolors.FAIL + 'no docker container %s running' % self.site_name + bcolors.ENDC
            return
        # the docker id is used to access the running container
        container_id = docker_info['Id']
        # we need an interface to the docker engine
        cli = self.default_values.get('docker_client')

        for cmds in cmd_lines:
            exe = cli.exec_create(container=container_id, cmd=cmds, tty=True, privileged=True)
            exe_start= cli.exec_start(exec_id=exe, stream=True, tty=True,)
            
            #for val in exe_start:
                #print (val)    
            
            for line in exe_start:
                try:
                    stream_line = StreamLineBuildGenerator(line)
                    # Do something with your stream line
                    # ...
                except ValueError:
                    # If we are not able to deserialize the received line as JSON object, just print it out
                    print(line)
                    continue    
            
                
        #http://stackoverflow.com/questions/35207295/docker-py-exec-start-howto-stream-the-output-to-stdout    # execute_in_shell


    def docker_add_ssh(self):
        """
        runs self.execute_in_shell and installs openssh server
        using apt get.
        It then creates a /root/.ssh folder in the container and 
        copies the id_rsa.pub found in the local .ssh folder to
        the containers /root/.ssh/autorized_keys file
        
        Args:
                         
        Returns:

        """
        try:
            key_pub = open(os.path.expanduser('~/.ssh/id_rsa.pub'), 'r').read()
        except:
            print bcolors.FAIL, 'could not read %s' % os.path.expanduser('~/.ssh/id_rsa.pub'), bcolors.ENDC
            return
        cmds = [
            ['/usr/bin/apt', 'update'],
            ['/usr/bin/apt', 'install', '-y', 'openssh-server'],
            ['mkdir', '-p', '/root/.ssh'],
            ['echo',  key_pub, '>', '/root/.ssh/authorized_keys'],
        ]
        self.execute_in_shell(cmds)
        
    def docker_start_ssh(self):
        """
        runs self.execute_in_shell and start openssh server
        Args:
                         
        Returns:

        """
        cmds = [['service', 'ssh', 'start']]
        self.execute_in_shell(cmds)
        
    def docker_show(self, what='base'):
        """
        docker_show displays a list information about a containe        
        Args:
                         
        Returns:

        """
        # make sure container is up and running
        self.check_and_create_container()
        # this places info about the running container into the default_values
        docker_info = self.default_values['docker_registry'].get(self.site_name)
        if not docker_info:
            print bcolors.FAIL + 'no docker container %s running' % self.site_name + bcolors.ENDC
            return
        # the docker id is used to access the running container
        indent = '    '
        if what == 'base':
            name = docker_info['Name']
            print '-' * len(name)
            print name
            print '-' * len(name)
            
            running = docker_info['State']['Running']
            
            print 'running:', running and bcolors.OKGREEN, running, bcolors.ENDC
            if running:
                print indent, 'Pid:', docker_info['State']['Pid']
                print indent, 'StartedAt:', docker_info['State']['StartedAt']
            print 'Network settings'
            print '----------------'
            for n in ['IPAddress','Gateway']:
                print indent, n, ':', docker_info['NetworkSettings'][n]
            print 'Ports'
            print '-----'
            for k,v in docker_info['NetworkSettings']['Ports'].items():
                print indent, k, ':', v
            print 'Volumes'
            print '-------'
            for v in docker_info['Mounts']:
                print indent, v['Destination']
                print indent * 2, v['Source']
                

        else:
            if what != 'all':
                what = what.split[',']
            for k,v in docker_info.items():
                if what != 'all' or not k in what:
                    print k, ':'
                    if isinstance(v, (basestring, int)):
                        print indent, v
                    elif isinstance(v, (tuple, list)):
                        for elem in v:
                            if isinstance(elem, basestring):
                                print indent * 2, elem
                            elif isinstance(elem, dict):
                                for kk,vv in elem.items():
                                    print indent * 2, kk, ':', vv
                                print indent * 2, '-' * 10
                    elif isinstance(v, dict):
                        for kk,vv in v.items():
                            print indent * 2, kk, ':', vv
                        print indent * 2, '-' * 10
        
