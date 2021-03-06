default_values = {
    'addlinks': None,
    'addons_path': '%(addons_path)s',
    'admin_passwd': 'admin',
    'base_path': '%(base_path)s',
    'create_database': True,
    'csv_internal_sep': ',',
    'current_user': '%(db_user)s',
    'data_dir': '%(data_dir)s',
    'db_host': 'localhost',
    'db_maxconn': '64',
    'db_name': '%(db_name)s',
    'db_password': 'admin',
    'db_port': False,
    'db_template': 'template1',
    'db_user': '%(db_user)s',
    'dbfilter': '%(db_name)s',
    'debug_mode': False,
    'demo': False,
    'dev_mode': True,
    'email_from': False,
    'geoip_database': '/usr/share/GeoIP/GeoLiteCity.dat',
    'import_partial': '',
    'inner': '%(inner)s',
    'limit_memory_hard': '2684354560',
    'limit_memory_soft': '2147483648',
    'limit_request': '8192',
    'limit_time_cpu': '60',
    'limit_time_real': '120',
    'list_db': True,
    'log_db': '%(db_name)s',
    'log_db_level': 'warning',
    'log_handler': ':INFO',
    'log_level': 'info',
    'logfile': 'None',
    'logrotate': True,
    'longpolling_port': '8072',
    'max_cron_threads': '2',
    'netrpc': False,
    'erp_version': '%(erp_version)s',
    'erp_minor': '%(erp_minor)s',
    'osv_memory_age_limit': '1.0',
    'osv_memory_count_limit': False,
    'outer': '%(outer)s',
    'parts_dir_name': 'parts',
    'pg_password': '%(pg_password)s',
    'pg_path': 'None',
    'pidfile': 'None',
    # 'project_path': '%(project_path)s',
    # 'projectname': '%(site_name)s',
    'proxy_mode': False,
    #'_data_dir': '%(remote_datadir)s',
    #'remote_database': 'afbsecure',
    # 'remote_db_user': '%(db_user)s',
    # 'remote_dump_path': '%(remote_dump_path)s',
    # 'remote_localhost': 'localhost',
    # 'remote_url': 'localhost',
    # 'remote_user': '%(db_user)s',
    'reportgz': False,
    # 'running_local': True,
    'server_wide_modules': 'None',
    'smtp_password': False,
    'smtp_port': '25',
    'smtp_server': '%(smtp_server)s',
    'smtp_ssl': False,
    'smtp_user': False,
    'syslog': False,
    'test_commit': False,
    'test_enable': False,
    'test_file': False,
    'test_report_directory': False,
    'unaccent': False,
    # 'use_docker': '',
    'username': '%(db_user)s',
    'without_demo': True,
    # 'workers': '0',
    'xmlrpc': True,
    'xmlrpc_interface': '',
    'xmlrpc_port': '8069',
    'xmlrpcs': False,
    # 'pip_modules' : ''
}
