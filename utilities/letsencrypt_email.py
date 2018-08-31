SERVERS = [
    'afbs.ch',
    #'agenda2go.ch',
    #'alice2.ch',
    #'altgewohnt.ch',
    'brun-del-re.ch',
    'cell-n-light.ch',
    #'docmarolf.ch',
    'dramueller.ch',
    'eplusp.ch',
    #'erpdemo.redcor.ch',
    'erzaehlwolf.ch',
    'go2breitsch.ch',
    'gitlab.redcor.ch',
    #'indernet.ch',
    #'key2go.ch',
    #'letape-saxon.ch',
    #'o2oo.ch',
    #'oelinker.ch',
    'redclean.ch',
    'redclean.net',
    'redcor.ch',
    #'redcor.net',
    'redo2oo.ch',
    #'rh6670.ch',
    #'susik.ch',
    #'thoenssen.ch',
    #'tibhub.com',
    'um-electricite.ch',
]

APACHE = """
# Ensure that Apache listens on port 80
Listen 80
"""
VHOST = """
<VirtualHost *:80>
    DocumentRoot "/var/www/html"
    ServerName %s

    # Other directives here
</VirtualHost>
"""
import os
import socket
result = ''
ipDic = {}
from pprint import pprint
apache = APACHE

for s in SERVERS:
    for h in ['mail', 'smtp', 'pop', 'imap']:
        hostname = "%s.%s" % (h, s) #example
        response = os.system("ping -c 1 " + hostname)
        
        #and then check the response...
        if response == 0:
            print(hostname, 'is up!')
            ip = socket.gethostbyname(hostname)
            hname = socket.gethostbyaddr(ip)[0]
            print(hname)
            ipl = ipDic.get(hname, [])
            if not hostname in ipl:
                ipl.append(hostname)
                ipDic[hname] = ipl
            if ip in ['178.63.103.72', '178.63.103.120']:
                result += ' -d %s' % hostname
                apache += VHOST % hostname
        else:
            print(hostname, 'is down!')
        #if s == 'brun-del-re.ch':
            #print ip
            #import sys
            #sys.exit()
            #xx
            

print(result)
print(pprint(ipDic))
open('vhost.txt', 'w').write(apache)

# --test-cert --staging \
"""
certbot certonly --cert-name mail.redcor.ch --webroot -w /var/www/html/ --expand --agree-tos  \
-d mail.afbs.ch -d mail.brun-del-re.ch \
-d smtp.brun-del-re.ch -d pop.brun-del-re.ch -d imap.brun-del-re.ch -d mail.cell-n-light.ch \
-d smtp.cell-n-light.ch -d pop.cell-n-light.ch -d imap.cell-n-light.ch -d mail.dramueller.ch \
-d smtp.dramueller.ch -d pop.dramueller.ch -d imap.dramueller.ch -d mail.eplusp.ch -d pop.eplusp.ch \
-d imap.eplusp.ch -d mail.go2breitsch.ch -d smtp.go2breitsch.ch -d pop.go2breitsch.ch -d imap.go2breitsch.ch \
-d mail.redclean.ch -d mail.redclean.net -d mail.redcor.ch -d smtp.redcor.ch -d pop.redcor.ch \
-d imap.redcor.ch -d mail.redo2oo.ch -d smtp.redo2oo.ch -d pop.redo2oo.ch -d mail.um-electricite.ch

"""