import json
import requests

"""
request tutorial:
https://medium.com/@anthonypjshaw/python-requests-deep-dive-a0a5c5c1e093
"""


# url = 'http://localhost:8069/web/dataset/search_read'
# urlj= 'http://localhost:8069/web/redfrubaj'
# headers = {'Content-Type': 'application/json'}
# data = {
#     'jsonrpc' : '2.0',
#     'method' : 'call',
#     'params' : {
#         'context' : {},
#         'name' : 'hola',
#         'email' : 'emailing',
#     },
# }

# data_json = json.dumps(data)
# r = requests.post(url=urlj, data=data_json, headers=headers)
# c = r.text
# print c

# res=requests.get('http://localhost:8069/web/login', auth=('admin', 'admin')) 
# print res
headers = {'Content-Type': 'application/json'}
data_json = json.dumps(
    {
        'params' : { 
            'model' : 'calendar.attendee',
            'domain' : [['partner_id', '=', 3]],
            #'fields': 'partner_id.name',
        }
    }
)
url = 'http://localhost:8069/web/dataset/search_read?model=calendar.attendee&fields=name'
res=requests.get(url=url, data=data_json, headers=headers)
print(res)

a=1
