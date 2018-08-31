import requests
import json

url = 'https://api.swisscom.com/messaging/sms'
CLIENT_ID = 'nel1taQrLkwRBsnXu19ld2suKOB0fqTa'

data = {
    "to": "+919895643264",  # "+918606827707",
    "text": "The wheather is fine but the sky is cloudy"
}

headers = {
    'content-type': 'application/json',
    'Accept-Charset': 'UTF-8',
    'SCS-Version': '2',
    'client_id': 'nel1taQrLkwRBsnXu19ld2suKOB0fqTa'
}

r = requests.post(url, data=json.dumps(data), headers=headers)
print("result--", r)
