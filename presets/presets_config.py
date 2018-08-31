import os
from collections import OrderedDict
BASE_PATH = os.path.split(os.path.abspath(__file__))[0]

APP_SEQUENCE = OrderedDict()
a = APP_SEQUENCE
# the values of the following entries are irelevant, they will be repplaced
# it is only the sequence of the following lines that is relevant
# each handler belongs to an app group and hase a sequence assigned
# to it, that defines what position it has within that group
# this sequence needs not be unique but if not, the real sequence is 
# not well defined
# the APP_SEQUENCE defines in what sequence the app groups are presented 
# to the user
a['company'] = 1
a['mailhandler'] = 1
a['bank'] = 1

# assign sequence numbers
counter = 0
for k in APP_SEQUENCE.keys():
    counter += 1 # should never be 0
    a[k] = counter * 10

BASE_PRESETS = [
    ('company', 'res.company'),
    ('outgoingmail', 'ir.mail_server'),
    ('incomingmail', 'fetchmail.server'),
    ('bank', 'res.bank')
]