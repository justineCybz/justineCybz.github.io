#!/bin/python3
import requests

username = "natas4"
password = "tKOcJIbzM4lTs8hbCmzn5Zr4434fGZQm"
headers = { 'Referer': 'http://natas5.natas.labs.overthewire.org/'}
r = requests.get('http://natas4.natas.labs.overthewire.org', auth=(username, password), headers=headers)
print(r.headers)
print(r.text)
