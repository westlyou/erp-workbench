#!bin/python
# -*- encoding: utf-8 -*-

from config import SITES #, BASE_INFO, GLOBALDEFAULTS
#from config.handlers import InitHandler, DBUpdater
from .create_handler import InitHandler
import os
import sys
from .utilities import bcolors
from scripts.messages import *
import datetime
#from froxlor.wrapper import DatabaseObject, PanelCustomer, PanelDomain
try:
    from sqlalchemy.sql import select, and_
    from sqlalchemy import create_engine, inspect
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Table, MetaData
    from sqlalchemy import or_
except ImportError:
    pass

DOMAIN_DEFAULTS = {
    #'id' :                      '8',
    'domain' :                  'brun-del-re.ch',
    'adminid' :                 '1',
    'customerid' :              '1',
    'aliasdomain' :             None,
    'documentroot' :            '/var/syscp/webs/redcor/',
    'isbinddomain' :            '1',
    'isemaildomain' :           '1',
    'email_only' :              '0',
    'iswildcarddomain' :        '1',
    'subcanemaildomain' :       '0',
    'caneditdomain' :           '1',
    'zonefile' :                '',
    'dkim' :                    '1',
    'dkim_id' :                 '0',
    'dkim_privkey' :            '',
    'dkim_pubkey' :             '',
    'wwwserveralias' :          '1',
    'parentdomainid' :          '0',
    'openbasedir' :             '1',
    'openbasedir_path' :        '0',
    'speciallogfile' :          '0',
    'ssl_redirect' :            '0',
    'specialsettings' :         '',
    'deactivated' :             '0',
    'bindserial' :              '2012111200',
    'add_date' :                '1285921119',
    'registration_date' :       '2000-01-01',
    'termination_date' :        '2020-01-01',
    'phpsettingid' :            '1',
    'mod_fcgid_starter' :       '-1',
    'mod_fcgid_maxrequests' :   '-1',
    'ismainbutsubto' :          '0',
    'letsencrypt' :             '0',
    'hsts' :                    '0',
    'hsts_sub' :                '0',
    'hsts_preload' :            '0',
}
MAILUSER_DEFAULT = {
    'id' :                   '1',
    'email' :                'robert@redcor.net',
    'username' :             'robert@redcor.net',
    'password' :             '',
    'password_enc' :         '$1$2U4YTYXCwwWwN$UDwrVSIk.vk20/vaBXftr.',
    'uid' :                  '2000',
    'gid' :                  '2000',
    'homedir' :              '/var/syscp/mails/',
    'maildir' :              'redcor/robert@redcor.net/',
    'postfix' :              'Y',
    'domainid' :             '2',
    'customerid' :           '1',
    'quota' :                '100',
    'pop3' :                 '1',
    'imap' :                 '1',
    'mboxsize' :             '0',
}
"""
if ($userinfo['emails_used'] < $userinfo['emails'] || $userinfo['emails'] == '-1') {
    if (isset($_POST['send']) && $_POST['send'] == 'send') {
        $email_part = $_POST['email_part'];
        // domain does not need idna encoding as the value of the select-box is already Punycode
        $domain = validate($_POST['domain'], 'domain');
        $stmt = Database::prepare("SELECT `id`, `domain`, `customerid` FROM `" . TABLE_PANEL_DOMAINS . "`
                                  WHERE `domain`= :domain
                                  AND `customerid`= :customerid
                                  AND `isemaildomain`='1' "
                                  );
        $domain_check = Database::pexecute_first($stmt, array("domain" => $domain, "customerid" => $userinfo['customerid']));

        if (isset($_POST['iscatchall']) && $_POST['iscatchall'] == '1') {
            $iscatchall = '1';
            $email = '@' . $domain;
            } else {
                $iscatchall = '0';
                $email = $email_part . '@' . $domain;
            }

        $email_full = $email_part . '@' . $domain;

        if (!validateEmail($email_full)) {
            standard_error('emailiswrong', $email_full);
        }

        $stmt = Database::prepare("SELECT `id`, `email`, `email_full`, `iscatchall`, `destination`, `customerid` FROM `" . TABLE_MAIL_VIRTUAL . "`
                                  WHERE (`email` = :email
                                         OR `email_full` = :emailfull )
                                  AND `customerid`= :cid"
                                  );
        $params = array(
            "email" => $email,
            "emailfull" => $email_full,
            "cid" => $userinfo['customerid']
            );
        $email_check = Database::pexecute_first($stmt, $params);

        if ($email == '' || $email_full == '' || $email_part == '') {
            standard_error(array('stringisempty', 'emailadd'));
            } elseif ($domain == '') {
                standard_error('domaincantbeempty');
                } elseif ($domain_check['domain'] != $domain) {
                    standard_error('maindomainnonexist', $domain);
                    } elseif (strtolower($email_check['email_full']) == strtolower($email_full)) {
                        standard_error('emailexistalready', $email_full);
                        } elseif ($email_check['email'] == $email) {
                            standard_error('youhavealreadyacatchallforthisdomain');
                            } else {
                                $stmt = Database::prepare("INSERT INTO `" . TABLE_MAIL_VIRTUAL . "`
                                                          (`customerid`, `email`, `email_full`, `iscatchall`, `domainid`)
                                                          VALUES (:cid, :email, :email_full, :iscatchall, :domainid)"
                                                          );
                                $params = array(
                                    "cid" => $userinfo['customerid'],
                                    "email" => $email,
                                    "email_full" => $email_full,
                                    "iscatchall" => $iscatchall,
                                    "domainid" => $domain_check['id']
                                    );
                                Database::pexecute($stmt, $params);

                                $address_id = Database::lastInsertId();
                                $stmt = Database::prepare("UPDATE " . TABLE_PANEL_CUSTOMERS . "
                                                          SET `emails_used` = `emails_used` + 1
                                                          WHERE `customerid`= :cid"
                                                          );
                                Database::pexecute($stmt, array("cid" => $userinfo['customerid']));

                                $log->logAction(USR_ACTION, LOG_INFO, "added email address '" . $email_full . "'");
                                redirectTo($filename, array('page' => $page, 'action' => 'edit', 'id' => $address_id, 's' => $s));
                            }
        } else {
            $result_stmt = Database::prepare("SELECT `id`, `domain`, `customerid` FROM `" . TABLE_PANEL_DOMAINS . "`
                                             WHERE `customerid`= :cid
                                             AND `isemaildomain`='1'
                                             ORDER BY `domain` ASC"
                                             );
            Database::pexecute($result_stmt, array("cid" => $userinfo['customerid']));
            $domains = '';

    while ($row = $result_stmt->fetch(PDO::FETCH_ASSOC)) {
        $domains.= makeoption($idna_convert->decode($row['domain']), $row['domain']);
    }

    //$iscatchall = makeyesno('iscatchall', '1', '0', '0');

    $email_add_data = include_once dirname(__FILE__).'/lib/formfields/customer/email/formfield.emails_add.php';

    if (Settings::Get('catchall.catchall_enabled') != '1') {
        unset($email_add_data['emails_add']['sections']['section_a']['fields']['iscatchall']);
    }

    $email_add_form = htmlform::genHTMLForm($email_add_data);

    $title = $email_add_data['emails_add']['title'];
    $image = $email_add_data['emails_add']['image'];

    eval("echo \"" . getTemplate("email/emails_add") . "\";");
    }
"""

class EmailValueError(ValueError):
    '''Raise when a specific subset of values in context of app is wrong'''
    def __init__(self, message, *args):
        self.message = message # without this you may get DeprecationWarning
        # allow users initialize misc. arguments as any other builtin Error
        super(MyAppValueError, self).__init__(message, foo, *args) 

class MailHandler(InitHandler):
    tables    = {} # tables define in the froxlor database
    table_dic = {}
    
    def __init__(self, opts, sites=SITES):
        super(MailHandler, self).__init__(opts, sites)
        self.mysql_host = opts.mysql_host
        self.mysql_port = opts.mysql_port
        self.mysql_user = opts.mysql_user
        self.mysql_pw = opts.mysql_password
        self.mysql_db = opts.mysql_db
        
        # construct session
        connect_dic = {
            'host' : self.mysql_host,
            'port' : self.mysql_port,
            'user' : self.mysql_user,
            'passwd' : self.mysql_pw,
            'db' : self.mysql_db,
        }
        email_engine = create_engine("mysql://%(user)s:%(passwd)s@%(host)s:%(port)s/%(db)s" % connect_dic)
        self.Session = sessionmaker(bind=email_engine)

        Base = declarative_base()
        Base.metadata.reflect(email_engine)
        
        class CustomerFroxlor(Base):
            __tablename__ = "panel_customers"
        
        class DomainFroxlor(Base):
            __tablename__ = "panel_domains"
            
        class MailuserFroxlor(Base):
            __tablename__ = "mail_users"
            
        class MailvirtualFroxlor(Base):
            __tablename__ = "mail_virtual"
            
        self.CustomerFroxlor = CustomerFroxlor
        self.DomainFroxlor = DomainFroxlor
        self.MailuserFroxlor = MailuserFroxlor
        self.MailvirtualFroxlor = MailvirtualFroxlor

    def get_tables(self):
        if not self.tables:
            session = self.get_session()
            insp = inspect(session.connection())
            self.tables = insp.get_table_names()
        return self.tables
           
    def get_table(self, tbl_name):
        if tbl_name not in self.table_dic:
            if tbl_name not in self.get_tables():
                raise EmailValueError('table %s is not defined')
            meta = MetaData(self.get_session().connection().engine)
            self.table_dic[tbl_name] = Table(tbl_name, meta, autoload=True)
        return self.table_dic[tbl_name]

    def get_session(self):
        from sqlalchemy import inspect
        session = self.Session()
        return session
    
    def get_connection(self):
        return self.get_session().connection()

    @property
    def get_mail_data(self):
        return self.site.get('email')
    
    def get_customer_froxlor(self, name = '', customer_id = 0):
        """
        get a customer either by name or by id
        @name: name of the customer
        @customer_id: customerid of the customer
        """
        session = self.get_session()
        if name:            
            result = session.query(self.CustomerFroxlor).filter(
                self.CustomerFroxlor.loginname == name)
        elif customer_id:
            result = session.query(self.CustomerFroxlor).filter(
                self.CustomerFroxlor.customerid == customer_id)
        else:
            return
        customer = result and result.all()
        return customer and customer[0]

    def get_domain_froxlor(self, name, customer_id):
        """
        get a domain by name and customer id
        it looks as if froxlor allows the same domain to be handled 
        by more than one customer, so the name is not enough
        @name: name of the domain
        @customer_id: customerid of the customer that handles the domain       
        """
        df = self.DomainFroxlor
        session = self.get_session()
        result  = session.query(df).filter(and_(
            df.domain == name,
            df.customerid == customer_id)        
        )       
        domain = result and result.all()
        return domain and domain[0]

    def get_domain_froxlor_by_id(self, domain_id):
        df = self.DomainFroxlor
        session = self.get_session()
        result  = session.query(df).filter(df.domainid == domain_id)        
        domain = result and result.all()
        return domain and domain[0]

    def get_mail_virtual_for_domain_id(self, domain_id):
        mv = self.MailvirtualFroxlor
        session = self.get_session()
        result  = session.query(mv).filter(mv.domainid == domain_id)        
        return result and result.all()

    def create_domain_froxlor(self, name, customer_id):
        #http://zetcode.com/db/mysqlpython/
        domain_id = self.get_domain_froxlor(name, customer_id)
        if domain_id:
            return domain_id
        session = self.get_session()
        customer = self.get_customer_froxlor(customer_id = customer_id)
        df = self.DomainFroxlor
        values = {}
        values['domain'] =                  name,
        values['adminid'] =                 customer.adminid
        values['customerid'] =              customer.customerid
        values['aliasdomain'] =             None
        values['documentroot'] =            customer.documentroot
        values['isbinddomain'] =            '1' # not clear what it is for
        values['isemaildomain'] =           '1' # neccessary, as default is 0 ??
        values['email_only'] =              '0' # not clear what it is for
        # dkim values should be handled
        # but at the moment are not
        #values['dkim'] =                    '1'
        #values['dkim_id'] =                 '0'
        #values['dkim_privkey'] =            ''
        #values['dkim_pubkey'] =             ''
        values['deactivated'] =             '0'
        values['add_date'] =                int(datetime.datetime.now().strftime('%Y%-m%-d')),
        values['registration_date'] =       '2000-01-01'
        values['termination_date'] =         '0000-00-00'
        session.add(df(**values))
        session.commit()
        return df
        
        
    def check_mail_user_froxlor(self, mail_user, server_data):
        # with froxlor mail is a unique constraint
        # the mail record has also a customer is
        # so there could be a situation, where the email exists but the customer id conflicts
        if mail_user.customerid != server_data.get('customer_id'):
            wrong_customer = get_customer_froxlor(customer_id = mail_user.customerid)
            raise EmailValueError('email %s allready exists, but is managed by customer %s' % 
                             (mail_user.email, wrong_customer.loginname))
        return True
        
    def get_mail_user(self, email, server_data = {}): 
        # email is unique
        mu = self.MailuserFroxlor
        session = self.get_session()
        # if for a mail_virtual catch all is set, the field mail has a value like '@DOMAIN' 
        # so we must check also for emaill full
        # example, with redirect to robert@redcor.ch
        # ------------------------------------------
        # id,   email,                   email_full,              destination,       domainid, customerid, popaccountid, iscatchall
        #'33', 'robert@erzaehlwolf.ch',  'robert@erzaehlwolf.ch', 'robert@redcor.ch','18',     '1',        '0',         '0'
        # same example, now with catchall set, the rest remains
        # -----------------------------------------------------
        # id,  email,                    email_full,               destination,      domainid, customerid, popaccountid, iscatchall
        #'33', '@erzaehlwolf.ch',        'robert@erzaehlwolf.ch', 'robert@redcor.ch','18',      '1',        '0',          '1'        
        result = session.query(self.mu).filter(or_(self.mu.email == email,self.mu.email_email == email))
        mail_user = result and result.all()
        mail_user = mail_user and mail_user[0]
        if mail_user and server_data and self.check_mail_user_froxlor(mail_user, server_data): 
            # actually check_mail_user dies if it is not fine
            return mail_user
        return mail_user or None
                 
    def update_mail_user(self, mail_user): 
        # email is unique
        mu = self.MailuserFroxlor
        session = self.get_session()

    def check_mail_virtual_froxlor(self, mail_virtual, server_data):
        # with froxlor mail is a unique constraint
        # the mail record has also a customer id
        # so there could be a situation, where the email exists but the customer id conflicts
        # catch all
        # ---------
        # we can define one email account per domain to be a catch all address
        # 
        if mail_virtual.customerid != server_data.get('customer_id'):
            wrong_customer = get_customer_froxlor(customer_id = mail_virtual.customerid)
            raise EmailValueError('email %s allready exists, but is managed by customer %s' % 
                             (mail_virtual.email, wrong_customer.loginname))
        return True
        
    def get_mail_virtual(self, email, server_data = {}): 
        # email is unique
        mv = self.MailvirtualFroxlor
        session = self.get_session()
        result = session.query(mv).filter(mv.email == email)
        mail_virtual = result and result.all()
        mail_virtual = mail_virtual and mail_virtual[0]
        if mail_virtual and server_data and self.check_mail_virtual_froxlor(mail_virtual, server_data): 
            # actually check_mail_virtual dies if it is not fine
            return mail_virtual
        return mail_virtual or None
    
    def update_mail_virtual(self, mail_virtual): 
        # email is unique
        mv = self.MailvirtualFroxlor
        session = self.get_session()
        
    
    def remove_catch_all(self, email='', mail_virtual = None):
        """
        Remove the catch all setting from an email account
        @email:    the email from which to remove the catch all setting
        """
        # first we get mail_virtual
        if not mail_virtual:
            mail_virtual = self.get_mail_virtual(email)
        if mail_virtual and mail_virtual.iscatchall:
            # we need to set both fields email and iscatchall
            # email is set to '@DOMAIN', when iscatchall is set
            mail_virtual.email = email
            mail_virtual.iscatchall = 0
            self.update_mail_virtual(mail_virtual)
            
    def set_catch_all(self, email, mail_virtual = None):
        """
        set the catch all setting form an email account
        @email:  the email for which to set the catch all setting
        """
        # first we get mail_virtual
        if not mail_virtual:
            mail_virtual = self.get_mail_virtual(email)
        if mail_virtual.iscatchall:
            # all set, nothing to do
            return
        # only on catchall is allowed per domain
        # so we run trough all mails for the domain and remove
        # a previous setting (if any)
        domain_id = mail_virtual.domainid
        for mv in self.get_mail_virtual_for_domain_id(domain_id):
            if mv.iscatchall:
                self.remove_catch_all(mail_virtual=mv)
        # now we can set the catch all flag
        # email is reduced to the domain, when the catch all flag is set.
        domain = self.get_domain_froxlor_by_id(domain_id)
        mail_virtual.email = domain.domain
        mail_virtual.iscatchall = 1
        self.update_mail_virtual(mail_virtual)
    
    def manage_mail_account(self, 
                            mailuser, 
                            user_data, 
                            server_data, 
                            cmd = 'check', 
                            reset_quota = False, 
                            reset_pw = False):
        """
        @mailuser : name of the account like 'mailhandler@afbs.ch'
                    This is NOT the email
        @userdata : a dictonary of the form:
                {
                    'email' : 'mailhandler@afbs.ch',
                    'user'  : 'mailhandler@afbs.ch', # username to log into the system
                    'pw'    : 'mailhandler@afbs.ch',
                    'quota' : 100,
                    'destination' : ''               # mail_user acount to use, any number of redirects
                                                       if is empty, tdoes not accept mail for the account                                                       
                    'catch_all' : True,              # if this is set, mail_virtual.email is of the form
                                                       @DOMAINNAME like @erzaehlwolf.ch
                },
        @server_data: a dictonary with information about the mail server settings
                      it is acnostic about the smtp server used (froxlor knows how to handle things)
                {
                    'type'    : 'froxlor',
                    'customer': 'redcor', # froxlor customer
                    'domain'  : 'afbs.ch',
                },
        @cmd      : operation to perform: 'add', 'delete', 'update', 'check'
        @reset_quota: if set, then reset quota to the value given in userdata, 
                    otherwise just make sure, at least the amount defined in user_data is provided

        """
        # manage a mail account
        # a mail account has three important elements
        # - an email address that consists from:
        #   a user name like john.doe
        #   a domain like jdoe.ch
        #   so the full email addres is john.doe@jdoe.ch
        # - a virtual mail account
        #   this controlls, whether froxlor (and postgres) accept the mail address
        #   It can act:
        #       - to redirect an incomming mail to other mail addresses
        #       - as catch all
        #         a catch all consumes all emails for which froxlor does not know an email address
        #         for catch all addresses froxlor only stores the @DOMAIN (where DOMAIN is something like redo2oo.ch)
        # - a mail user account 
        #   where the mails are stored
        #   a mail user account has a quota and a physical space somwhere, where the incomming emails are stored
        # some settings like
        # - redirerect
        # - catch all
        result = {
            'mail_virtual' : None,
            'mail_user' : None,
        }
        if cmd not in ['add', 'delete', 'update', 'check']:
            raise EmailValueError('%s is not a vallid manage_mail_account command' % cmd)
        if cmd == 'check':
            # if email is managed by an other froxlor customer an error is thrown
            try:
                email = user_data.get('email')
                if email:
                    virtual_user = None
                    mail_user = None
                    # when we get the virtual_user, we also check whether the email allready
                    # defined for an other customer. this  would raise an error
                    virtual_user = self.get_mail_virtual(email, server_data)
                    if virtual_user:
                        result['mail_virtual'] = virtual_user
                        # no mail user exists without mail_virtual (at least I think so ..)
                        mail_user = self.get_mail_user(email)
                        if mail_user:
                            result['mail_user'] = mail_user
            except EmailValueError as e:
                pass
            return result
        elif cmd == 'update':
            # get the actual settings, so we can decide, if any action is needed
            actual = self.manage_mail_account(mailuser, user_data, server_data, cmd = 'check')
            mail_virtual = actual['mail_virtual']
            mail_user    = actual['mail_user']
            # there are three things that need special handling when updating
            # password: this is only changed, when change pw is set
            # quota: quota is only set, when either the new quota is bigger than the old one
            #        or when reset_quota is set
            # catchall: catchall is only allowed to be set for one domain
            #        so can allways remove it, but when setting it, we have to check whether it 
            #        is set with an other mail account and remove it if neccessary.
                        
    def manage_mail(self):
        """
        manage_mail is used to set all emails declared in a site description 
            'mail_server' : {
                'type'    : 'froxlor',
                'customer': 'redcor',
                'domain'  : 'afbs.ch',
            },
        """
        connection = self.get_connection()
        mail_data = self.get_mail_data
        mail_server_data = mail_data.get('mail_server')
        mail_server_data['site_name'] = self.site_name
        customer = self.get_customer_froxlor(name = mail_server_data.get('customer'))
        if not customer:
            server_data['panel_customer_tbl'] = 'panel_customers'
            print(CUSTOMER_UNKNOWN % server_data)
        # next we need to get the customer_id from the know customer name
        domain = self.get_domain_froxlor(mail_server_data.get('domain'), customer.customerid)
        if not domain:
            domain = self.create_domain_froxlor(mail_server_data.get('domain'), customer.customerid)
        
        # second step is to create and check all the email needed
        server_data = {
            'customer_id' : customer.customerid, 
            'domain_id'   : domain.id,
        }
        missing_emails = {}
        bad_emails = {}
        existing_emails = {}
        missing_mail_virtual = {}
        bad_mail_virtual = {}
        existing_mail_virtual = {}
        for mailuser, user_data in list(mail_data.get('mail_user', {}).items()):
            result = self.manage_mail_account(mailuser, user_data, server_data, cmd='check')
            
                
        new_rec = {
            'catch_all' : catch_all,
        }
