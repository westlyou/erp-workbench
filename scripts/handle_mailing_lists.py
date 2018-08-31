#!bin/python
# -*- encoding: utf-8 -*-
import sys
import os
import psycopg2
from optparse import OptionParser


def main(opts):
    """
    """
    if opts.pw:
        conn_string = "dbname='%s' user=%s host='%s' password='%s'" % (
            opts.dbname, opts.user, opts.host, opts.pw)
    else:
        conn_string = "dbname='%s' user=%s host='%s'" % (opts.dbname,
                                                         opts.user, opts.host)

    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    ifile = opts.input
    if not ifile:
        print '*' * 80
        print 'no inputfile defined'
        sys.exit()

    if not os.path.exists(ifile):
        print '*' * 80
        print '%s not found' % ifile
        sys.exit()

    mailinglist = opts.mailinglist
    if not mailinglist:
        print '*' * 80
        print 'no mailinglist defined'
        sys.exit()

    # does mailing list exist ?
    try:
        cursor.execute('select * from mail_mass_mailing_list')
    except psycopg2.ProgrammingError:
        print '*' * 80
        print 'mass mailing seems not to be installed for %s' % opts.dbname
        sys.exit()

    mlist_name = opts.mailinglist
    cursor.execute("select id from mail_mass_mailing_list where name = '%s'" %
                   mlist_name)
    row = cursor.fetchone()
    if not row:
        print '*' * 80
        print '%s mailing list does not exist for %s' % (mlist_name,
                                                         opts.dbname)
        sys.exit()
    mailinglist_id = row[0]
    emails = open(ifile)
    for line in emails:
        if line.find('@') > -1:
            #xxxx validate email ..
            email = line.strip()
            s = "select id from mail_mass_mailing_contact where email = '%s' and list_id = %s" % (
                email, mailinglist_id)
            cursor.execute(s)
            row = cursor.fetchone()
            if not row:
                s = "INSERT INTO mail_mass_mailing_contact (email, list_id) values ('%s', %s)" % (
                    email, mailinglist_id)
                cursor.execute(s)
                conn.commit()
                print email
    print '-- done --'


if __name__ == '__main__':
    usage = "makeusers_direct.py -h for help on usage"
    parser = OptionParser(usage=usage)

    parser.add_option(
        "-H",
        "--host",
        action="store",
        dest="host",
        default='localhost',
        help="define host default localhost")

    parser.add_option(
        "-d",
        "--dbname",
        action="store",
        dest="dbname",
        default='afbs',
        help="define host default ''")

    parser.add_option(
        "-i",
        "--input",
        action="store",
        dest="input",
        help="path to read email addresses from")

    parser.add_option(
        "-m",
        "--mailinglist",
        action="store",
        dest="mailinglist",
        help="mailinglist to add emails to")

    parser.add_option(
        "-u",
        "--user",
        action="store",
        dest="user",
        default='robert',
        help="define user default odoo")

    parser.add_option(
        "-p",
        "--pw",
        action="store",
        dest="pw",
        default='',
        help="define password default ''")

    (opts, args) = parser.parse_args()
    main(opts)
