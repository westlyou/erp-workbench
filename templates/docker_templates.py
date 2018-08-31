
# --------------------------------------------------
# -------------------- flectra ------------------------
# --------------------------------------------------
docker_template = """
docker run -p 127.0.0.1:%(odoo_port)s:8069 -p 127.0.0.1:%(odoo_longpoll)s:8072 --restart always \
    -v %(odoo_server_data_path)s/%(site_name)s/etc:/etc/odoo \
    -v %(odoo_server_data_path)s/%(site_name)s/start-entrypoint.d:/opt/odoo/start-entrypoint.d \
    -v %(odoo_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \
    -v %(odoo_server_data_path)s/%(site_name)s/dump:/mnt/dump \
    -v %(odoo_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore \
    -v %(odoo_server_data_path)s/%(site_name)s/:/var/lib/odoo/ \
    -v %(odoo_server_data_path)s/%(site_name)s/log:/var/log/odoo \
    -e LOCAL_USER_ID=1000 -e DB_NAME=%(site_name)s \
    -e PYTHONIOENCODING=utf-8 \
    --name %(container_name)s -d --link db:db -t %(odoo_image_version)s
"""
# for docker_template_update I changed:
# --restart always -> --rm
# -d -> ''
# -> --init /etc/odoo/runodoo.sh \
docker_template_update = """
docker run -p 127.0.0.1:%(odoo_port)s:8069 -p 127.0.0.1:%(odoo_longpoll)s:8072 --rm \
    --entrypoint /etc/odoo/runodoo.sh \
    -v %(odoo_server_data_path)s/%(site_name)s/etc:/etc/odoo \
    -v %(odoo_server_data_path)s/%(site_name)s/start-entrypoint.d:/opt/odoo/start-entrypoint.d \
    -v %(odoo_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \
    -v %(odoo_server_data_path)s/%(site_name)s/dump:/mnt/dump \
    -v %(odoo_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore \
    -v %(odoo_server_data_path)s/%(site_name)s/:/var/lib/odoo/ \
    -v %(odoo_server_data_path)s/%(site_name)s/log:/var/log/odoo \
    -e LOCAL_USER_ID=1000 -e DB_NAME=%(site_name)s \
    -e PYTHONIOENCODING=utf-8 \
    --name %(container_name)s_tmp --link db:db -t %(odoo_image_version)s
"""

docker_db_template = """
    docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo \
    -v %(odoo_server_data_path)s/database/data:/var/lib/postgresql/data --name db --restart always \
    -p 55432:5432 postgres:%(postgres_version)s
"""

docker_file_template = """
FROM %(odoo_base_image)s

# Install dependencies
RUN apt-get update && apt-get install -y \

RUN add-apt-repository universe
RUN apt-get update && apt-get install -y \
    python-pip
RUN pip install %(pip_list)s
"""
docker_run_apt_template = """# Project's specifics packages
RUN set -x; \\
        apt-get update \\
        && apt-get install -y --no-install-recommends \\
        %(apt_list)s \\
        %(pip_install)s %(pip_list)s \\
        && apt-get remove -y \\
        %(apt_list)s \\
        && apt-get clean \\
        && rm -rf /var/lib/apt/lists/*
"""
docker_run_no_apt_template = """# Project's specifics packages
RUN set -x; \\
        %(pip_install)s %(pip_list)s \\
"""

docker_base_file_template = """
FROM %(odoo_image_version)s
MAINTAINER robert@redo2oo.ch

%(run_block)s

COPY ./requirements.txt /opt/odoo/
RUN cd /opt/odoo && pip install -r requirements.txt

ENV ADDONS_PATH=/opt/odoo/local-src,/opt/odoo/src/addons
#ENV DB_NAME=afbsdemo
ENV MIGRATE=False
# Set the default config file
ENV OPENERP_SERVER /etc/odoo/openerp-server.conf
"""
docker_odoo_setup_version = """
%s.0
"""
docker_odoo_setup_requirements = """
# project's packages, customize for your needs:
unidecode==0.4.14
"""

docker_odoo_setup_script = """
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('VERSION') as fd:
    version = fd.read().strip()

setup(
    name="my-project-name",
    version=version,
    description="project description",
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    author="Author...",
    author_email="email...",
    url="url...",
    packages=['songs'] + ['songs.%s' % p for p in find_packages('./songs')],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved',
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
"""
# --------------------------------------------------
# -------------------- FLECTRA ---------------------
# --------------------------------------------------
flectra_docker_template = """
docker run -p 127.0.0.1:%(odoo_port)s:7073 -p 127.0.0.1:%(odoo_longpoll)s:7072 --restart always \
    -v %(odoo_server_data_path)s/%(site_name)s/etc:/etc/flectra \
    -v %(odoo_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \
    -v %(odoo_server_data_path)s/%(site_name)s/dump:/mnt/dump \
    -v %(odoo_server_data_path)s/%(site_name)s/filestore:/var/lib/flectra/filestore \
    -v %(odoo_server_data_path)s/%(site_name)s/:/var/lib/flectra/ \
    -v %(odoo_server_data_path)s/%(site_name)s/log:/var/log/flectra \
    -e LOCAL_USER_ID=1000 -e DB_NAME=%(site_name)s \
    -e PYTHONIOENCODING=utf-8 \
    --name %(container_name)s -d --link db:db -t %(odoo_image_version)s
"""
