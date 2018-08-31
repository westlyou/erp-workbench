import collections
# this config file should work for both
# flectra and odoo
# the following values have to be adapted in the configurator 
# - xmlrpc_port
# - longpolling_port
# - logfile
# - datadir
# - addon path weg muss /opt/odoo/local-src,/opt/odoo/src/addons,
# - hinzu 
# - server wide modules ??
d = collections.OrderedDict()

d['csv_internal_sep'] = ','
d['data_dir'] = '%(data_dir)s'
# as this instance runs in a docker container
# the db_host is the name of a linked container with the database
d['db_host'] = 'db'
d['db_maxconn'] = 20
d['db_password'] = 'odoo'
d['db_port'] = False
d['db_template'] = 'template1'
d['db_user'] = 'odoo'
d['debug_mode'] = False
d['demo'] = '{}'
d['email_from'] = False
d['geoip_database'] = '/usr/share/GeoIP/GeoLiteCity.dat'
d['limit_memory_hard'] = 2684354560
d['limit_memory_soft'] = 2147483648
d['limit_request'] = 8192
d['limit_time_cpu'] = 600
d['limit_time_real'] = 1200
d['list_db'] = True
d['log_db'] = False
d['log_db_level'] = 'warning'
d['log_handler'] = ':INFO'
d['log_level'] = 'info'
d['logfile'] = '%(logfile)s'
d['logrotate'] = True
d['longpolling_port'] = '%(longpolling_port)s'
d['max_cron_threads'] = 2
d['netrpc'] = False
d['osv_memory_age_limit'] = '1.0'
d['osv_memory_count_limit'] = False
d['pg_path'] = 'None'
d['pidfile'] = False
# We can activate proxy_mode even if we are not behind a proxy, because
# it is used only if HTTP_X_FORWARDED_HOST is set in environ
d['proxy_mode'] = True
d['reportgz'] = False
d['server_wide_modules'] = '%(server_wide_modules)s'
d['smtp_password'] = False
d['smtp_port'] = 25
d['smtp_server'] = 'localhost'
d['smtp_ssl'] = False
d['smtp_user'] = False
d['syslog'] = False
d['running_env'] = 'dev'
d['test_commit'] = False
d['test_enable'] = False
d['test_file'] = False
d['test_report_directory'] = False
d['translate_modules'] = ['all']
d['unaccent'] = False
d['without_demo'] = 'all'
d['workers'] = 4
d['xmlrpc'] = True  # Activate HTTP
d['xmlrpc_port'] = '%(xmlrpc_port)s'
d['xmlrpcs'] = False

CONFIG_DEFAULTS = d

