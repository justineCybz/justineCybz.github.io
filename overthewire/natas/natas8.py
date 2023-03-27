#!/bin/python3
import requests
import base64
import binascii
from bs4 import BeautifulSoup


username = "natas8"
password = "a6bZCNYwdKqN5cGP11ZdtPg0iImQQhAB"

r = requests.post('http://natas8.natas.labs.overthewire.org/index-source.html', auth=(username, password))
print(r.headers)
soup = BeautifulSoup(r.text, 'html.parser')
encoded = soup.find("span", style="color: #DD0000").string.strip('"')
print(encoded)
encoded = binascii.unhexlify(encoded)
print(encoded)
encoded = encoded[::-1]
print(encoded)
encoded = base64.standard_b64decode(encoded)
print(encoded)
p = requests.post('http://natas8.natas.labs.overthewire.org/', data={"secret":encoded, "submit":"submit"}, auth=(username, password))
print(p.text)
