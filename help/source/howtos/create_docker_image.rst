Create Docker Image
-------------------

Creating a docker image consist of several steps:

    - collect all apt modules we need next to the one odoo is providing
    - collect all pip libraries we need next to the one odoo is providing
        This information we find in the site description files in a ::
        
            'extra_libs': {
                'pip' : [
                    'xmlsec',
                    'scrapy',
                    'html2text',
                ],
                'apt' : [
                    'python-dev',
                    'pkg-config',
                    'libxml2-dev',
                    'libxslt1-dev',
                    'libxmlsec1-dev',
                    'libffi-dev',
                ]
            },

        section
    - we neet to be able to log into docker hub to be able to push the image
    - downloading the actuall odoo source
    - creating a number of folders that will be copied into the image

This process is done semiautomatically by running the following command::

    wwb
    bin/d -dbi SITENAME -dbiC # where SITENAME could be afbstest


Create DB Image
---------------
before changing anythin with an existing container, please check wher its data is by running::

    docker inspect db


docker_db_template::

    docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo \
    -v %(erp_server_data_path)s/database/data:/var/lib/postgresql/data --name db --restart always \
    -p 55432:5432 postgres:%(postgres_version)s



sample configuration created with https://pgtune.leopard.in.ua::

    # DB Version: 10
    # OS Type: linux
    # DB Type: web
    # Total Memory (RAM): 1 GB
    # Connections num: 500
    # Data Storage: hdd

    max_connections = 500
    shared_buffers = 256MB
    effective_cache_size = 768MB
    maintenance_work_mem = 64MB
    checkpoint_completion_target = 0.7
    wal_buffers = 7864kB
    default_statistics_target = 100
    random_page_cost = 4
    effective_io_concurrency = 2
    work_mem = 524kB
    min_wal_size = 1GB
    max_wal_size = 2GB


query settings::

    SELECT * FROM pg_settings;

    SELECT *
    FROM   pg_settings
    WHERE  name = 'max_connections';
