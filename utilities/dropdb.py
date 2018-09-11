#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import shutil
from pprint import pprint

sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
from config import BASE_INFO, SITES, ACT_USER
import psycopg2


SQL = """SELECT pg_terminate_backend(pg_stat_activity.pid) \
  FROM pg_stat_activity \
  WHERE pg_stat_activity.datname = '%s' \
    AND pid <> pg_backend_pid();"""
SQL2 = "DROP DATABASE %s"

#from optparse import OptionParser
class bcolors:
    """
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

dbpw = 'admin'
db_name = len(sys.argv) > 1 and sys.argv[1]
if not db_name:
    print('no database name provided')
    sys.exit()

conn_string = "dbname='%s' user=%s host='%s' password='%s'" % ('postgres', ACT_USER, 'localhost', dbpw)
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
cursor.execute('SET AUTOCOMMIT = ON;')
print('close connections')
print(cursor.execute(SQL % db_name))
print(cursor.fetchall())
print(conn.commit())
conn.close()
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
conn.autocommit = True
print('drop db %s' % db_name)
print(cursor.execute(SQL2 % db_name))
print(conn.commit())
print(conn.close())