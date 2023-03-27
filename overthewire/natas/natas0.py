#!/bin/python3
import urllib3
http = urllib3.PoolManager()
username = "natas0"
password = "natas0"
from base64 import b64encode





#Authorization token: we need to base 64 encode it 

#and then decode it to acsii as python 3 stores it as a byte string

def basic_auth(username, password):

    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    
    return f'Basic {token}'
page = http.request('POST', 'http://natas0.natas.labs.overthewire.org', headers = { 'Authorization' : basic_auth(username, password) })
print(page.data);
