#!bin/python
# -*- encoding: utf-8 -*-
from collections import OrderedDict
# BASE_PRESET is used to construct a file with values
# used to construct a new site
# the preset file will be named _{SITENAME}_.pre
# and consist of lines:
# key: any value for key
# key2: any value for key2
#
# the naming of the key is:
# modelkey_valuename
# where the modelkey is looked up in MODELS_TO_USE
# and valuename is the name of the field of that model
#
# 
BASE_PRESET = OrderedDict()
# you can add any number of more fields
BASE_PRESET['titel_1'] = ('Company fields', 'In diesem Abschnitt werden die Firmendaten bereitgestellt')
# ----------------------------------------
BASE_PRESET['company_name'] = ('My Demo-Company', 'Der Name der Firma. Z.B; redO2oo KLG')
BASE_PRESET['company_image'] = ('skeleton/images/logo_klg_232.png', 'Der Pfad zu einer Bild-Datei mit dem Firmenlogo')
BASE_PRESET['company_favicon'] = ('skeleton/images/favicon.ico', 'Der Pfad zu einer Bild-Datei mit dem Favicon')
BASE_PRESET['company_street'] = ('Sickingerst 3', 'Die erste Adresszeile. Weitere Adressdaten können in der Site gesetzt werden')
BASE_PRESET['company_website'] = ('https://www.redo2oo.ch', 'Die URL zur Firmenwebsite')
BASE_PRESET['company_phone'] = ('+41 31 333 10 20', 'Die Firmen-Telephon Nummer')
BASE_PRESET['company_email'] = ('info@o2oo.ch', 'Die Firmen-Email-Addresse')
BASE_PRESET['company_vat'] = ('123 MWST-NR', 'Die Mehrwersteuer-Nummer')
BASE_PRESET['company_company_registry'] = ('789-Firmenregistrierung', 'Die ofizielle Firmenregistrierungs-Nummer')
BASE_PRESET['company_report_header'] = ('We are ERP specialists', 'Die Kopzeile, wie sie auf Ausdrucken erscheint')
BASE_PRESET['company_report_footer'] = ('tel: 123... Bank: 3333', 'Die Fusszeile, wie sie auf Rechnungen Angeboten usw erscheint')

BASE_PRESET['titel_2'] = ('Outgoing Mail server', 'Hier werden Werte des zum Versenden von Mails genutzten Mailserves gesetzt')
# ----------------------------------------------
BASE_PRESET['outgoingmail_name'] = ('mail@redcor.ch', 'Der Name, unter welchem der Server gelistet wird')
BASE_PRESET['outgoingmail_type'] = ('IMAP Server', 'Der Typ des Servers. Es git POP, IMAP und Localhost.')
BASE_PRESET['outgoingmail_server'] = ('mail.redcor.ch', 'Der Servername in der form xx.yyyyy.zz')
BASE_PRESET['outgoingmail_port'] = ('143', 'Der Port an dem der Server läuft. Er ändert sich je nach Typ und Sicherheitseinstellung')
BASE_PRESET['outgoingmail_is_ssl'] = (1, 'Ist die Anmeldung verschlüsselt?')
BASE_PRESET['outgoingmail_user'] = ('mailhandler@o2oo.ch', 'Anmeldenamen beim Mailserver')
BASE_PRESET['outgoingmail_password'] = ('XXXX', 'Passwort des Mail-Nutzers')

BASE_PRESET['titel_3'] = ('Incomming Mail server', 'Hier werden Werte des zum Empfangen von Mails genutzten Mailserves gesetzt')
# -----------------------------------------------
BASE_PRESET['incomingmail_name'] = ('mail@redcor.ch', '')
BASE_PRESET['incomingmail_smtp_host'] = ('mail.redcor.ch', 'Der Servername in der form xx.yyyyy.zz')
BASE_PRESET['incomingmail_smtp_encryption'] = ('ssl', 'Ist die Anmeldung verschlüsselt?')
BASE_PRESET['incomingmail_port'] = ('465', 'Der Port an dem der Server läuft. Er ändert sich je nach Sicherheitseinstellung')
BASE_PRESET['incomingmail_is_ssl'] = (1, 'Ist die Anmeldung verschlüsselt?')
BASE_PRESET['incomingmail_smtp_user'] = ('mailhandler@o2oo.ch', 'Anmeldenamen beim Mailserver')
BASE_PRESET['incomingmail_smtp_pass'] = ('XXXX', 'Passwort des Mail-Nutzersr')

BASE_PRESET['titel_4'] = ('Bank Data', 'Hier werden Daten zur Bank der ersten zwei von der Firma genutzten Banken erfasst')
# -----------------------------------
BASE_PRESET['bank_name:1'] = ('Bank1' 'Wähle die Bank aus der liste der Banke. Diese ist auf banks.redo2oo.ch zu finden')
BASE_PRESET['bank_name:2'] = ('Bank2' 'Wähle die Bank aus der liste der Banke. Diese ist auf banks.redo2oo.ch zu finden')

BASE_PRESET['titel_4'] = ('Bank Account 1', 'Angaben zum Konto bei der Bank1')
# ----------------------------------------
BASE_PRESET['bankaccount_bank_id:1'] = ('$bank_name:1','Wähle eine der oben definierten Banken. Die erste hat ID 1')
BASE_PRESET['bankaccount_bank_name:1'] = ('Valiant Bank Breitenrain','Unter diesem Namen erscheint die Bank im Odoo-Backend')
BASE_PRESET['bankaccount_acc_number:1'] = ('CH36 0000 0000 0000 0000 0','IBAN Konto-Nummer')

BASE_PRESET['titel_5'] = ('Bank Account 2', 'Angaben zum Konto bei der Bank2')
# ----------------------------------------
BASE_PRESET['bankaccount_bank_id:2'] = ('$bank_name:2','Wähle eine der oben definierten Banken. Die zweite hat ID 2')
BASE_PRESET['bankaccount_bank_name:2'] = ('Postfinance','Unter diesem Namen erscheint die Bank im Odoo-Backend')
BASE_PRESET['bankaccount_acc_number:2'] = ('CH26 0000 0000 0000 0000 0','IBAN Konto-Nummer')

BASE_PRESET['titel_6'] = ('Website', 'Angaben zur Firmenwebsite')
# ----------------------------------------
BASE_PRESET['website_website_name'] = ('Wir sind ERP Spezialisten','Wähle eine stimmigen Titel der Website')


# MODELS_TO_USE
MODELS_TO_USE = {
    'company' : 'res.company',
    'outgoingmail' : 'ir.mail_server',
    'incomingmail' : 'fetchmail.server',
    'bank' : 'res.bank',
    'bankaccount' : 'res.partner.bank',
    'website' : 'website.config.settings',
}
